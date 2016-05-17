from ssl import PROTOCOL_TLSv1
TSL_v1 = PROTOCOL_TLSv1
DEFAULT_TLS_VERSION = PROTOCOL_TLSv1
try:
    from ssl import PROTOCOL_TLSv1_1
    TSL_v1_1 = PROTOCOL_TLSv1_1
except ImportError:
    TSL_v1_1 = DEFAULT_TLS_VERSION
try:
    from ssl import PROTOCOL_TLSv1_2
    DEFAULT_TLS_VERSION = PROTOCOL_TLSv1_2
    TSL_v1_2 = PROTOCOL_TLSv1_2
except ImportError:
    TSL_v1_2 = DEFAULT_TLS_VERSION

import sys

from netaddr import IPAddress, AddrFormatError
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager

from .exceptions import ValidationError

IS_PY3 = sys.version[0] == '3'
TIMEOUT = 5


def validate_port(port):
    try:
        p = int(port)
    except ValueError:
        raise ValidationError('Port must be an integer ({} given)'
                              .format(port))

    if not 1 <= p <= 65535:
        raise ValidationError('Invalid port number ({} given)'.format(p))


def validate_ip(ip):
    try:
        IPAddress(ip)
    except AddrFormatError:
        raise ValidationError('Invalid IP address ({} given)'.format(ip))


def validate_protocol(protocol):
    if protocol.upper() not in ('TCP', 'UDP'):
        raise ValidationError('Invalid protocol ({} given)'.format(protocol))


class UseTlsAdapter(HTTPAdapter):

    def __init__(self, tls_version):
        self.tls_version = tls_version
        super(UseTlsAdapter, self).__init__()

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize, block=block,
                                       ssl_version=self.tls_version)


def get_sub_vs_list_from_data(response_data):
    subvs_entries = []
    full_data = {}
    for key, value in response_data.items():
        if key == "SubVS":
            if isinstance(value, list):
                for subvs in value:
                    full_data[subvs['VSIndex']] = subvs
                    subvs_entries.append(subvs['VSIndex'])
            else:
                full_data[value['VSIndex']] = value
                subvs_entries.append(value['VSIndex'])
    return subvs_entries, full_data


def get_api_bool_string(api_bool):
    return 'y' if api_bool else 'n'
