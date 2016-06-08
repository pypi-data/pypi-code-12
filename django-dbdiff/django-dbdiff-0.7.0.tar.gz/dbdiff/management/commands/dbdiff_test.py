import imp
import os
import sys

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Discover and run dbdiff tests in the specified modules or the'
    'current directory.'

    def handle(self, *test_labels, **options):
        for app in settings.INSTALLED_APPS:
            path = imp.find_module(app)

            for root, dirs, files in os.walk(path):
                print root,dirs, files
