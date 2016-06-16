
"""this module is defined to wrap the thrift.
"""

from tingyun.armoury.ammunition.external_tracker import wrap_external_trace


def detect_tsocket(module):
    """
    :param module:
    :return:
    """
    def tsocket_url(tsocket, *args, **kwargs):
        # _unix_socket is passed in when TSocket initialized
        # when wrap the specified func, the tsocket is instance.
        url = 'thrift://%s:%s' % (tsocket.host, tsocket.port)

        if tsocket._unix_socket is None:
            url = 'thrift://%s:%s' % (tsocket.host, tsocket.port)

        return url

    wrap_external_trace(module, 'TSocket.open', 'thrift', tsocket_url)


def detect_tsslsocket(module):
    """
    :param module:
    :return:
    """
    def tsocket_ssl_url(tsocket, *args, **kwargs):
        # _unix_socket is passed in when TSSSocket initialized
        # when wrap the specified func, the TSSSocket is instance.
        url = 'thrift//%s:%s' % (tsocket.host, tsocket.port)

        if tsocket._unix_socket is None:
            url = 'thrift//%s:%s' % (tsocket.host, tsocket.port)

        return url

    wrap_external_trace(module, 'TSSLSocket.open', 'thrift', tsocket_ssl_url)
