#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

__version__ = "0.0.4"
__short_description__ = "A utility tool to help you build better sphinx documents"
__license__ = "MIT"

try:
    from .api_reference_doc import ApiReferenceDoc
    from .doctree import DocTree
except Exception as e:
    print(e)