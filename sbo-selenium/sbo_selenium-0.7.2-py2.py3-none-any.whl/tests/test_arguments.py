from __future__ import unicode_literals

import sys

from django.utils.six import StringIO

from django.test import TestCase

from sbo_selenium.management.commands.selenium import Command


class TestArguments(TestCase):
    """
    Test cases for the command line arguments of the selenium management
    command.
    """

    def test_base_arguments(self):
        """ The "selenium" management command should inherit the base test command's arguments """
        self._assert_in_help('--liveserver')

    def test_extra_arguments(self):
        """ The "selenium" management command should have its own custom arguments """
        self._assert_in_help('--browser-version')

    def _assert_in_help(self, text):
        """Assert that the selenium command's help output includes the given text"""
        output = StringIO()
        real_stdout = sys.stdout
        try:
            sys.stdout = output
            command = Command()
            command.print_help('manage.py', 'selenium')
        finally:
            sys.stdout = real_stdout
        self.assertIn(text, output.getvalue())
