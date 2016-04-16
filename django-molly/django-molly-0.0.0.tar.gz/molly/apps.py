from __future__ import unicode_literals

from .signals import application_started
from django.apps import AppConfig
from django.core.handlers import wsgi

from functools import wraps


def init(self, *args, **kwargs):
    super(wsgi.WSGIHandler, self).__init__(*args, **kwargs)
    application_started.send(sender=self.__class__, application=self)


class MollyConfig(AppConfig):
    name = 'molly'

    def ready(self):
        # monkey patch the WSGIHandler.__init__
        # so that the application started signal is sent
        wsgi.WSGIHandler.__init__ = wraps(wsgi.WSGIHandler.__init__)(init)
