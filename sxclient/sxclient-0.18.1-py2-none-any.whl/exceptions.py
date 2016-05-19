'''
Exceptions specific for the package.

Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: Apache 2.0, see LICENSE for more details.

'''

__all__ = [
    'SXClientException',
    'OperationError',
    'InvalidUserKeyError',
    'SXClusterError',
    'SXClusterNonFatalError',
    'SXClusterRequestTimeout',
    'SXClusterTooManyRequests',
    'SXClusterNotFound',
    'SXClusterNodeNotAMember',
    'SXClusterInternalError',
    'SXClusterFatalError',
    'SXClusterClientError',
    'SXClusterPayloadTooLarge',
    'SXClusterBadRequest',
    'SXClusterUnauthorized',
    'SXClusterForbidden',
]


class SXClientException(Exception):
    '''
    General exception type for library-specific exceptions.
    '''


class OperationError(SXClientException):
    '''
    Should be raised during operation execution in case of errors unrelated to
    communication with the cluster.
    '''


class InvalidUserKeyError(SXClientException):
    '''
    Should be raised when a user key is invalid.
    '''


class SXClusterError(SXClientException):
    '''
    Should be raised when a problem occurs during communication with the
    cluster.
    '''


class SXClusterNonFatalError(SXClusterError):
    '''
    Should be raised when the cluster communication problem is non-fatal.
    '''


class SXClusterRequestTimeout(SXClusterNonFatalError):
    '''
    Should be raised when there's a request timeout.
    '''


class SXClusterTooManyRequests(SXClusterNonFatalError):
    '''
    Should be raised when there's too many requests to cluster.
    '''


class SXClusterNotFound(SXClusterNonFatalError):
    '''
    Should be raised when cluster responds with 404.
    '''


class SXClusterNodeNotAMember(SXClusterNonFatalError):
    '''
    Should be raised when the queried node is no longer a cluster member
    (cluster responds with 410).
    '''


class SXClusterInternalError(SXClusterNonFatalError):
    '''
    Should be raised when cluster responds with >= 500.
    '''


class SXClusterFatalError(SXClusterError):
    '''
    Should be raised when the cluster communication problem is fatal.
    '''


class SXClusterClientError(SXClusterFatalError):
    '''
    Should be raised when the cluster communication problem is due to
    client's error.
    '''


class SXClusterPayloadTooLarge(SXClusterClientError):
    '''
    Should be raised when trying to upload a file bigger then volume's
    free space.
    '''


class SXClusterBadRequest(SXClusterClientError):
    '''
    Should be raised when making an invalid request to cluster.
    '''


class SXClusterUnauthorized(SXClusterClientError):
    '''
    Should be raised when trying to access cluster with invalid credentials.
    '''


class SXClusterForbidden(SXClusterClientError):
    '''
    Should be raised when trying to access cluster without expected privileges.
    '''
