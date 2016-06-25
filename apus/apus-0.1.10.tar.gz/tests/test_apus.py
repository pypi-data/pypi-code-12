#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_apus
----------------------------------

Tests for `apus` module.
"""

import pytest

from contextlib import contextmanager
from click.testing import CliRunner

from apus import apus
from apus import cli


class TestApus(object):

    @classmethod
    def setup_class(cls):
        pass

    def test_something(self):
        pass
    def test_command_line_interface(self):
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'apus.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output

    @classmethod
    def teardown_class(cls):
        pass

