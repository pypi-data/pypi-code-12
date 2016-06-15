# coding: utf-8
import os

PACKAGES_PATH = '/home/damirazo/.venv/creadoc/local/lib/python2.7/site-packages/'
M3_EXT_ROOT = os.path.join(PACKAGES_PATH, 'm3_ext')
M3_ROOT = os.path.join(PACKAGES_PATH, 'm3')
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = 'yunz7!4sczxfx2mur-sec620px!l-(5_+0^o3j&#r!w6&11ubk'
DEBUG = True
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'south',
    'm3_mutex',
    'm3_users',
    'creadoc',

    'demo.app',
    'demo.app.designer',
    'demo.app.reports',
    'demo.app.example',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'demo.app.middlewares.FakeUserMiddleware',
    'demo.app.middlewares.PrettifyErrorMiddleware',
)

ROOT_URLCONF = 'demo.urls'
WSGI_APPLICATION = 'demo.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'

TEMPLATE_DIRS = (
    os.path.join('demo', 'app', 'templates'),
    os.path.join(M3_EXT_ROOT, 'templates'),
    os.path.join(M3_EXT_ROOT, 'ui', 'templates'),
)

STATICFILES_DIRS = (
    os.path.join(M3_EXT_ROOT, 'static'),
)

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/downloads/'


# Фрагмент url, по которому доступен контроллер модуля CreaDoc
CREADOC_URL = 'creadoc'
# Наименование директории в MEDIA_ROOT, в которую сохраняются шаблоны
CREADOC_REPORTS_DIR = 'reports'
# Путь до директории с шаблонами
CREADOC_REPORTS_ROOT = os.path.join(MEDIA_ROOT, CREADOC_REPORTS_DIR)
# URL, по которому доступны шаблоны
CREADOC_REPORTS_URL = MEDIA_URL + CREADOC_REPORTS_DIR + '/'
# Промежутки (в миллисекундах) между запусками процедуры автосохранения.
# Сохранение производится в локальный браузерный кэш (localStorage).
CREADOC_DESIGNER_LOCAL_AUTOSAVE_TIMEOUT = 6000
