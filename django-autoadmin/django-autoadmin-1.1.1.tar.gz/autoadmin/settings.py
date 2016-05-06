from __future__ import unicode_literals

from django.conf import settings

EMAIL = lambda: getattr(settings, 'AUTOADMIN_EMAIL', 'autoadmin@example.com')
PASSWORD = lambda: getattr(settings, 'AUTOADMIN_PASSWORD', None)
USERNAME = lambda: getattr(settings, 'AUTOADMIN_USERNAME', 'admin')
