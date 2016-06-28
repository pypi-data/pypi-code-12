"""
Command update country.
"""

from django.core.management.base import BaseCommand
from ...tools import models, country
# pylint: disable=no-member


def update_countries():
    "Update countries"
    model = models.ALL['Country']
    index_old = set(model.objects.all().values_list('numeric', flat=True))

    data = list(country.get())
    index_new = set([row[0] for row in data])

    db_obsolete = index_old.difference(index_new)
    model.objects.filter(numeric__in=db_obsolete).update(obsolete=True)
    print('# %s DB Country entries marked obsolete.' % len(db_obsolete))

    db_insert = index_new.difference(index_old)
    tmp = list()
    for entry in data:
        if entry[0] in db_insert:
            instance = model()
            instance.numeric = entry[0]
            instance.code_2 = entry[1]
            instance.code_3 = entry[2]
            instance.iso3166 = entry[3]
            tmp.append(instance)

    model.objects.bulk_create(tmp)
    print('# %s DB Country entries inserted.' % len(db_insert))

def update_country_names():
    "Update country names"
    tmp = list()
    lookup = dict()
    for item in models.ALL['Country'].objects.all():
        lookup[item.numeric] = item

    model = models.ALL['CountryName']
    index_old = set(model.objects.all().values_list('value', flat=True))

    data = list(country.get())
    for entry in data:
        default=True
        for name in entry[4:]:
            if name not in index_old:
                instance = model()
                instance.country = lookup[entry[0]]
                instance.default = default
                instance.value = name
                instance.iso3166 = entry[3]
                tmp.append(instance)
                if default:
                    default=False
    model.objects.bulk_create(tmp)
    print('# %s DB Country Name entries inserted.' % len(tmp))


def update():
    "Standard function to update data."
    print('#' * 80)
    print('# Update Countries')
    update_countries()
    update_country_names()
    print('#' * 80)
    print('')

class Command(BaseCommand):
    """Update Countries"""
    help = "Update Country data."

    # pylint: disable=unused-argument
    def handle(self, *args, **kwargs):
        update()

