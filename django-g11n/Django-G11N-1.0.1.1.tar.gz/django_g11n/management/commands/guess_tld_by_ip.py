"""
Command Guess TLD by IP
"""

from django.core.management.base import BaseCommand
from ...tools import fetch
# pylint: disable=no-member

_ARGUMENT_ADDRESS = 'IP Address'
class Command(BaseCommand):
    """Guess the TLD by given IP."""
    help = "Guess the TLD by given IP."

    def add_arguments(self, parser):
        parser.add_argument(_ARGUMENT_ADDRESS)

    # pylint: disable=unused-argument
    def handle(self, *args, **kwargs):
        address = kwargs[_ARGUMENT_ADDRESS]
        fetched = fetch.country_by_ip(address)
        return fetched
