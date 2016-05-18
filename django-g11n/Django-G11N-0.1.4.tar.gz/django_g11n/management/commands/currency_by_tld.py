"""
Command Currency by TLD.
"""

from django.core.management.base import BaseCommand
from ...tools import fetch
# pylint: disable=no-member

_ARGUMENT_TLD = 'Country Code Top Level Domain'
class Command(BaseCommand):
    """Return the currency by given top level domain."""
    help = "Return the currency by given top level domain."

    def add_arguments(self, parser):
        parser.add_argument(_ARGUMENT_TLD)

    # pylint: disable=unused-argument
    def handle(self, *args, **kwargs):
        tld = kwargs[_ARGUMENT_TLD]
        fetched = fetch.currency_by_country_tld(tld)
        if all(item is None for item in fetched):
            return None

        fetched = [str(item) for item in fetched]
        return ':'.join(fetched)
