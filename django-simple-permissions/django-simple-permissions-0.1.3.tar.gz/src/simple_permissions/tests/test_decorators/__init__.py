import django
if django.VERSION < (1, 6):
    # Django 1.5 and earlier use a different test method and the followings
    # are required to be exposed
    from simple_permissions.tests.test_decorators.test_functionbase import *
    from simple_permissions.tests.test_decorators.test_methodbase import *
    from simple_permissions.tests.test_decorators.test_classbase import *
    from simple_permissions.tests.test_decorators.test_permission_required import *
