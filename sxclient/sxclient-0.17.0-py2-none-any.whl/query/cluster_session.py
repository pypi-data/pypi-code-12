'''
Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: Apache 2.0, see LICENSE for more details.
'''
import requests

from sxclient.defaults import DEFAULT_REQUEST_TIMEOUT
from sxclient.query.auth import SXAuth
from sxclient.query.hostname_adapter import SXHostnameAdapter


class ClusterSession(requests.Session):
    '''
    Custom session object used by a QueryHandler object.

    Initialization parameters:
      - cluster -- Cluster data structure; cluster.name is used for SSL
        verification
      - user_data -- UserData object used for authentication
      - request_timeout -- timeout for requests made in the scope of current
        session; defaults to sxclient.defaults.DEFAULT_REQUEST_TIMEOUT
    '''

    def __init__(
            self, cluster, user_data=None,
            request_timeout=DEFAULT_REQUEST_TIMEOUT
    ):
        super(ClusterSession, self).__init__()
        self.mount('https://', SXHostnameAdapter(assert_hostname=cluster.name))
        if user_data is not None:
            self.auth = SXAuth(user_data)
        self.verify = cluster.verify_ssl_cert
        self.request_timeout = request_timeout
