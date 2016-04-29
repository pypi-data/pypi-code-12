RF_HOST = '0.0.0.0'
RF_PORT = 8100

SIP_HOST = '0.0.0.0'
SIP_PORT = 5060


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/caller.log',
            'maxBytes': 10485760,
            'backupCount': 2,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'callerlib': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    }
}
