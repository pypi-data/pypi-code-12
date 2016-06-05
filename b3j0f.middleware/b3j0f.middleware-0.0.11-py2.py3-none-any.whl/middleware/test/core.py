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

from ..core import register, unregister, getmcallers, getprotocols


class RegisterTest(UTCase):
    """Test for the functions register and unregister."""

    def setUp(self):

        unregister()

    def tearDown(self):

        unregister()

    def test_decorator(self):

        @register('a')
        def exa():
            """"""
            pass

        @register(['a', 'b'])
        def exab():
            pass

        @register(['b', 'c'])
        def exbc():
            pass

        self._test(exa, exab, exbc)

    def test_func(self):

        exa = lambda: None
        exab = lambda: None
        exbc = lambda: None

        register('a', exa)
        register(['a', 'b'], exab)
        register(['b', 'c'], exbc)

        self._test(exa, exab, exbc)

    def _test(self, a, ab, bc):

        with self.assertRaises(TypeError):
            register('a', 1)

        mcallers = getmcallers('a')
        self.assertEqual(mcallers, set([a, ab]))
        mcallers = getmcallers('b')
        self.assertEqual(mcallers, set([ab, bc]))
        mcallers = getmcallers('c')
        self.assertEqual(mcallers, set([bc]))
        mcallers = getmcallers(['a', 'b'])
        self.assertEqual(mcallers, set([ab]))
        mcallers = getmcallers(['b', 'c'])
        self.assertEqual(mcallers, set([bc]))

        with self.assertRaises(ValueError):
            getmcallers(['error'])

        with self.assertRaises(ValueError):
            getmcallers([])

        protocols = getprotocols()
        self.assertEqual(protocols, set('abc'))

        protocols = getprotocols(a)
        self.assertEqual(protocols, set('a'))

        protocols = getprotocols(ab)
        self.assertEqual(protocols, set('ab'))

        protocols = getprotocols(bc)
        self.assertEqual(protocols, set('bc'))

        unregister(a)
        mcallers = getmcallers('a')
        self.assertEqual(mcallers, set([ab]))

        unregister(protocols='b')
        with self.assertRaises(ValueError):
            getmcallers('b')

        protocols = getprotocols(bc)
        self.assertEqual(protocols, set(['c']))

        register('b', bc)
        protocols = getprotocols(bc)
        self.assertEqual(protocols, set('bc'))

        unregister(bc, 'b')
        protocols = getprotocols(bc)
        self.assertEqual(protocols, set(['c']))

        unregister()
        protocols = getprotocols()
        self.assertFalse(protocols)


if __name__ == '__main__':
    main()
