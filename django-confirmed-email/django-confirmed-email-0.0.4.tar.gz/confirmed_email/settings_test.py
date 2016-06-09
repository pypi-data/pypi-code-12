import os
SECRET_KEY = 'NOT_REALLY_IMPORTANT_FOR_TESTING',
DEBUG = True,

DATABASES = {
    'default': {
        'NAME': 'confirmed-email.sqlite3',
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

ROOT_URLCONF = 'confirmed_email.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'confirmed_email',
)
