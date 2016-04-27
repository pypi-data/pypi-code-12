# encoding: utf-8
# Copyright 2011–2014 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EDRN Site Collaborations: functional tests.'''

import doctest
import unittest2 as unittest
from plone.testing import layered
from edrnsite.collaborations.testing import EDRNSITE_COLLABORATIONS_FUNCTIONAL_TESTING as LAYER

optionFlags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE | doctest.REPORT_ONLY_FIRST_FAILURE)

def test_suite():
    return unittest.TestSuite([
        layered(doctest.DocFileSuite('README.rst', package='edrnsite.collaborations', optionflags=optionFlags), LAYER),
    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
