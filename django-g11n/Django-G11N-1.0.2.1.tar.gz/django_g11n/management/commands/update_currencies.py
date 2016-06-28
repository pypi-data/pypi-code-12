"""
Command update currencies.
"""

from django.core.management.base import BaseCommand
from ...tools import models
from django_g11n.tools import currency
# pylint: disable=no-member

def format_search_key(key):
    "Currency names are unfortunately not all directly mappable."
    key = key.lower()
    key = key.replace('(the)', '')
    key = key.strip()
    return key

def insert_delete():
    "Delete old entries insert new"
    model = models.ALL['Currency']
    tmp = list()
    lookup = {key.strip().lower(): value for (key, value) in \
              models.ALL['CountryName'].objects.all()\
                                           .values_list('value', 'country__id')}

    existing = list(model.objects.all().values_list('numeric', flat=True))

    for entry in currency.get():
        if int(entry[1]) in existing:
            continue

        instance = model()
        instance.country = entry[0]
        search = format_search_key(entry[0])

        if search in lookup:
            instance.reference_id = lookup[search]
        else:
            instance.reference_id = lookup['unknown']

        instance.numeric = entry[1]
        instance.name = entry[2]
        instance.code = entry[3]
        if entry[4].isdigit():
            instance.decimals = entry[4]
        instance.is_fund = entry[5]
        instance.default = entry[6]
        instance.iso4217 = entry[7]
        tmp.append(instance)

    if len(tmp) > 0:
        model.objects.all().delete()
        model.objects.bulk_create(tmp)

    print('# %s entries inserted into DB' % len(tmp))

def update():
    "Standard function to update data."
    print('#' * 80)
    print('# Update Currencies')
    insert_delete()
    print('#' * 80)
    print('')

class Command(BaseCommand):
    """Update Currencies"""
    help = "Update all currencies."

    # pylint: disable=unused-argument
    def handle(self, *args, **kwargs):
        update()

