# -*- coding: utf-8 -*-

from b3j0f.conf import Configurable, category, Parameter
from link.middleware.connectable import ConnectableMiddleware
from link.etcd import CONF_BASE_PATH

from etcd import Client, EtcdKeyNotFound
import os


@Configurable(
    paths='{0}/middleware.conf'.format(CONF_BASE_PATH),
    conf=category(
        'ETCD',
        Parameter(name='host', value='localhost'),
        Parameter(name='port', ptype=int, value=4001),
        Parameter(name='srv_domain', value=None),
        Parameter(name='version_prefix', value='/v2'),
        Parameter(name='read_timeout', ptype=int, value=60),
        Parameter(name='allow_redirect', ptype=bool, value=True),
        Parameter(name='protocol', value='http'),
        Parameter(name='cert', value=None),
        Parameter(name='ca_cert', value=None),
        Parameter(name='username', value=None),
        Parameter(name='password', value=None),
        Parameter(name='allow_reconnect', ptype=bool, value=False),
        Parameter(name='use_proxies', ptype=bool, value=False),
        Parameter(name='expected_cluster_id', value=None),
        Parameter(name='per_host_pool_size', ptype=int, value=10)
    )
)
class EtcdMiddleware(ConnectableMiddleware):
    """
    Middleware that connects to **etcd**.

    The following operations are available:

    .. code-block:: python

       client = EtcdMiddleware()
       client['/path'] = value
       value = client['/path']
       del client['/path']
       '/path' in client

    If ``value`` is a ``dict``, then paths are created recursively.
    If ``value`` is a ``list``, then items are appended to the directory.
    """

    __protocols__ = ['etcd']

    def _connect(self):
        return Client(
            host=self.host,
            port=self.port,
            srv_domain=self.srv_domain,
            version_prefix=self.version_prefix,
            read_timeout=self.read_timeout,
            allow_redirect=self.allow_redirect,
            protocol=self.protocol,
            cert=self.cert,
            ca_cert=self.ca_cert,
            username=self.username,
            password=self.password,
            allow_reconnect=self.allow_reconnect,
            use_proxies=self.use_proxies,
            expected_cluster_id=self.expected_cluster_id,
            per_host_pool_size=self.per_host_pool_size
        )

    def _disconnect(self, conn):
        del conn

    def _isconnected(self, conn):
        return conn is not None

    def _readval(self, path):
        node = self.conn.read(path, recursive=True)

        if node.dir:
            result = {
                child.key: self._readval(os.path.join(path, child.key))
                for child in node._children
            }

        else:
            result = node.value

        return result

    def __getitem__(self, path):
        try:
            result = self._readval(path)

        except EtcdKeyNotFound as err:
            raise KeyError(str(err))

        return result

    def _writeval(self, path, val):
        if isinstance(val, dict):
            self.conn.write(path, dir=True)

            for key in val:
                keypath = os.path.join(path, key)
                self._writeval(keypath, val[key])

        elif isinstance(val, list):
            self.conn.write(path, dir=True)

            for item in val:
                self.conn.write(path, item, append=True)

        else:
            self.conn.write(path, val)

    def __setitem__(self, path, val):
        dirname = os.dirname(path)

        if dirname != '/':
            self.conn.write(dirname, dir=True)

        self._writeval(path, val)

    def __delitem__(self, path):
        self.conn.delete(path, recursive=True)

    def __contains__(self, path):
        return path in self.conn
