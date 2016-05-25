# encoding: utf-8
from distutils.version import LooseVersion as Ver
import operator

from .exceptions import PockerException, PVersionError

OPERATORS_MAP = {
    '<':    operator.lt,
    '<=':   operator.le,
    '==':   operator.eq,
    '>=':   operator.ge,
    '>':    operator.gt,
}

def required_version(current_version, versions):
    for version in versions:
        if not ' ' in version:
            raise PockerException(u"Wrong version specification. "
                                  u"Operator and version must be serparataed with space. "
                                  u"Example: '>= 1.6'")
        operator, version = version.split()
        if not OPERATORS_MAP[operator](Ver(current_version), Ver(version)):
            raise PVersionError(u"Current docker verions: '{0}'. ".format(current_version) +
                                u"Required version: '{0}'".format(operator+version))

class QueryDict(dict):
    '''QueryDict is a dict() that can be queried with dot.'''
    def __getattr__(self, attr):
        try:
            return self.__getitem__(attr)
        except KeyError:
            raise AttributeError(attr)

    def __setattr__(self, attr, value):
        self.__setitem__(attr, value)
qdict = QueryDict


import socket
import errno
from time import time as now
#code.activestate.com/recipes/578955-wait-for-network-service-to-appear/
def wait_net_service(server, port, timeout=None):
    """ Wait for network service to appear
        @param timeout: in seconds, if None or 0 wait forever
        @return: True of False, if timeout is None may return only True or
                 throw unhandled network exception
    """

    # time module is needed to calc timeout shared between two exceptions
    end = timeout and now() + timeout

    while True:
        #create new socket each time to avoid ECONNABORTED
        #https://stackoverflow.com/questions/9646550/what-does-econnaborted-mean-when-trying-to-connect-a-socket
        s = socket.socket()
        try:
            if timeout:
                next_timeout = end - now()
                if next_timeout < 0:
                    return False
                else:
                    s.settimeout(next_timeout)

            s.connect((server, port))

        except socket.timeout as err:
            # this exception occurs only if timeout is set
            if timeout:
                return False

        except socket.error as err:
            # catch timeout exception from underlying network library
            # this one is different from socket.timeout
            if type(err.args) != tuple or err[0] not in (errno.ETIMEDOUT, errno.ECONNREFUSED):
                raise
        else:
            s.close()
            return True

