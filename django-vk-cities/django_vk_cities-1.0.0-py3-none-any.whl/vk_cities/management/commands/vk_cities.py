# coding=utf-8

from django.conf import settings
from django.core.management.base import BaseCommand

from vk_cities import utils


class Command(BaseCommand):

    help = 'vk_cities management'
    commands = (
        'download',
    )

    def add_arguments(self, parser):
        parser.add_argument('command', type=str, choices=self.commands)

    def handle(self, *args, **options):
        getattr(self, options['command'])()

    def download(self):
        utils.download(
            getattr(settings, 'VK_CITIES_COUNTRIES', []),
            getattr(settings, 'LANGUAGE_CODE', 'en'),
        )
