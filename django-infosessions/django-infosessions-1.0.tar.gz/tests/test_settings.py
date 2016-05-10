SECRET_KEY = 'fake-key'
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'tests',
    'infosessions',
]

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/5',
        'OPTIONS': {
            'PARSER_CLASS': 'redis.connection.HiredisParser'
        },
    },
}

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3'}}

DD_SESSION_USE_FALLBACK = False
DD_SESSION_PREFIX = 'test'
SESSION_ENGINE = 'infosessions.session'
