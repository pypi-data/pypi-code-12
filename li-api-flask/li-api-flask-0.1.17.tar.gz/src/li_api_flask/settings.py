# -*- coding: utf-8 -*-
import os
from li_common import helpers

ENVIRONMENT_FILE = '/etc/profile.d/env.sh'
helpers.carregar_env(ENVIRONMENT_FILE)

VERSAO = helpers.pegar_versao_git()

SECRET_KEY = os.environ.get('SECRET_KEY')

ENVIRONMENT = os.environ.get('ENVIRONMENT')

if os.environ.get('DEBUG') == 'False':
    DEBUG = False
else:
    DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "HOST": os.environ.get('DATABASE_HOST'),
        "NAME": os.environ.get('DATABASE_NAME'),
        "PASSWORD": os.environ.get('DATABASE_PASSWORD'),
        "PORT": os.environ.get('DATABASE_PORT'),
        "USER": os.environ.get('DATABASE_USER'),
        "CONN_MAX_AGE": 60,
        "TIME_ZONE": 'America/Sao_Paulo'
    }
}

REDIS = {
    'HOST': os.environ.get('REDIS_HOST'),
    'PORT': os.environ.get('REDIS_PORT'),
    'DB': os.environ.get('REDIS_DB')
}

SENTRY_DSN_API = os.environ.get('SENTRY_DSN_API')

ELASTICSEARCH_ASSISTANCE_URL = os.environ.get('ELASTICSEARCH_ASSISTANCE_URL')
ELASTICSEARCH_EVIDENCE_URL = os.environ.get('ELASTICSEARCH_EVIDENCE_URL')

TIME_ZONE = 'America/Sao_Paulo'

CELERY_TIMEZONE = 'America/Sao_Paulo'

LANGUAGE_CODE = 'pt-br'

MEDIA_URL = os.environ.get('MEDIA_URL')

TEMPLATE_DIRS = ('/opt/bucket.email.templates', )

LOG_LEVEL = 'DEBUG' if DEBUG else 'ERROR'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        }
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': LOG_LEVEL,
            'propagate': True
        },
        'django.request': {
            'handlers': ['default'],
            'level': LOG_LEVEL,
            'propagate': False
        },
        # 'django.db.backends': {
        #     'level': LOG_LEVEL,
        #     'handers': ['default'],
        # }
    }
}
