"""Command Initial Inserts"""

from django.core.management.base import BaseCommand
from . import (update_countries, update_currencies, update_ipranges,
               update_languages, update_language_countries)
# pylint: disable=no-member

class Command(BaseCommand):
    """Initial inserting of data."""
    help = "Insert data."

    # pylint: disable=unused-argument
    def handle(self, *args, **kwargs):
        update_countries.update()
        update_currencies.update()
        update_ipranges.update()
        update_languages.update()
        update_language_countries.update()
