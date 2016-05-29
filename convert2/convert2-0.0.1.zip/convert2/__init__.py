#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "0.0.1"
__short_description__ = "Convert anything to any type."
__license__ = "MIT"

import warnings

try:
    from .converter import any2int, any2float, any2str, any2datetime, any2date
except Exception as e:
    warnings.warn("Please install numpy an pandas first.")