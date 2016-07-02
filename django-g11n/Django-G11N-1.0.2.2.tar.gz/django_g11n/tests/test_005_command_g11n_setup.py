"main testing module"
from django.test import TestCase

class MockUpdate(object):
    def __init__(self, module):
        self.restore = module

    def update(self):
        pass

# Create your tests here.
class UpdateLanguageCountriesTestCase(TestCase):
    "main test case"
    # pylint: disable=missing-docstring, no-member, invalid-name
    @classmethod
    def setUpClass(cls):
        returns = super(UpdateLanguageCountriesTestCase, cls).setUpClass()
        return returns

    def setUp(self):
        TestCase.setUp(self)
        from django.core.management import call_command
        self.call_command = call_command
        #
        from ..management.commands import g11n_setup
        self.g11n_setup = g11n_setup
        self.update_modules = ['update_countries', 'update_currencies',
                               'update_ipranges', 'update_languages',
                               'update_language_countries']
        for name in self.update_modules:
            module = getattr(g11n_setup, name)
            mock = MockUpdate(module)
            setattr(g11n_setup, name, mock)

    def tearDown(self):
        for name in self.update_modules:
            mock = getattr(self.g11n_setup, name)
            setattr(self.g11n_setup, name, mock.restore)

        TestCase.tearDown(self)

    def test_001_insert(self):
        self.call_command('g11n_setup')


if __name__ == '__main__': # pragma: no cover
    # pylint: disable=wrong-import-position
    import django
    django.setup()
    django.core.management.call_command('test')

