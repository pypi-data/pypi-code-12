##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Tag test setup"""

import doctest
import unittest


def test_suite():
    optionflags = (doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS |
                   doctest.REPORT_ONLY_FIRST_FAILURE)
    return unittest.TestSuite([
        doctest.DocFileSuite('README.txt', optionflags=optionflags),
        doctest.DocFileSuite('subset.txt', optionflags=optionflags),
        doctest.DocTestSuite('z3c.batching.batch', optionflags=optionflags),
    ])
