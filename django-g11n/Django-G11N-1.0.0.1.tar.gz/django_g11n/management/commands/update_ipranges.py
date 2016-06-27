"""
Command update IP Ranges.
"""

from django.core.management.base import BaseCommand
from ...tools import models
from django_g11n.tools import ipranges
# pylint: disable=no-member

def fetch_and_insert():
    "Fetch the data from the regional NIC."
    model = models.ALL['IPRange']
    index_old = set(model.objects.all().values_list('identifier',
                                                    flat=True))

    data = list(ipranges.get())
    index_new = set([row[0] for row in data])

    db_remove = index_old.difference(index_new)
    model.objects.filter(identifier__in=db_remove).delete()
    print('# %s entries removed from DB' % len(db_remove))

    db_insert = index_new.difference(index_old)

    lookup = dict(\
                models.ALL['Country'].objects.all().values_list('code_2', 'id'))

    tmp = list()
    not_found = set()
    for entry in data:
        if entry[0] in db_insert:
            instance = model()
            instance.identifier = entry[0]
            instance.regional_nic = entry[1]
            instance.tld = entry[2]
            if entry[2] in lookup:
                instance.reference_id = lookup[entry[2]]
            else:
                not_found.add(entry[2])

            instance.ipv = entry[3]
            instance.network_hex = entry[4]
            instance.broadcast_hex = entry[5]
            tmp.append(instance)

    if len(not_found) > 0:
        print("! Couldn't find country/region entries for: %s" % not_found)
    print("# Bulk insert %s items into the DB ..." % len(db_insert))
    model.objects.bulk_create(tmp)
    print('# Bulk insert done.')


def update():
    "Standard function to update data."
    fetch_and_insert()


class Command(BaseCommand):
    """Update IP Ranges"""
    help = "Use ipranges module to update the IP Ranges from the regional NIC."

    # pylint: disable=unused-argument
    def handle(self, *args, **kwargs):
        update()
