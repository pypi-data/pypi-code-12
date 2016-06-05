# -*- coding: utf-8 -*-

# --------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2016 Jonathan Labéjof <jonathan.labejof@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# --------------------------------------------------------------------

"""Module dedicated to ease registration and instanciation of middleware from
an URL."""

__all__ = ['URLMiddleware', 'fromurl', 'getmcallerswp']

from six.moves.urllib.parse import (
    urlsplit, urlunsplit, SplitResult, parse_qs, urlencode
)

from inspect import getmembers, isroutine

from b3j0f.utils.iterable import first

from .core import getmcallers
from .cls import Middleware

PROTOCOL_MSEPARATOR = '-'  #: multi protocol separator character.
PROTOCOL_SSEPARATOR = '+'  #: successive protocol separator character.


def convertquery(query):

    result = query.copy() if query else {}

    if result:
        for key in query:
            val = query[key]
            if len(val) == 1:
                result[key] = val[0]

    return result


class URLMiddleware(Middleware):
    """Middleware instanciated with a URL properties."""

    DEFAULT_HOST = 'localhost'  #: default hostname.

    def __init__(
            self, scheme, hostname=DEFAULT_HOST, port=0, user=None,
            password=None, path=None, query=None, fragment='',
            nextm=None, *args, **kwargs
    ):
        """
        :param str scheme: url scheme which corresponds to one of this protocol.
        :param str hostname: hostname name.
        :param int port: port value.
        :param str user: user name.
        :param str password: user password.
        :param list path: url path.
        :param dict query: url query.
        :param str fragment: urlfragment.
        :param URLMiddleware nextm: next middleware.
        """

        super(URLMiddleware, self).__init__(*args, **kwargs)

        self.scheme = scheme
        self.hostname = hostname
        self.port = port
        self.user = user
        self.password = password
        self.path = path
        self.query = convertquery(query)
        self.fragment = fragment
        self.nextm = nextm

    @property
    def splitresult(self):
        """Return self splitresult.

        :rtype: str"""

        scheme = self.scheme
        user = self.user
        password = self.password
        hostname = self.hostname
        port = self.port
        path = '/'.join(self.path) if self.path else ''
        query = urlencode(self.query) if self.query else ''
        fragment = self.fragment

        if self.nextm:

            nsr = self.nextm.splitresult

            scheme = '{0}+{1}'.format(scheme, nsr.scheme)
            if not user:
                user = nsr.user
            if not password:
                password = nsr.password
            if not hostname:
                hostname = nsr.hostname
            if not port:
                port = nsr.port
            if not path:
                path = nsr.path
            if not query:
                query = convertquery(parse_qs(nsr.query))
            else:
                query = self.query.copy()
                query.update(convertquery(parse_qs(nsr.query)))
                query = urlencode(query)
            if not fragment:
                fragment = nsr.fragment

        netloc = '{0}{1}{2}'.format(
            (
                '{0}{1}@'.format(
                    user if user else '',
                    ':{0}'.format(password) if password else ''
                )
            ) if user else '',
            hostname,
            ':{0}'.format(port) if port else ''
        )

        return SplitResult(
            scheme=scheme,
            netloc=netloc,
            path=path,
            query=query,
            fragment=fragment
        )


    @property
    def url(self):
        """Return self url.

        :rtype: str"""

        return urlunsplit(self.splitresult)


_CACHED_MIDDLEWARE = {}


def getmcallerswp(url):
    """Get list of middleware callers with parameters from an URL.

    The list of middleware callers is choosen from the scheme and might accept
        such as callable parameters:

    - a scheme: registered protocols separated with the '-' and '+' characters.
    - an hostname: url hostname.
    - a port: url port.
    - an username: user name.
    - a password: a password value.
    - a path: url path.
    - a fragment: url fragment.

    And additional parameters given by the url queries.

    :param str url: url from where instanciate a middleware.
    :param bool cache: if True (default), return old registered middleware
        instance with the same url.

    .. example:

        git+ssh-local://pseudo:pwd@website/

        returns [('git', gitmcallers), ('ssh-local', sshmcallers)], {'user': pseudo, 'password': pwd, 'hostname': website}

    :rtype: tuple"""

    parseduri = urlsplit(url)

    protocols = parseduri.scheme.split(PROTOCOL_SSEPARATOR)

    path = parseduri.path

    if path:
        path = path[1:]
        path = parseduri.path.split('/')

    kwargs = {
        'hostname': parseduri.hostname, 'port': parseduri.port,
        'user': parseduri.username, 'password': parseduri.password,
        'path': path, 'query': convertquery(parse_qs(parseduri.query)),
        'fragment': parseduri.fragment
    }

    mcallerswithparams = []

    for protocol in protocols:

        mprotocols = protocol.split(PROTOCOL_MSEPARATOR)

        mcallers = getmcallers(mprotocols)

        mcallerswithparams.append((protocol, mcallers))

    return mcallerswithparams, kwargs


def fromurl(url, cache=True, chain=True):
    """Get list of middleware from an URL.

    The list of middleware is choosen from the scheme and might accept such as
    callable parameters:

    - a scheme: registered protocols separated with the '-' and '+' characters.
    - an hostname: url hostname.
    - a port: url port.
    - an username: user name.
    - a password: a password value.
    - a path: url path.
    - a fragment: url fragment.

    And additional parameters given by the url queries.

    :param str url: url from where instanciate a middleware.
    :param bool cache: if True (default), return old registered middleware
        instance with the same url.
    :param bool chain: each middleware instance is given to the previous one.

    .. example:

        git+ssh-local://pseudo:pwd@website/

        returns git(user=pseudo, ..., nextm=sshlocal(user=pseudo, ...))

    :rtype: list
    :return: middleware initialized with url properties."""

    if cache and url in _CACHED_MIDDLEWARE:
        result = _CACHED_MIDDLEWARE[url]

    else:
        mcallerswp, kwargs = getmcallerswp(url)

        result = []

        mcallerswp.reverse()

        lastm = None

        for protocol, mcallers in mcallerswp:

            mcaller = first(mcallers)

            middleware = mcaller(scheme=protocol, nextm=lastm, **kwargs)

            result.append(middleware)

            if chain:
                lastm = middleware

        result.reverse()

        if cache:
            _CACHED_MIDDLEWARE[url] = result

    return result
