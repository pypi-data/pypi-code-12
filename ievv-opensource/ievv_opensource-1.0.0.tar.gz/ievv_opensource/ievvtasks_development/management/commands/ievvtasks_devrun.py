from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run development servers configured for this project.'

    def add_arguments(self, parser):
        parser.add_argument('-n', '--name', dest='name',
                            required=False,
                            choices=settings.IEVVTASKS_DEVRUN_RUNNABLES.keys(),
                            default='default',
                            help='.')

    def handle(self, *args, **options):
        name = options['name']
        settings.IEVVTASKS_DEVRUN_RUNNABLES[name].start()
