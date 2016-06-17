import os
import sys

import django
from django.conf import settings
from django.core.management import call_command

def makemigrations():
    sys.path.insert(0, os.getcwd())
    settings.configure(DEBUG=True,
                       DATABASES={
                           'default': {
                               'ENGINE': 'django.db.backends.sqlite3',
                           }
                       },
                       SECRET_KEY='fake_key',
                       INSTALLED_APPS=[sys.argv[1]],
                      )

    django.setup()
    call_command('makemigrations', sys.argv[1], skip_checks=False)
