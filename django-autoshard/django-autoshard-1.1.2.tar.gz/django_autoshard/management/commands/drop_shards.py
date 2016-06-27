from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Build drop shards queries and print them. Will never actually run the queries. Useful in development.'

    def handle(self, *args, **opts):
        for _, shard in settings.SHARDS.items():
            self.stdout.write('DROP DATABASE %s;' % shard.database)
