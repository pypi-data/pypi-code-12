from django.core.management.base import BaseCommand
from optparse import make_option

from mcfeely.models import Email


class Command(BaseCommand):
  args = '<queue_name>'
  option_list = BaseCommand.option_list + (
    make_option('--retry',
                action='store_true',
                dest='retry',
                default=False,
                help='retry Deferred email'
                ),
  )
  help = 'send all mail in the specified queue'


def handle(self, *args, **options):
  emails = Email.objects.prefetch_related('recipient_set').all()
