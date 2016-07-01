#!/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

here = os.path.abspath(os.path.dirname(__file__))
try:
    import dockerfly
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(here, '../../')))
