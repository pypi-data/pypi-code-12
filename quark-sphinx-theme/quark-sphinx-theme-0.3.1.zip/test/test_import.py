# -*- coding: utf-8 -*-
# This file is part of quark-sphinx-theme.
# Copyright (c) 2016 Felix Krull <f_krull@gmx.de>
# Released under the terms of the BSD license; see LICENSE.

from unittest import TestCase


class TestModuleImport(TestCase):
    def assertImports(self, modname):  # noqa
        try:
            __import__(modname)
        except ImportError as exc:
            self.fail('failed to import \'%s\': %s' % (modname, exc))

    def test_main_package(self):
        self.assertImports('quark_sphinx_theme')

    def test_mixin(self):
        self.assertImports('quark_sphinx_theme._mixin')

    def test_ext(self):
        self.assertImports('quark_sphinx_theme.ext')

    def test_ext_html_rewrite(self):
        self.assertImports('quark_sphinx_theme.ext.html_rewrite')

    def test_ext_html_compat(self):
        self.assertImports('quark_sphinx_theme.ext.html_compat')
