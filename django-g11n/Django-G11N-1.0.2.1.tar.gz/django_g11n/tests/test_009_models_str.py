# Copyright (c) 2016, Martin P. Hellwig, All Rights Reserved.
"""
Test the commands
"""
# pylint:disable=R0904,C0111,W0212, import-error, too-few-public-methods
# pylint:disable=attribute-defined-outside-init, wrong-import-position
# pylint:disable=no-self-use
from django.test import TestCase

ORDER = ['Language', 'Country', 'LanguageCountrySpecifier', 'LanguageCountry',
         'CountryName', 'Currency', 'IPRange']
KWARG = {'Language':{'english':'Oi', 'french':'Ey'},
         'Country':{'numeric':999, 'code_2':'XX', 'code_3':'XXX'},
         'LanguageCountrySpecifier':{'short':'XX', 'value':'X all the way'},
         'LanguageCountry':{'language':'Language', 'country':'Country',},
         'CountryName':{'country':'Country', 'value':'X'},
         'Currency':{'country':'X', 'numeric':1, 'name':'X', 'code':'X'},
         'IPRange':{'identifier':'X', 'regional_nic':'X', 'tld':'XX',
                    'ipv':4, 'network_hex':'X', 'broadcast_hex':'X'},
         }

class TestModelsString(TestCase):
    def test_010_string(self):
        from ..tools import models
        tmp = dict()
        for key in ORDER:
            kwarg = KWARG[key]
            model = models.ALL[key]
            for kwarg_key in list(kwarg):
                kwarg_value = kwarg[kwarg_key]
                if kwarg_value in tmp:
                    kwarg[kwarg_key] = tmp[kwarg_value]

            tmp[key] = model.objects.create(**kwarg)
            str(tmp[key])

    def test_020_resave(self):
        from ..tools import models
        key = 'Language'
        model = models.ALL[key]
        subject = model.objects.create(**KWARG[key])
        subject.code_a2 = 'en'
        subject.save()

if __name__ == '__main__': # pragma: no cover
    import django
    django.setup()
    django.core.management.call_command('test')
