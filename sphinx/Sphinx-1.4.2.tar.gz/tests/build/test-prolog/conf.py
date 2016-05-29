# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, os.path.abspath('.'))


master_doc = 'index'
extensions = ['test_source_parser']

rst_prolog = '*Hello world*.\n\n'
rst_epilog = '\n\n*Good-bye world*.'
