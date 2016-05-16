"""Settings module.

Attributes:
    LOGGER_CONFIG (dict): Logging configuration settings. Includes formatters, handlers, loggers
"""
LOGGER_CONFIG = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'simple',
            'filename': 'goldfinchsong.log',
            'encoding': 'utf-8'
        }
    },
    'loggers': {
        'goldfinchsong': {
            'handlers': ['file', 'console'],
            'propagate': True,
            'level': 'INFO',
        },
    }
}