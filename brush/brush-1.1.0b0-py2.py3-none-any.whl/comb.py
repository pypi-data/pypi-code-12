"""XMLRPC data acquisition from Menlo frequency combs."""

from abc import ABCMeta, abstractmethod
from collections import defaultdict
import time
import random
import six
from six.moves.xmlrpc_client import ServerProxy
from .stores import store


@six.add_metaclass(ABCMeta)
class BaseFrequencyComb(object):
    """Abstract base class for frequency combs. This allows for real
    and simulated combs for testing.

    """
    @abstractmethod
    def get_data(self):
        """Get data."""

    @abstractmethod
    def get_version(self):
        """Return the version number of the control software."""

    def __getitem__(self, key):
        """Shortcut for getting one data entry without timestamp."""
        result = self.get_data()
        return result[key]


class DummyFrequencyComb(BaseFrequencyComb):
    """Simulated frequency comb for testing purposes."""
    def __init__(self):
        """Create an empty metadata dict to be filled in later."""
        self.metadata = defaultdict(
            lambda: dict(type='double', description='Dummy test case'))
        self.metadata['offset.freq']['type'] = 'double'
        self.metadata['offset.freq']['description'] = 'Offset frequency'
        self.metadata['reprate.freq']['type'] = 'double'
        self.metadata['reprate.freq']['description'] = 'Rep rate frequency'
        self.metadata['system.locked']['type'] = 'bool'
        self.metadata['system.locked']['description'] = 'System locked?'
        self.metadata['counter.channels']['type'] = 'int'
        self.metadata['counter.channels']['description'] = 'Number of counter channels'
        self.metadata['counter0.freq']['type'] = 'double'
        self.metadata['counter0.freq']['description'] = 'Counter channel 0 frequency'
        self.metadata['counter1.freq']['type'] = 'double'
        self.metadata['counter1.freq']['description'] = 'Counter channel 1 frequency'
        self.metadata['counter2.freq']['type'] = 'double'
        self.metadata['counter2.freq']['description'] = 'Counter channel 2 frequency'
        self.metadata['lb1.status']['type'] = 'int'
        self.metadata['lb1.status']['description'] = 'Lockbox 1 status'
        self.metadata['lb2.status']['type'] = 'int'
        self.metadata['lb2.status']['description'] = 'Lockbox 2 status'
        store.metadata = self.metadata.copy()

    def get_data(self):
        """Return random data in order to simulate the presence of a
        Menlo XMLRPC server. Only a small subset of possible data keys
        are provided.

        :return: randomized data values
        :rtype: dict

        """
        data = {
            'counter.channels': 3,
            'offset.freq': random.uniform(19.9e6, 20.1e6),
            'reprate.freq': random.uniform(249.000999e6, 250.000999e6),
            'system.locked': random.choice([True, False]),
            'counter0.freq': random.uniform(19.9e6, 20.1e6),
            'counter1.freq': random.uniform(19.9e6, 20.1e6),
            'counter2.freq': random.uniform(19.9e6, 20.1e6),
            'lb1.status': random.choice([0, 1, 2]),
            'lb2.status': random.choice([0, 1, 2]),
            'timestamp': time.time()
        }
        return data

    def get_version(self):
        return '1.0.0_Dummy'

    def keys(self):
        return self.metadata.keys()


class FrequencyComb(BaseFrequencyComb):
    """Class for communicating with a Menlo frequency comb.

    :param str host: server hostname
    :param int port: server port
    :param user: username for authentication
    :type user: str or None
    :param password: password for authentication
    :type password: str or None

    """
    def __init__(self, host, port=8123, user=None, password=None):
        url = 'http://'
        if user is not None:
            assert isinstance(user, six.string_types)
            url += user
        if password is not None:
            assert isinstance(password, six.string_types)
            url += ':' + password
        url += '@'
        if host is None:
            raise RuntimeError("You must set the XMLRPC host.")
        assert isinstance(host, six.string_types)
        url += host + ':' + str(port) + '/RPC2'

        self.server = ServerProxy(url)
        data_info = self.server.data.getInfo()
        self.metadata = {
            key: {
                'type': data_info[key][0],
                'description':  data_info[key][1]
            } for key in self.server.data.getInfo().keys()
        }
        store.metadata = self.metadata.copy()

    def get_data(self):
        """Query the XMLRPC server for the most recent data.

        :return: all data values
        :rtype: dict

        """
        t = self.server.data.last_timestamp() - 0.01
        data = self.server.data.query(t)
        timestamp = list(data.keys())[0]
        data = data.pop(timestamp)
        result = {'timestamp': float(timestamp)}
        for key in data:
            if 'timestamp' not in key:
                result[key] = data[key]
        return result

    def get_version(self):
        """Return the version of the Menlo XMLRPC server software."""
        return self.server.hello()
