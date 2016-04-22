# -*- coding: utf-8 -*-
"""
    module.name
    ~~~~~~~~~~~~~~~
    Preamble...
"""
from __future__ import absolute_import, print_function, unicode_literals
import os

from os.path import normpath, join

DEBUG = True

os.environ.setdefault('DJANGO_LIVE_TEST_SERVER_ADDRESS', 'localhost:8000-9000')

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'ghostly.tests.django.testapp',
]

STATIC_URL = '/static/'

SECRET_KEY = 's3cr3t'

# Django replaces this, but it still wants it. *shrugs*
DATABASE_ENGINE = 'django.db.backends.sqlite3'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

MIDDLEWARE_CLASSES = {}

ROOT_URLCONF = 'ghostly.tests.django.testapp.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [
        os.path.join(os.path.dirname(__file__), 'templates')
    ],
    'OPTIONS': {
        'context_processors': [
            'django.contrib.auth.context_processors.auth',
            'django.core.context_processors.debug',
            'django.core.context_processors.i18n',
            'django.core.context_processors.media',
            'django.core.context_processors.static',
            'django.core.context_processors.tz',
            'django.core.context_processors.csrf',
            'django.contrib.messages.context_processors.messages',
            'django.core.context_processors.request',
        ]
    },
}]

# # STATIC FILE CONFIGURATION
# # See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
# STATIC_ROOT = normpath(join(SITE_ROOT, 'assets'))
#
# # See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
# STATIC_URL = '/static/'
#
# # See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
# STATICFILES_DIRS = (
#     normpath(join(SITE_ROOT, 'static')),
# )
#
# # See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
# STATICFILES_FINDERS = (
#     'django.contrib.staticfiles.finders.FileSystemFinder',
#     'django.contrib.staticfiles.finders.AppDirectoriesFinder',
# )
# # END STATIC FILE CONFIGURATION
