"""Module configuration objects."""

from django.apps import AppConfig
from django.conf import settings

from . import utils


def _set(key, default):
    key = 'ABOUTCONFIG_%s' % key
    setattr(settings, key, getattr(settings, key, default))


class AboutconfigConfig(AppConfig):
    """Configuration provider for the module.

    Ensures configuration is loaded into cache on application start-up."""

    name = 'aboutconfig'


    @classmethod
    def ready(cls):
        _set('CACHE_NAME', 'default')
        _set('CACHE_TTL', None)

        # can't load data if models don't exist in the db yet
        if cls.migrations_applied():
            utils.preload_cache()


    @classmethod
    def migrations_applied(cls):
        """Check if module's migrations have been applied yet."""

        from django.db.migrations.loader import MigrationLoader
        from django.db import connection

        loader = MigrationLoader(connection, ignore_no_migrations=True)

        return (cls.name, '0002_initial_data') in loader.applied_migrations
