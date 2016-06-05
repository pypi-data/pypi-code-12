# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

import sys
if sys.version_info < (3, 0):
    from ._unicodecsv import writer
else:
    from csv import writer


def csv_exporter(data, metadata, filepath, **kwargs):
    w = writer(open(filepath, "w", encoding='utf-8'))
    for line in data:
        w.writerow(line)
    return filepath
