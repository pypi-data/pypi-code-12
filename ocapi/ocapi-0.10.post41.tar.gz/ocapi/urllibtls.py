#!/usr/bin/env python
# -*- coding:utf-8 -*-
# (c)Ing. Zdenek Dlauhy, Michal Dlauhý, info@dlauhy.cz

try:
    import http.client as httplib
except ImportError:
    import httplib
import socket
import ssl
import sys




try:
    import urllib.parse
except ImportError:
    #set same settigns as python 3
    import urllib
    import urllib2
    urllib.parse = urllib2.urlparse
    urllib.parse.urlencode = urllib.urlencode


# Python 2.6's urllib2 does not allow you to select the TLS dialect,
# and by default uses a SSLv23 compatibility negotiation implementation.
# Besides being vulnerable to POODLE, the OSX implementation doesn't
# work correctly, failing to connect to servers that respond only to
# TLS1.0+. These classes help set up TLS support for urllib2.

if sys.version_info < (3, 0, 0):
    class HTTPSConnection(httplib.HTTPConnection):
        "This class allows communication via SSL."
        default_port = httplib.HTTPS_PORT

        def __init__(self, host, port=None, key_file=None, cert_file=None,
                strict=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                source_address=None):
            httplib.HTTPConnection.__init__(self, host, port, strict, timeout,
                    source_address)
            self.key_file = key_file
            self.cert_file = cert_file

        def connect(self):
            "Connect to a host on a given (SSL) port."
            sock = socket.create_connection((self.host, self.port),
                    self.timeout, self.source_address)
            if self._tunnel_host:
                self.sock = sock
                self._tunnel()
            # this is the only line we modified from the httplib.py file
            # we added the ssl_version variable
            self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file, ssl_version=ssl.PROTOCOL_TLSv1)

    # now we override the one in httplib
    httplib.HTTPSConnection = HTTPSConnection
    # ssl_version corrections are done


def connect(host="pripravto.cz", url="/login", port=443, data=None, method="POST",
            headers=None, debug=None, cookie=None, tls=True, timeout=None):
        """patched url opener based on httplib with TLS support"""
        if timeout is None:
            timeout = 20
        # patch connection
        if tls:
            conn = httplib.HTTPSConnection(host, port, timeout=timeout)
        else:
            conn = httplib.HTTPConnection(host, port, timeout=timeout)
        # get headers, x-www-form-urlendoded is important
        if headers is None:
            headers = {"Content-type": "application/x-www-form-urlencoded",
                       "Accept": "text/plain"}
        if cookie and "Cookie" not in headers:
            headers['Cookie'] = cookie
        if 'User-Agent' not in headers:
            headers['User-Agent'] =  'Python ocapi connector - Python version 1.2'
        if isinstance(data, str):
            pass
        else:
            if data is not None:
                data = urllib.parse.urlencode(data)
        conn.request(method, url, data, headers)
        if debug:
            conn.set_debuglevel(level=debug)
        response = conn.getresponse()
        return response
