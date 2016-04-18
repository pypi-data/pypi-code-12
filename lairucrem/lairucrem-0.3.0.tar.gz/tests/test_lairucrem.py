#! /usr/bin/env python
# Copyright (C) 2016 Alain Leufroy
#
# Author: Alain Leufroy <alain@leufroy.fr>
# Licence: WTFPL, grab your copy here: http://sam.zoy.org/wtfpl/
"""test lairucrem module"""


from __future__ import unicode_literals, absolute_import

import os
import lairucrem
from .test_utils import temprepo



def test_get_extension_path():
    root = os.path.dirname(os.path.abspath(lairucrem.__file__))
    expected = os.path.join(root, b'extension.py')
    lairucrem.get_extension_path().must.equal(expected)


def test_repository():
    with temprepo() as _repo:
        repo = lairucrem.repository(_repo._root)
        # check repository path
        str(repo.root()).strip().must.equal(_repo._root)
        # check environ
        'HGPLAIN'.must.be.within(repo._partial_call_args['env'])

