from functools import wraps

from prosodypy import lua

assert lua

import os
config = lua.require("core.configmanager")
settings_module = config.get("*", "django_settings_module")
os.environ['DJANGO_SETTINGS_MODULE'] = settings_module
import django
django.setup()

from django.db import connections

def db_connect(func, using='default'):
    @wraps(func)
    def inner(*args, **kwargs):
        connection = connections[using]
        connection.close_if_unusable_or_obsolete()
        connection.ensure_connection()
        return func(*args, **kwargs)
    return inner
