#===============================================================================
# The Broad Institute
# SOFTWARE COPYRIGHT NOTICE AGREEMENT
# This software and its documentation are copyright 2016 by the
# Broad Institute/Massachusetts Institute of Technology. All rights reserved.
#
# This software is supplied without any warranty or guaranteed support whatsoever.
# Neither the Broad Institute nor MIT can be responsible for its use, misuse, or
# functionality.
#===============================================================================

import os
from setuptools import setup, find_packages

#===============================================================================
# Setup
#===============================================================================

README = open('README').read()
README = README.replace("&nbsp;","")
README = README.replace("**","")

setup(
	name         = 'mdbtools',
    version      = "0.3.3",
    author       = 'Michael S. Noble',
    author_email = 'mnoble@broadinstitute.org', 
    url          = 'https://github.com/broadinstitute/mdbtools',
    packages     = find_packages(),
    description  = (
		"mdbtools: Python and UNIX CLI utilities to simplify common MongoDB DevOps tasks"
	),
    long_description = README,
    entry_points     = {
		'console_scripts': [
			# FIXME: this list s/b generated from $(TOOLS) macro in Makefile
			'mdbcat = mdbtools:console',
			'mdbcp = mdbtools:console',
			'mdbls = mdbtools:console',
			'mdbmv = mdbtools:console',
			'mdbquery = mdbtools:console',
			'mdbrm = mdbtools:console',
			'mdbstats = mdbtools:console',
			'mdbtouch = mdbtools:console',
		]
	},
    test_suite   = 'nose.collector',
)
