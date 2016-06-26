from django.conf import settings
import os

REDIS_SETTING_NAME = getattr(settings, 'ASYNC_TASKS_REDIS_SETTING_NAME', 'default')
BASE_DIR = getattr(settings, 'BASE_DIR')
LOG_PATH = getattr(settings, 'ASYNC_TASKS_LOG_PATH', os.path.join(BASE_DIR, 'logs'))
LOG_FILENAME = getattr(settings, 'ASYNC_TASKS_LOG_FILENAME', 'async-tasks.log')