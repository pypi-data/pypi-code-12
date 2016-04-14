#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import libsbml

"""High level SBML utils over libsbml"""

__author__ = "Nicolas Loira"
__email__ = "nloira@gmail.com"
__date__ = "14/March/2016"


def read_sbml(sbmlfile):
	document = libsbml.readSBML(sbmlfile)
	errors = document.getNumErrors()

	if errors > 0:
		document.printErrors()
		sys.exit("Invalid SBML.")
	else:
		return document


def log(msg):
	"""Write to stderr"""
	sys.stderr.write(msg + '\n')
