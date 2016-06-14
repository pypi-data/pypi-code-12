"""Tests for the act._resources.

While this tests things in the act._resources module all tests are via
the public API.

"""

import pathlib
import sys

import pytest

import act


class TestFsloc:

    @pytest.mark.parametrize('attr',
                             ['prefix',
                              'bindir',
                              'sbindir',
                              'sysconfdir',
                              'statedir',
                              'libdir',
                              'datadir',
                              'infodir',
                              'mandir'])
    def test_type(self, attr):
        item = getattr(act.fsloc, attr)
        assert isinstance(item, pathlib.Path)

    def test_prefix(self):
        assert str(act.fsloc.prefix) == sys.prefix

    @pytest.mark.parametrize('attr',
                             ['bindir',
                              'sbindir',
                              'sysconfdir',
                              'statedir',
                              'libdir',
                              'datadir',
                              'infodir',
                              'mandir'])
    def test_root(self, attr):
        item = getattr(act.fsloc, attr)
        assert str(item).startswith(str(act.fsloc.prefix))
