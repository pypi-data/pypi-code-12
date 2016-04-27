REDIS_URL = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 1
PROXY_MIDDLEWARE_URL = "http://localhost:5100"
TIME_ZONE = 'UTC'
RESUME = False
MAX_RETRY = 3
UNIQUE_CHECK = True
THREADS = 5

AUTOTHROTTLE = False
TIMEOUT = 5
MIN_DELAY = 0.5
MAX_DELAY = 60
REQUEST_PROCESSOR = 'dragline.http:RequestProcessor'

DEFAULT_REQUEST_ARGS = {
    'allow_redirects': True,
    'auth': None,
    'cert': None,
    'cookies': None,
    'data': None,
    'files': None,
    'headers': None,
    'json': None,
    'method': None,
    'params': None,
    'proxies': None,
    'stream': False,
    'timeout': None,
    'verify': False
}

SELENIUM_ARGS = {
    'proxy': None,
    'WINDOW_SIZE_WIDTH': 1024,
    'WINDOW_SIZE_HEIGHT': 768,
    'DISABLE_CSS': False,
    'DISABLE_IMAGE': False,
    'DISABLE_FLASH': False
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        }
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        },
        'dragline': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        }
    }
}
