"""
Command update languages.
"""

from django.core.management.base import BaseCommand
from ...tools import models
from django_g11n.tools import language
# pylint: disable=no-member

def update_languages():
    "Update countries"
    model = models.ALL['Language']
    index_old = set(model.objects.all().values_list('bibliographic', flat=True))

    data = list(language.get())
    index_new = set([row[0] for row in data])

    db_obsolete = index_old.difference(index_new)
    if len(db_obsolete) > 0:
        model.objects.filter(bibliographic__in=db_obsolete)\
                                                          .update(obsolete=True)
        print('# %s DB Language entries marked obsolete.' % len(db_obsolete))

    db_insert = index_new.difference(index_old)
    tmp = list()
    for entry in data:
        if entry[0] in db_insert:
            instance = model()
            instance.bibliographic = entry[0]
            instance.terminologic = entry[1]
            instance.code_a2 = entry[2]
            instance.english = entry[3]
            instance.french = entry[4]
            instance.iso639_2 = entry[5]
            tmp.append(instance)

    model.objects.bulk_create(tmp)
    print('# %s DB Language entries inserted.' % len(db_insert))


def update():
    "Standard function to update data."
    print('#' * 80)
    print('# Update Languages')
    update_languages()
    print('#' * 80)
    print('')

class Command(BaseCommand):
    """Update Languages"""
    help = "Update language data."

    # pylint: disable=unused-argument
    def handle(self, *args, **kwargs):
        update()

