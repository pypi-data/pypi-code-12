
import atexit
import os
import subprocess
import time
import threading

from django.apps import AppConfig
from django.conf import settings


# time in seconds to check for the worker
WORKER_MONITOR_INTERVALL = 5


class ExitHandler:

    def __init__(self, process):
        self.process = process

    def __call__(self):
        self.process.terminate()
        self.delete_periodic_tasks()

    def delete_periodic_tasks(self):
        """
        Tasks are persistent in the db. Periodic tasks are read in at
        process start and will not expire. So they should get deleted
        here.
        """
        from .models import TaskQueue  # noqa
        qs = TaskQueue.objects.filter(is_periodic=True)
        if qs.count():
            qs.delete()


class Supervisor:
    """
    Supervisor for the worker process.
    Starts and monitors the worker.
    """
    def __init__(self):
        self.exit_handler = None

    def __call__(self):
        process = self.start_worker()
        self.set_exit_handler(process)
        self.monitor_worker(process)

    def monitor_worker(self, process):
        while True:
            return_code = process.poll()
            if return_code:
                # bad things happend
                process = self.restart_process()
            else:
                time.sleep(WORKER_MONITOR_INTERVALL)

    def restart_process(self):
        atexit.unregister(self.exit_handler)
        process = self.start_worker()
        self.set_exit_handler(process)
        return process

    def set_exit_handler(self, process):
        self.exit_handler = ExitHandler(process)
        atexit.register(self.exit_handler)

    def start_worker(self):
        os.environ.setdefault('DJANGO_AUTOTASK', 'true')
        process = subprocess.Popen(
            ['python', 'manage.py', 'run_autotask'],
            env=os.environ,
            cwd=settings.BASE_DIR)
        return process


class AutotaskConfig(AppConfig):
    name = 'autotask'
    is_called = False

    def ready(self):
        if self.is_called:
            return
        self.is_called = True
        if not os.environ.get('DJANGO_AUTOTASK'):
            self.start_supervisor()

    def start_supervisor(self):
        """
        Start supervisor as daemon thread so the supervisor-thread will
        not block on shut-down.
        """
        supervisor = Supervisor()
        thread = threading.Thread(target=supervisor, daemon=True)
        thread.start()
