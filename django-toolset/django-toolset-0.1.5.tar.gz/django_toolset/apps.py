# coding=utf-8
try:
    from django.apps import AppConfig

    class DjangoHelpersConfig(AppConfig):
        name = 'django_toolset'

except ImportError:
    pass
