'''
sxclient SX client-side library
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

sxclient is a library which implements methods for communicating with an SX
cluster. Using provided objects and functions, it is possible to prepare and
send a series of queries as per the API documentation at
<http://docs.skylable.com/>.

Example usage:

    >>> import sxclient
    >>> cluster = sxclient.Cluster('my.cluster.example.com')
    >>> user_data = sxclient.UserData.from_key_path('/path/to/my/keyfile')
    >>> with sxclient.ClusterSession(cluster, user_data) as session:
    ...     content = sxclient.ListUsers(cluster, session).json_call()

or:

    >>> import sxclient
    >>> cluster = sxclient.Cluster('my.cluster.example.com')
    >>> user_data = sxclient.UserData.from_key_path('/path/to/my/keyfile')
    >>> sx = sxclient.SXController(cluster, user_data)
    >>> sx.listUsers.json_call()

For more info about SX objects see their docstrings.


Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: Apache 2.0, see LICENSE for more details.

'''
from sxclient.models import Cluster, UserData
from sxclient.query import ClusterSession
from sxclient.controller import SXController
from sxclient.tools import (  # noqa
    SXFileCat,
    SXFileDownloader,
    SXFileUploader,
)
from sxclient.exceptions import *  # noqa

__version__ = '0.18.0'

__all__ = [
    'Cluster',
    'UserData',
    'ClusterSession',
    'SXController',
]
