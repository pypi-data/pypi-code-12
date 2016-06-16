from enhydris.settings.base import *

DEBUG = True
TEMPLATE_DEBUG = True
ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS
DATABASES =  {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'emy',
        'USER': 'emy',
        'PASSWORD': 'topsecret',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
TIME_ZONE = 'Europe/Athens'
SITE_ID = 1
MEDIA_ROOT = '/tmp'
MEDIA_URL = '/site_media/'
STATIC_ROOT = 'static/'
STATIC_URL = '/enhydris-static/'
# Make this unique, and don't share it with anybody.
SECRET_KEY = 'yy)g)w2jqkpyv9$w39i9$7(6wb+$h(_+x3gj#=@fzs2tmuj$#='
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
ENHYDRIS_USERS_CAN_ADD_CONTENT = True
ENHYDRIS_TSDATA_AVAILABLE_FOR_ANONYMOUS_USERS = True
ENHYDRIS_SITE_CONTENT_IS_FREE = True

ROOT_URLCONF = 'enhydris.urls'

from selenium import webdriver
SELENIUM_WEBDRIVERS = {
    'default': {
        'callable': webdriver.Firefox,
        'args': (),
        'kwargs': {},
    }
}
