# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from .json_exporter import json_exporter
from .csv_exporter import csv_exporter

try:
    import cPicle as pickle
except ImportError:
    import pickle


def pickle_exporter(data, metadata, filepath, **kwargs):
    with open(filepath, "wb") as f:
        pickle.dump({'data': data, 'metadata': metadata}, f)
    return filepath
