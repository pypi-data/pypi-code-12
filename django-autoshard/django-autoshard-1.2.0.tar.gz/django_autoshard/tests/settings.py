DEBUG = False
SECRET_KEY = '0mgs0s3cr37!10n3!!'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'autoshard',
    }
}
MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_autoshard',
    'django_autoshard.tests.fakeapp'
]
AUTH_USER_MODEL = 'fakeapp.User'
TEST_RUNNER = 'django_autoshard.tests.runner.TestRunner'
DJANGO_AUTOSHARD = {
    "NODES": [
        {
            "HOST": "",
            "RANGE": range(2)
        }
    ]
}
