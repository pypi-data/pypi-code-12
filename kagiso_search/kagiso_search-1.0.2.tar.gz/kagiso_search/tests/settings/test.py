import os

DEBUG = True

SECRET_KEY = '^7jcx7^h#b@%a76lr@a2!7xj#@4@5ayuyan9c$y#(_(8l3)_%t'

ROOT_URLCONF = 'kagiso_search.tests.urls'
ITEMS_PER_PAGE = 5

AUTH_API_TOKEN = 'xyz'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'wagtail.wagtailadmin',
    'wagtail.wagtailcore',
    'wagtail.wagtaildocs',
    'wagtail.wagtailembeds',
    'wagtail.wagtailforms',
    'wagtail.wagtailimages',
    'wagtail.wagtailredirects',
    'wagtail.wagtailsearch',
    'wagtail.wagtailsites',
    'wagtail.wagtailsnippets',
    'wagtail.wagtailusers',

    'modelcluster',
    'taggit',

    'kagiso_search',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'wagtail.wagtailcore.middleware.SiteMiddleware',
    'wagtail.wagtailredirects.middleware.RedirectMiddleware',
)


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'kagiso_search',
        'USER': os.getenv('USER'),
        'PASSWORD': 'password',
        'ATOMIC_REQUESTS': True,
    }
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
