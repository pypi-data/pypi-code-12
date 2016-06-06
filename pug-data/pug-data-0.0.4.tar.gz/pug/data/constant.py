#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Constants (paths, translation dictionaries)
>>> os.path.isdir(DATA_PATH)
True
>>> DICT_ROMAN2INT['IX']
9
>>> DICT_ROMAN2INT['XLII']
42
>>> DICT_ROMAN2INT['XXX']
30
>>> DICT_ROMAN2INT['LXXV']
85
"""

import os

MODULE_PATH = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.join(MODULE_PATH, 'cache')
DICT_ROMAN2INT = {'': 0, 'I': 1, 'II': 2, 'III': 3, 'IV': 4,  'V': 5,
                  'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9}
R2I_10 = dict(DICT_ROMAN2INT)
for num_X in range(1, 4):
    for s, num in R2I_10.items():
        DICT_ROMAN2INT['X' * num_X + s] = 10 * num_X + num
for (prefix, value) in [('XL', 40), ('L', 50)]:
    DICT_ROMAN2INT.update(dict([(prefix + s, value + num) for s, num in R2I_10.items()]))
for num_X in range(1, 4):
    DICT_ROMAN2INT.update(dict([('L' + 'X' * num_X, 50 + 10 * num_X + num) for s, num in R2I_10.items()]))
del R2I_10
