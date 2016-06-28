"main testing module"
from django.test import TestCase

# pylint: disable=too-few-public-methods
class MockToolsIpranges(object):
    "Mock the currency module"
    def __init__(self):
        # identifier, regional_nic, tld, ipv, network_hex, broadcast_hex

        self._data = [
            ['1', 'NIC', 'GB', '4', '00000000', 'ffffffff'],
            ['2', 'NOC', '--', '4', '00000000', 'ffffffff'],
        ]

    def get(self):
        "Mock the get function"
        return self._data

# Create your tests here.
class UpdateIPRangesTestCase(TestCase):
    "main test case"
    # pylint: disable=missing-docstring, no-member, invalid-name
    @classmethod
    def setUpClass(cls):
        returns = super(UpdateIPRangesTestCase, cls).setUpClass()
        return returns

    def setUp(self):
        TestCase.setUp(self)
        from django.core.management import call_command
        self._call_command = call_command
        self._call_command('update_countries')

        from ..management.commands import update_ipranges
        self._update = update_ipranges
        self._restore = update_ipranges.ipranges

        update_ipranges.ipranges = MockToolsIpranges()

    def tearDown(self):
        TestCase.tearDown(self)
        self._update.ipranges = self._restore

    def test_001_insert(self):
        self._call_command('update_ipranges')
        # Calling twice, as the second time it should exclude it.
        self._call_command('update_ipranges')



if __name__ == '__main__': # pragma: no cover
    # pylint: disable=wrong-import-position
    import django
    django.setup()
    django.core.management.call_command('test')

