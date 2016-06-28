"main testing module"
from django.test import TestCase, Client

# Create your tests here.
class VariousTestCase(TestCase):
    "main test case"
    # pylint: disable=missing-docstring, no-member, invalid-name, no-self-use
    def test_001(self):
        client = Client()
        client.get('', REMOTE_ADDR='109.74.193.121')

    def test_002_by_request_ipaddress(self):
        from ..tools import by_request
        import os
        os.environ['G11N_IP_OVERRIDE'] = ''
        self.assertRaises(ValueError, by_request.ipaddress, None)

    def test_003_by_request_ipaddress(self):
        from ..tools import by_request
        import os
        address = '109.74.193.121'
        os.environ['G11N_IP_OVERRIDE'] = address
        expected = {'ip':address}
        self.assertEqual(expected, by_request.ipaddress(None))

if __name__ == '__main__': # pragma: no cover
    # pylint: disable=wrong-import-position
    import django
    django.setup()
    django.core.management.call_command('test')

