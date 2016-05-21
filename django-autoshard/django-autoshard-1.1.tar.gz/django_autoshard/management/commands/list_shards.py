from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'List all installed shards'

    def handle(self, *args, **opts):
        for _, shard in settings.SHARDS.items():
            info = 'ALIAS [{}] :: DATABASE NAME [{}] :: HOST :: [{}]'.format(
                shard.alias, shard.database, shard.host
            )
            self.stdout.write(self.style.MIGRATE_HEADING(info))
