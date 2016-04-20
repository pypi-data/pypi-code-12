'''
Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: Apache 2.0, see LICENSE for more details.
'''
import copy
from collections import deque, Iterable
from random import shuffle
from threading import Lock

from requests.compat import urlunparse

from sxclient.tools import get_addresses, toutf8

__all__ = ['Cluster']


class Cluster(object):
    '''
    Store cluster connection parameters and provide connection data for cluster
    and its specific nodes.

    Initialization parameters:
      - name -- name of the cluster; used to lookup node addresses in case
        ip_addresses is not set
      - ip_addresses -- IP address or addresses of a node or nodes belonging to
        the cluster; should be passed either as string, or a iterable
        containing strings, each corresponding to an IP address
      - is_secure -- flag determining whether the connection will be secured by
        SSL
      - verify_ssl_cert -- parameter indicating whether the SSL certificate
        used for connection should be validated; defaults to True. If string is
        passed as a value, it is be used as a path to a custom trusted CA
        bundle for certificate verifications.
      - port -- custom remote port to connect to; if unset, default ports will
        be used (443 for https, 80 for http)
    '''

    def __init__(
        self, name, ip_addresses=None, is_secure=True, verify_ssl_cert=True,
        port=None
    ):
        self._addresses_lock = Lock()

        self.name = toutf8(name)
        if ip_addresses is not None:
            self.set_ip_addresses(ip_addresses)
        else:
            self.set_ip_addresses(
                toutf8(addr) for addr in get_addresses(self.name)
            )
        self.is_secure = is_secure
        self.verify_ssl_cert = verify_ssl_cert
        self.port = int(port) if port is not None else None

    def set_ip_addresses(self, ip_addresses):
        with self._addresses_lock:
            try:
                addresses = deque([toutf8(ip_addresses)])
            except TypeError:
                if isinstance(ip_addresses, Iterable):
                    addresses = deque(
                        toutf8(addr) for addr in ip_addresses
                    )
                else:
                    raise TypeError(
                        'ip_addresses should be either iterable or string, is '
                        '%s' % type(ip_addresses).__name__
                    )
            shuffle(addresses)
            self._addresses = addresses

    def iter_ip_addresses(self):
        '''Return iterator over available IP addresses.'''
        with self._addresses_lock:
            addresses = copy.copy(self._addresses)
            return iter(addresses)

    @property
    def url(self):
        return self.get_host_url(self.host)

    def get_host_url(self, host):
        '''Get URL for a node host specified in the argument.'''
        data = (self.scheme, self.get_host_netloc(host), '', '', '', '')
        url = urlunparse(data)
        return url

    @property
    def host(self):
        with self._addresses_lock:
            addr = self._addresses[0]
            self._addresses.rotate(-1)
            return addr

    @property
    def scheme(self):
        if self.is_secure:
            scheme = 'https'
        else:
            scheme = 'http'
        return scheme

    def get_host_netloc(self, host):
        '''
        Get network location (host + port) for a node host specified in the
        argument.
        '''
        # if host is IPv6 address, add brackets
        if ':' in host:
            host = ''.join(('[', host, ']'))
        if self.port is not None:
            netloc = ':'.join((host, str(self.port)))
        else:
            netloc = host
        return netloc
