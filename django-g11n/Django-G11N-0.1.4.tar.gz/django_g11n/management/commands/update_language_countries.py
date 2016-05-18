"""
Command update Language-Country.
"""

from django.core.management.base import BaseCommand
from ...tools import models
from django_g11n.tools import language_country
# pylint: disable=no-member
SPECIFIERS = dict(language_country.SPECIFIERS)

def update_specifiers():
    "Update Language Country Specifiers"
    model = models.ALL['LanguageCountrySpecifier']
    index_old = set(model.objects.filter(override=False)\
                                               .values_list('short', flat=True))

    data = list(language_country.get()['specifiers'])
    index_new = set([row[0] for row in data])

    db_obsolete = index_old.difference(index_new)
    if len(db_obsolete) > 0:
        model.objects.filter(short__in=db_obsolete).delete()
        print('# %s DB Language Country Specifiers deleted.' % len(db_obsolete))

    db_insert = index_new.difference(index_old)
    tmp = list()
    for entry in data:
        if entry[0] in db_insert:
            instance = model()
            instance.short = entry[0]
            instance.value = entry[1]
            instance.override = False
            tmp.append(instance)

    model.objects.bulk_create(tmp)
    text = '# %s DB Language Country Specifier entries inserted.'
    text = text % len(db_insert)
    print(text)


def lc_string(language, country, specifier):
    "Creates the string."
    tmp = '-'.join([language, country])
    if specifier != '':
        tmp += ' ('+SPECIFIERS[specifier]+')'

    return tmp

def lookups():
    "return lookups"
    tmp = dict()
    tmp['language3'] = dict()
    tmp['language2'] = dict()
    tmp['country'] = dict()
    tmp['specifiers'] = dict()

    for item in models.ALL['Language'].objects.all():
        tmp['language3'][item.bibliographic] = item
        tmp['language2'][item.code_a2] = item

    tmp['country'] = {item.code_2:item for item in \
                                            models.ALL['Country'].objects.all()}
    tmp['specifier'] = {item.short:item for item in \
                           models.ALL['LanguageCountrySpecifier'].objects.all()}
    return tmp

def _create_indexes(data):
    "creates the indexes for update_language_countries."
    index_lup = dict()
    index_old = set()

    for item in models.ALL['LanguageCountry'].objects.filter(override=False):
        string = str(item)
        index_old.add(string)
        index_lup[string] = item

    index_new = set()
    for language, country, specifier, _ in data:
        index_new.add(lc_string(language, country, specifier))

    return index_new, index_old, index_lup

def _find_and_remove_old(index_old, index_new, index_lup):
    "remove old countries"
    db_obsolete = index_old.difference(index_new)

    if len(db_obsolete) > 0:
        delete_ids = list()
        for key in db_obsolete:
            delete_ids.append(index_lup[key].id)
        models.ALL['LanguageCountry'].objects.filter(id__in=delete_ids).delete()
        print('# %s DB Language Countries deleted.' % len(db_obsolete))

def update_language_countries():
    "Update countries"
    data = list(language_country.get()['language_tld'])
    index_new, index_old, index_lup = _create_indexes(data)
    _find_and_remove_old(index_old, index_new, index_lup)

    db_insert = index_new.difference(index_old)
    tmp = list()
    lup = lookups()
    for language, country, specifier, default in data:
        string = lc_string(language, country, specifier)
        if string in db_insert:
            if len(language) > 2:
                language = lup['language3'][language]
            else:
                language = lup['language2'][language]

            country = lup['country'][country]
            if len(specifier) > 0:
                specifier = lup['specifier'][specifier]
            else:
                specifier = None

            instance = models.ALL['LanguageCountry']()
            instance.language_id = language.id
            instance.country_id = country.id
            instance.default = default
            instance.override = False
            if specifier is not None:
                instance.specifier_id = specifier.id

            tmp.append(instance)

    models.ALL['LanguageCountry'].objects.bulk_create(tmp)
    print('# %s DB Language entries inserted.' % len(tmp))

def update_country_names_local():
    "In the model CountryName update language to 'en-US' for empty ones"
    language = models.ALL['LanguageCountry'].objects.get(language__code_a2='en',
                                                         country__code_2='US')
    models.ALL['CountryName'].objects.filter(language__isnull=True)\
                                                      .update(language=language)

def update():
    "Standard function to update data."
    print('#' * 80)
    print('# Update Language Country')
    update_specifiers()
    update_language_countries()
    update_country_names_local()
    print('#' * 80)
    print('')


class Command(BaseCommand):
    """Update Languages"""
    help = "Update language/country combos."

    # pylint: disable=unused-argument
    def handle(self, *args, **kwargs):
        update()

