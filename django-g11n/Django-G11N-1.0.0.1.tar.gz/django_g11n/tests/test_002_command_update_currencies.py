"main testing module"
from django.test import TestCase

# Create your tests here.
class UpdateCurrenciesTestCase(TestCase):
    "main test case"
    # pylint: disable=missing-docstring, no-member, invalid-name
    @classmethod
    def setUpClass(cls):
        returns = super(UpdateCurrenciesTestCase, cls).setUpClass()
        return returns

    def setUp(self):
        returns = TestCase.setUp(self)
        from . import common
        common.setup_currencies()
        return returns

    def test_001_insert(self):
        from django.core.management import call_command
        call_command('update_currencies')
        # Calling twice, as the second time it should exclude it.
        call_command('update_currencies')



if __name__ == '__main__': # pragma: no cover
    # pylint: disable=wrong-import-position
    import django
    django.setup()
    django.core.management.call_command('test')

