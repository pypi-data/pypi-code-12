# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
"""
git-flow -- A collection of Git extensions to provide high-level
repository operations for Vincent Driessen's branching model.
"""
#
# This file is part of `gitflow`.
# Copyright (c) 2010-2011 Vincent Driessen
# Copyright (c) 2012-2013 Hartmut Goebel
# Copyright (c) 2015 Christian Assing
# Distributed under a BSD-like license. For full terms see the file LICENSE.txt
#

VERSION = (1, 0, 1,)

__version__ = ".".join(map(str, VERSION[0:3])) + "".join(VERSION[3:])
__author__ = "Christian Assing, Hartmut Goebel, Vincent Driessen"
__contact__ = "chris@ca-net.org"
__homepage__ = "http://github.com/chassing/gitflow/"
__docformat__ = "restructuredtext"
__copyright__ = "2010-2011 Vincent Driessen; 2012-2013 Hartmut Goebel; 2015 Christian Assing"
__license__ = "BSD"
