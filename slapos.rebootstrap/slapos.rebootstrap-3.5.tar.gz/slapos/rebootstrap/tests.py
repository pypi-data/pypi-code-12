##############################################################################
#
# Copyright (c) 2010 ViFiB SARL and Contributors.
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
from zope.testing import renormalizing
import doctest
import pkg_resources
import re
import sys
import unittest
import zc.buildout
import zc.buildout.testing
import zc.buildout.tests

def setUp(test):
  zc.buildout.testing.buildoutSetUp(test)
  zc.buildout.testing.install_develop('slapos.rebootstrap', test)

def test_suite():
  # Note: Doctests are used, as this is the good way to test zc.buildout based
  #       applications. And zc.buildout.testing.buildoutSetUp does *NOT* support
  #       non-doctest suites
  kwargs = dict(setUp=setUp,
      tearDown=zc.buildout.testing.buildoutTearDown,
      checker=renormalizing.RENormalizing([
                        (re.compile('--prefix=\S+sample-buildout'),
                         '--prefix=/sample_buildout'),
                        (re.compile('\s/\S+sample-buildout'),
                         ' /sample_buildout'),
                        (re.compile(sys.executable),
                         '/system_python'),
                        zc.buildout.testing.normalize_path,
                        ]),
    )
  test_list = []
  for text in pkg_resources.resource_listdir(__name__, '.'):
    if text.endswith('.txt'):
      test_list.append(doctest.DocFileSuite(text, **kwargs))
  suite = unittest.TestSuite(test_list)
  return suite
