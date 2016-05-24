DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.sqlite',
    }
}

SECRET_KEY = '1'

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "tests",
    "dps",
]

ROOT_URLCONF = "tests.urls"

from .dps_settings import *
