import os

DEFAULT_SETTINGS_PATH = '/opt/ubackup/settings.py'

CHUNK_SIZE = 1024 * 1024 * 10

CURRENT_DIR = os.path.dirname(__file__)
VERSION = open(os.path.join(CURRENT_DIR, 'VERSION.txt')).read()

DROPBOX_APP_KEY = 'rqqumcq9htn0fcb'
DROPBOX_APP_SECRET = 'ag8dvti5kx2cfg9'

LOG_DIRECTORY = '/var/log/ubackup'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'standard': {
            'format': '[%(asctime)s][%(levelname)s] %(name)s %(filename)s:%(funcName)s:%(lineno)d | %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
        'requests': {
            'level': 'WARNING',
            'handlers': ['console'],
        }
    },
}
