from itertools import chain
import time
import six

if six.PY3:
    from concurrent.futures import ThreadPoolExecutor
else:
    from collections import deque
    from threading import Thread

from django.conf import settings
from django.core.management.commands.migrate import Command as DjangoMigrateCommand
from django.db import OperationalError


class Command(DjangoMigrateCommand):
    def migrate(self, shard, *args, **options):
        try:
            start = time.time()
            options['database'] = shard.alias
            super(Command, self).handle(*args, **options)
            shard.connection.close()
            self.stdout.write(
                self.style.MIGRATE_HEADING('Migrated database %s in %.4f sec' % (shard.database, time.time() - start)))
        except OperationalError as e:
            self.stdout.write(
                    self.style.MIGRATE_HEADING('Failed migrating database: %s. Error: %s' % (options['database'], e)))

    def run(self, *args, **options):
        if six.PY3:
            executor = ThreadPoolExecutor(max_workers=10)
            for _, shard in settings.SHARDS.items():
                executor.submit(self.migrate, *chain((shard,), args), **options)
        else:
            queue = deque()
            for _, shard in settings.SHARDS.items():
                queue.append(Thread(target=self.migrate, args=chain((shard,), args), kwargs=options))
            workers = 0
            while queue:
                if workers < 10:
                    t = queue.popleft()
                    t.start()

    def handle(self, *args, **options):
        options['verbosity'] = 0
        try:
            self.run(*args, **options)
            self.stdout.write(self.style.MIGRATE_HEADING('Done.\n'))
        except KeyboardInterrupt:
            self.stdout.write(self.style.MIGRATE_HEADING('Migration interrupted.\n'))
