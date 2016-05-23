# -*- coding: utf-8 -*-
# This file is part of quark-sphinx-theme.
# Copyright (c) 2016 Felix Krull <f_krull@gmx.de>
# Released under the terms of the BSD license; see LICENSE.

import os
from unittest import TestCase

import quark_sphinx_theme


class TestGetPath(TestCase):
    def test_get_path(self):
        p = quark_sphinx_theme.get_path()
        self.assertTrue(os.path.isdir(p))
        conf = os.path.join(p, 'quark', 'theme.conf')
        self.assertTrue(os.path.isfile(conf))
