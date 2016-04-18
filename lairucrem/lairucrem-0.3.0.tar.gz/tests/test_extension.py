#! /usr/bin/env python
# Copyright (C) 2016 Alain Leufroy
#
# Author: Alain Leufroy <alain@leufroy.fr>
# Licence: WTFPL, grab your copy here: http://sam.zoy.org/wtfpl/
"""test the extension"""

from __future__ import unicode_literals, absolute_import

import os
import io
import sure
from lairucrem import get_extension_path
from .test_utils import temprepo


def test_graphlog():
    with temprepo() as repo:
        for i in range(2):
            repo.mkcset('foo', 'cset %i' % i)
        results = list(repo.debuglairucremgraphlog\
                       .bake(config='extensions.lairucrem=%s' % get_extension_path())\
                       .bake(config="ui.graphnodetemplate={lairucremgraphnode}")\
                       (template='{desc}', _iter='out'))
        results.must.equal([
            'o\n', # <- working
            '|\n',
            '@  cset 1\n',
            '|\n',
            'o  cset 0\n',
            '\n'
        ])


def test_templates():
    with temprepo() as repo:
        for i in range(2):
            repo.mkcset('foo', 'cset %i' % i)
        with io.open(os.path.join(repo._root, 'foo'), 'w', encoding='utf-8') as fid:
            fid.write('draft')
        results = list(repo.debuglairucremgraphlog\
                       .bake(config='extensions.lairucrem=%s' % get_extension_path())\
                       .bake(config="ui.graphnodetemplate={lairucremgraphnode}")\
                       (template='{lairucremid}\n'))
        len(results[0].strip()).should.equal(1) # just the graph node
