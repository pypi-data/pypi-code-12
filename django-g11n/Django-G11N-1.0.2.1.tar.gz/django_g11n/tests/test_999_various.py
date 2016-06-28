"main testing module"
from django.test import TestCase

# Create your tests here.
class VariousTestCase(TestCase):
    "main test case"
    # pylint: disable=missing-docstring, no-member, invalid-name
    @classmethod
    def setUpClass(cls):
        returns = super(VariousTestCase, cls).setUpClass()
        from . import common
        from ..tools import models
        print('# Setting up IP ranges, this will take a while.')
        common.setup_ipranges_all()
        print('# ... done.')
        common.setup_currencies()
        return returns

    def setUp(self):
        TestCase.setUp(self)
        from django.core.management import call_command
        from . import common
        self.call = common.call_command_returns

    def tearDown(self):
        TestCase.tearDown(self)

    def test_001_guess(self):
        expected = 'GB'
        actually = self.call('guess_tld_by_ip',  '109.74.193.121')
        self.assertEqual(expected, actually)

        provided = 'GB'
        expected = 'GBP'
        actually = self.call('currency_by_tld', provided)
        self.assertEqual(expected, actually)


    def test_002_tools_fetch(self):
        from ..tools import fetch
        self.assertEqual(fetch.country_by_ip('0.0.0.0'), None)
        from ..tools import models
        _ = models.ALL['IPRange'].objects.get(id=1)
        _.id = None
        _.save()
        self.assertRaises(ValueError, fetch.country_by_ip, '3.0.0.1')
        


if __name__ == '__main__': # pragma: no cover
    # pylint: disable=wrong-import-position
    import django
    django.setup()
    django.core.management.call_command('test')

