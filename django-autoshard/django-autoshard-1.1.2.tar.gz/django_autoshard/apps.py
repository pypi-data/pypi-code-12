from django.apps import AppConfig


class DjangoAutoShardApp(AppConfig):
    name = 'django_autoshard'
    verbose_name = 'Django Autoshard'

    def __init__(self, app_name, app_module):
        super(DjangoAutoShardApp, self).__init__(app_name, app_module)

    def ready(self):
        from .factory import ShardingFactory
        ShardingFactory().configure()
        super(DjangoAutoShardApp, self).ready()
