from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import ProgrammingError


class Command(BaseCommand):
    help = 'Create shards databases'

    def handle(self, *args, **opts):
        for _, shard in settings.SHARDS.items():
            cursor = shard.connection._nodb_connection.cursor()
            try:
                cursor.execute('CREATE DATABASE %s' % shard.database)
                self.stdout.write(self.style.MIGRATE_HEADING(
                    'Database [%s] created.' % shard.database
                ))
            except ProgrammingError as e:
                self.stderr.write(str(e))
        self.stdout.write(self.style.MIGRATE_HEADING('Done.\n'))
