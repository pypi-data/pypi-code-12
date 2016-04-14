#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of BioPantograph https://bitbucket.org/nloira/pantograph
# Copyright © 2009-2016 Nicolas Loira
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BioPantograph.  If not, see <http://www.gnu.org/licenses/>.

"""High level SBML utils over libsbml"""

import sys
import libsbml


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
