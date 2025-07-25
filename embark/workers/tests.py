# Create your tests here.
__copyright__ = 'Copyright 2021-2025 Siemens Energy AG, Copyright 2021-2025 The AMOS Projects'
__author__ = 'Benedikt Kuehne, ashiven'
__license__ = 'MIT'

import secrets
from django.test import TestCase

from workers.models import Worker, Configuration
from workers.orchestrator import Orchestrator, OrchestratorTask
from workers.tasks import config_worker_scan_task
from uploader.models import FirmwareAnalysis
from users.models import User


class TestOrchestrator(TestCase):
    def setUp(self):
        user = User.objects.create(username='test123')
        user.set_password('12345')
        user.api_key = secrets.token_urlsafe(32)
        user.save()
        test_config = Configuration.objects.create(user=user, name='test_config', ssh_user='test_user', ssh_password='test_password', ip_range='192.111.111.1/24')  # nosec
        self.test_worker1 = Worker.objects.create(name='test_worker1', ip_address='192.111.111.1', system_info={}, reachable=True)  # pylint: disable=W0201
        self.test_worker2 = Worker.objects.create(name='test_worker2', ip_address='192.111.111.2', system_info={}, reachable=True)  # pylint: disable=W0201
        self.test_worker1.configurations.add(test_config)
        self.test_worker2.configurations.add(test_config)
        self.orchestrator = Orchestrator()  # pylint: disable=W0201
        self.orchestrator.free_workers = {}
        self.orchestrator.busy_workers = {}

    def test_orchestrator_add_worker(self):
        """
        Test that a worker can be added to the orchestrator.
        """
        self.orchestrator.add_worker(self.test_worker1)
        self.assertIn(self.test_worker1.ip_address, self.orchestrator.get_free_workers())

    def test_orchestrator_remove_worker(self):
        """
        Test that a worker can be removed from the orchestrator.
        """
        self.orchestrator.add_worker(self.test_worker1)
        self.orchestrator.remove_worker(self.test_worker1)
        self.assertNotIn(self.test_worker1.ip_address, self.orchestrator.get_free_workers())
        self.assertNotIn(self.test_worker1.ip_address, self.orchestrator.get_busy_workers())

    def test_orchestrator_assign_worker(self):
        """
        Test that a worker can be assigned a task in the orchestrator.
        """
        task = OrchestratorTask(FirmwareAnalysis.objects.create().id, None, None, None)
        self.orchestrator.add_worker(self.test_worker1)
        self.orchestrator.assign_worker(self.test_worker1, task)
        self.assertIn(self.test_worker1.ip_address, self.orchestrator.get_busy_workers())
        self.assertEqual(self.orchestrator.get_busy_workers()[self.test_worker1.ip_address].analysis_id, task.firmware_analysis_id)

    def test_orchestrator_release_worker(self):
        """
        Test that a worker can be released from a task in the orchestrator.
        """
        task = OrchestratorTask(FirmwareAnalysis.objects.create().id, None, None, None)
        self.orchestrator.add_worker(self.test_worker1)
        self.orchestrator.assign_worker(self.test_worker1, task)
        self.orchestrator.release_worker(self.test_worker1)
        self.assertIn(self.test_worker1.ip_address, self.orchestrator.get_free_workers())
        self.assertNotIn(self.test_worker1.ip_address, self.orchestrator.get_busy_workers())

    def test_orchestrator_complex(self):
        """
        Test the orchestrator with a more complex sequence of operations.
        """
        task1 = OrchestratorTask(FirmwareAnalysis.objects.create().id, None, None, None)
        task2 = OrchestratorTask(FirmwareAnalysis.objects.create().id, None, None, None)
        self.orchestrator.add_worker(self.test_worker1)
        self.orchestrator.add_worker(self.test_worker2)
        self.orchestrator.assign_worker(self.test_worker1, task1)
        self.orchestrator.assign_worker(self.test_worker2, task2)
        self.orchestrator.release_worker(self.test_worker1)
        self.orchestrator.release_worker(self.test_worker2)
        self.orchestrator.assign_worker(self.test_worker2, task1)
        self.orchestrator.remove_worker(self.test_worker1)
        self.assertIn(self.test_worker2.ip_address, self.orchestrator.get_busy_workers())
        self.assertNotIn(self.test_worker1.ip_address, self.orchestrator.get_free_workers())
        self.orchestrator.release_worker(self.test_worker2)
        self.assertIn(self.test_worker2.ip_address, self.orchestrator.get_free_workers())

    def test_fifo_queue_task(self):
        """
        Test that tasks are assigned in FIFO order.
        """
        self.orchestrator.add_worker(self.test_worker1)
        self.orchestrator.add_worker(self.test_worker2)

        task1 = OrchestratorTask(FirmwareAnalysis.objects.create().id, None, None, None)
        task2 = OrchestratorTask(FirmwareAnalysis.objects.create().id, None, None, None)
        task3 = OrchestratorTask(FirmwareAnalysis.objects.create().id, None, None, None)

        self.orchestrator.queue_task(task1)
        self.orchestrator.queue_task(task2)
        self.orchestrator.queue_task(task3)

        self.assertEqual(self.orchestrator.get_busy_workers()[self.test_worker1.ip_address].analysis_id, task1.firmware_analysis_id)
        self.assertEqual(self.orchestrator.get_busy_workers()[self.test_worker2.ip_address].analysis_id, task2.firmware_analysis_id)
        self.assertEqual(self.orchestrator.tasks[0], task3)
        self.orchestrator.release_worker(self.test_worker1)
        self.orchestrator.release_worker(self.test_worker2)
        self.orchestrator.queue_task(task2)
        self.assertEqual(self.orchestrator.get_busy_workers()[self.test_worker1.ip_address].analysis_id, task3.firmware_analysis_id)

    def test_unreachable_host(self):
        """
        Test that unreachable hosts don't get added as workers.
        """
        unroutable_ip = '192.0.2.1'  # Unroutable IP (RFC 5737 TEST-NET-1)
        config = Configuration.objects.create(  # nosec
            user=User.objects.create(email="tom@example.com"),
            ssh_user='tom',
            ssh_password='tomisthebest',
            ip_range=f'{unroutable_ip}/32'
        )
        config_worker_scan_task(config.id)
        self.assertNotIn(unroutable_ip, self.orchestrator.free_workers)
