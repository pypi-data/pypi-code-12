'''
Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: Apache 2.0, see LICENSE for more details.
'''
from requests import ConnectionError

from sxclient.cache import region
from sxclient.defaults import UUID_HEADER_PATTERN, DEFAULT_REQUEST_TIMEOUT
from sxclient.exceptions import SXClusterNonFatalError

from sxclient.query.cluster_session import ClusterSession
from sxclient.operations import OPERATION_CLASSES


class SXController(object):
    '''
    Controlls all defined operations.

    Example usage:

        >>> import sxclient
        >>>
        >>> # initialize sx
        >>> cluster = sxclient.Cluster('my.cluster.example.com')
        >>> user_data = sxclient.UserData.from_key_path('/path/to/my/keyfile')
        >>> sxcontroller = sxclient.SXController(cluster, user_data)
        >>>
        >>> print sxcontroller.available_operations
        ['listUsers', 'getClusterMetadata', 'listNodes', 'deleteVolume', ...]
        >>>
        >>> help(sxcontroller.listUsers)
        # some help comes here
        >>>
        >>> sxcontroller.listUsers.json_call()
        {u'admin': {u'admin': True, u'userQuotaUsed': 0, ...
    '''

    def __init__(
            self, cluster, user_data=None,
            request_timeout=DEFAULT_REQUEST_TIMEOUT
    ):
        self._user_data = user_data
        self.available_operations = []
        self.cluster = cluster
        self.session = ClusterSession(
            self.cluster,
            user_data=user_data,
            request_timeout=request_timeout
        )
        self._initialize_operations()

    def close(self):
        self.session.close()

    def _initialize_operations(self):
        for name, operation_class in OPERATION_CLASSES.iteritems():
            operation_instance = operation_class(
                self.cluster, self.session
            )
            attr_name = name[:1].lower() + name[1:]
            if hasattr(self, attr_name):
                raise AttributeError(
                    '%s already exists on SXController class' % attr_name
                )

            setattr(self, attr_name, operation_instance)
            self.available_operations.append(attr_name)

    @region.cache_on_arguments(namespace='python-sxclient')
    def get_cluster_uuid(self):
        '''
        Retrieves the uuid of the underlying cluster. The result of this
        call is cached for 10 minutes so you don't have to worry about
        performance when calling this method multiple times.
        '''

        resp = None
        last_exception = None
        for address in self.cluster.iter_ip_addresses():
            try:
                url = self.cluster.get_host_url(address)
                resp = self.session.head(url)
                break
            except ConnectionError as exc:
                last_exception = exc

        if resp is None:
            raise last_exception

        if 'sx-cluster' not in resp.headers:
            msg = "No 'SX-Cluster' header in the response"
            raise SXClusterNonFatalError(msg)
        cluster_header = resp.headers['sx-cluster']
        uuid = UUID_HEADER_PATTERN.findall(cluster_header).pop()
        return uuid.lower()
