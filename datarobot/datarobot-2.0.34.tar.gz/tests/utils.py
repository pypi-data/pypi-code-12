import unittest
import contextlib
import warnings
import mock

from datarobot.client import set_client
from datarobot.rest import RESTClientObject


class SDKTestcase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        set_client(None)
        cls.patcher = mock.patch('datarobot.utils.get_endpoint_from_file')
        c = RESTClientObject(auth='t-token', endpoint='https://host_name.com')
        cls.patcher.return_value = None
        cls.patcher.start()
        set_client(c)

    @classmethod
    def tearDownClass(cls):
        cls.patcher.stop()
        set_client(None)


def assertJsonEq(first, second, msg='Ouups'):
    assert sorted(first) == sorted(second), '%r != %r\n%s' % (first,
                                                              second,
                                                              msg)


@contextlib.contextmanager
def warns(*categories):
    """Assert warnings are raised in a block, analogous to pytest.raises."""
    with warnings.catch_warnings(record=True) as messages:
        yield messages
    assert tuple(message.category for message in messages) == categories
