"""Command Initial Inserts"""

from django.core.management.base import BaseCommand
from . import (update_countries, update_currencies, update_ipranges,
               update_languages, update_language_countries)
# pylint: disable=no-member

class Command(BaseCommand):
    """Initial setup of the data."""
    help = "Insert initial data for setup purpose"

    # pylint: disable=unused-argument
    def handle(self, *args, **kwargs):
        # For first setup, we need to call the updates in a specific order.
        # Later updates can be done in any order.
        update_countries.update()
        update_currencies.update()
        update_ipranges.update()
        update_languages.update()
        update_language_countries.update()
