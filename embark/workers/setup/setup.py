import logging
import os

from subprocess import Popen, PIPE

import paramiko

from django.conf import settings

from workers.models import Worker

logger = logging.getLogger(__name__)


def setup_dependencies():
    """
    Sets up all dependencies required for offline workers
    """
    if not os.path.isdir(settings.WORKER_SETUP_PATH) or not os.path.exists(settings.WORKER_SETUP_ZIP_PATH):
        try:
            file = os.path.join(os.path.dirname(__file__), "host.sh")
            cmd = f"sudo {file} '{settings.WORKER_SETUP_PATH}' '{settings.WORKER_SETUP_ZIP_PATH}'"
            with open(f"{settings.WORKER_SETUP_LOGS}", "w+", encoding="utf-8") as file:
                with Popen(cmd, stdin=PIPE, stdout=file, stderr=file, shell=True) as proc:  # nosec
                    proc.communicate()

                logger.info("Worker depenendencies setup successful")
        except BaseException as exception:
            logger.error("Error setting up worker dependencies: %s", exception)


def exec_blocking_ssh(client, command):
    """
    Executes ssh command blocking, as exec_command is non-blocking

    Warning: This command might block forever, if the output is too large (based on recv_exit_status)

    :params client: paramiko ssh client
    :params command: command string
    """
    _, stdout, _ = client.exec_command(command)  # nosec B601: No user input

    status = stdout.channel.recv_exit_status()
    if status != 0:
        raise paramiko.SSHException(f"Command failed with status {status}: {command}")


def setup_worker(worker: Worker):
    """
    Transfers dependencies to offline worker and executes script

    :params worker: Worker instance
    """
    # TODO: Move to better place (e.g. if workers are enabled in config)
    setup_dependencies()

    logger.info("Setup started")

    worker.status = Worker.ConfigStatus.CONFIGURING
    worker.save()

    ssh_client = worker.ssh_connect()

    try:
        sftp_client = ssh_client.open_sftp()
        sftp_client.put(settings.WORKER_SETUP_ZIP_PATH, "/root/WORKER_SETUP.tar.gz")
        sftp_client.close()

        exec_blocking_ssh(ssh_client, 'tar xvzf /root/WORKER_SETUP.tar.gz >untar.log 2>&1')
        exec_blocking_ssh(ssh_client, 'sudo /root/WORKER_SETUP/installer.sh >installer.log 2>&1')

        worker.status = Worker.ConfigStatus.CONFIGURED
        logger.info("Setup done")
    except paramiko.SSHException as ssh_error:
        logger.error("SSH connection failed: %s", ssh_error)
        worker.status = Worker.ConfigStatus.ERROR
    finally:
        ssh_client.close()
        worker.save()
