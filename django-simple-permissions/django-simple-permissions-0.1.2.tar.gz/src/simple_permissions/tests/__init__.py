import django
if django.VERSION < (1, 6):
    # Django 1.5 and earlier use a different test method and the followings
    # are required to be exposed
    from simple_permissions.tests.test_backends import *
    from simple_permissions.tests.test_handlers import *
    from simple_permissions.tests.test_utils import *
    from simple_permissions.tests.test_logics import *
    from simple_permissions.tests.test_decorators import *
    from simple_permissions.tests.test_templatetags import *
