from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'A build system (for less, coffeescript, ...).'

    def add_arguments(self, parser):
        parser.add_argument('-w', '--watch', dest='watch',
                            required=False, action='store_true',
                            help='Starts a blocking process that watches for changes.')
        # parser.add_argument('init', dest='init',
        #                     required=False, action='store_true',
        #                     help='')

    def handle(self, *args, **options):
        settings.IEVVTASKS_BUILDSTATIC_APPS.configure_logging()
        settings.IEVVTASKS_BUILDSTATIC_APPS.install()
        settings.IEVVTASKS_BUILDSTATIC_APPS.run()
        if options['watch']:
            settings.IEVVTASKS_BUILDSTATIC_APPS.watch()
