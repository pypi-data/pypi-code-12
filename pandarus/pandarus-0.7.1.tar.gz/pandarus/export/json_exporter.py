# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

import bz2
import codecs
import json


def json_exporter(data, metadata, filepath, compressed=True):
    if compressed:
        filepath += ".bz2"
        with bz2.BZ2File(filepath, "w") as f:
            f.write(json.dumps({'data': data, 'metadata': metadata},
                ensure_ascii=False).encode('utf-8'))
    else:
        with codecs.open(filepath, "w", encoding="utf-8") as f:
            json.dump({'data': data, 'metadata': metadata}, f, ensure_ascii=False)
    return filepath
