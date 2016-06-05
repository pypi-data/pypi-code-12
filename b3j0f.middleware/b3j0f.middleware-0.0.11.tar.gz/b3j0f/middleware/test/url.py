#!/usr/bin/env python
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

from b3j0f.utils.ut import UTCase

from unittest import main

from six.moves.urllib.parse import parse_qs, urlencode

from ..url import URLMiddleware, fromurl, getmcallerswp
from ..core import getprotocols, register

from functools import reduce


class URLMiddlewareTest(UTCase):
    """Test for the functions register and unregister."""

    def setUp(self):

        self.scheme = 'scheme'

    def test_default(self):
        """Test with default parameters."""

        urlmiddleware = URLMiddleware(scheme=self.scheme)

        self.assertEqual(urlmiddleware.scheme, self.scheme)
        self.assertEqual(urlmiddleware.hostname, URLMiddleware.DEFAULT_HOST)
        self.assertEqual(urlmiddleware.port, 0)
        self.assertIsNone(urlmiddleware.user)
        self.assertIsNone(urlmiddleware.password)
        self.assertIsNone(urlmiddleware.path)
        self.assertFalse(urlmiddleware.query)
        self.assertFalse(urlmiddleware.fragment)

        url = urlmiddleware.url

        self.assertEqual(url, 'scheme://localhost')

    def test_params(self):
        """Test with parameters."""

        hostname = 'hostname'
        port = 25
        user = 'user'
        password = 'password'
        path = ['path']
        query = {'query': 'query'}
        fragment = 'fragment'

        urlmiddleware = URLMiddleware(
            scheme=self.scheme, hostname=hostname, port=port, user=user,
            password=password, path=path, query=query, fragment=fragment
        )

        self.assertEqual(urlmiddleware.scheme, self.scheme)
        self.assertEqual(urlmiddleware.hostname, hostname)
        self.assertEqual(urlmiddleware.port, port)
        self.assertEqual(urlmiddleware.user, user)
        self.assertEqual(urlmiddleware.password, password)
        self.assertEqual(urlmiddleware.path, path)
        self.assertEqual(urlmiddleware.query, query)
        self.assertEqual(urlmiddleware.fragment, fragment)

        url = urlmiddleware.url
        self.assertEqual(
            url, 'scheme://user:password@hostname:25/path?query=query#fragment'
        )

class Tests(UTCase):
    """Test functions getmcallerswp, fromurl and tourl."""

    class TestA(URLMiddleware):
        __protocols__ = ['a']

    class TestBC(TestA):
        __protocols__ = ['c', 'b']

    def setUp(self):

        self.scheme = ['a', 'b-a-c']
        self.user = 'user'
        self.password = 'password'
        self.hostname = 'hostname'
        self.port = 25
        self.path = 'path/path'
        self.query = {'query': 'query'}
        self.fragment = 'fragment'

        self.url = '{0}://{1}:{2}@{3}:{4}/{5}?{6}#{7}'.format(
            reduce(lambda x, y: x + '+' + y, self.scheme),
            self.user, self.password, self.hostname, self.port, self.path,
            urlencode(self.query), self.fragment
        )

    def test_getmcallerswp(self):
        """Test the function getmcallerswp."""

        mcallerswp, kwargs = getmcallerswp(self.url)

        mprotocols0, mcallers0 = mcallerswp[0]
        self.assertEqual(mcallers0, set([self.TestA, self.TestBC]))
        self.assertEqual(mprotocols0, 'a')

        mprotocols1, mcallers1 = mcallerswp[1]
        self.assertEqual(mcallers1, set([self.TestBC]))
        self.assertEqual(mprotocols1, 'b-a-c')

        self.assertEqual(
            kwargs,
            {
                'user': self.user,
                'password': self.password,
                'hostname': self.hostname,
                'port': self.port,
                'path': [''] + self.path.split('/'),
                'query': self.query,
                'fragment': self.fragment
            }
        )

    def test_fromurl(self):
        """Test the function fromurl."""

        middlewares = fromurl(self.url)

        self.assertIsInstance(middlewares[0], self.TestA)
        self.assertIsInstance(middlewares[1], self.TestBC)
        self.assertIs(middlewares[0].nextm, middlewares[1])

        middlewares2 = fromurl(self.url)

        self.assertEqual(middlewares, middlewares2)

        middlewares3 = fromurl(self.url, False)

        self.assertNotEqual(middlewares3, middlewares)

        self.assertEqual(
            middlewares[0].url,
            self.url
        )


if __name__ == '__main__':
    main()
