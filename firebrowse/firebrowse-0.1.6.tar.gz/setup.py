#===============================================================================
# The Broad Institute
# SOFTWARE COPYRIGHT NOTICE AGREEMENT
# This software and its documentation are copyright 2015-2016 by the
# Broad Institute/Massachusetts Institute of Technology. All rights are reserved.
#
# This software is supplied without any warranty or guaranteed support whatsoever. Neither
# the Broad Institute nor MIT can be responsible for its use, misuse, or functionality.
# 
#===============================================================================

import os
from setuptools import setup, find_packages

#===============================================================================
# Setup
#===============================================================================

setup(
      name         = 'firebrowse',
      version      = "0.1.6",
      author       = 'Michael S. Noble, Dan DiCara',
      author_email = 'gdac@broadinstitute.org', 
      url          = 'http://firebrowse.org',
      packages     = find_packages(),
      description  = ("Firebrowse portal API bindings for Python"),
      long_description = open('README').read(),
      entry_points     = {'console_scripts': ['fbget = firebrowse.fbget:main']},
      test_suite   = 'nose.collector',
)
