"main testing module"
from django.test import TestCase

# Create your tests here.
class UpdateCountriesTestCase(TestCase):
    "main test case"
    # pylint: disable=missing-docstring, no-member, invalid-name
    @classmethod
    def setUpClass(cls):
        returns = super(UpdateCountriesTestCase, cls).setUpClass()
        return returns

    def setUp(self):
        TestCase.setUp(self)

    def test_001_insert(self):
        from django.core.management import call_command
        call_command('update_countries')

        from ..tools import models

        model = models.ALL['Country']
        query = model.objects.filter()
        query = query.values_list('code_2', flat=True).distinct()
        self.assertEqual(254, query.count())

        model = models.ALL['CountryName']
        query = model.objects.filter()
        query = query.values_list('value', flat=True).distinct()
        self.assertEqual(270, query.count())



if __name__ == '__main__': # pragma: no cover
    # pylint: disable=wrong-import-position
    import django
    django.setup()
    django.core.management.call_command('test')

