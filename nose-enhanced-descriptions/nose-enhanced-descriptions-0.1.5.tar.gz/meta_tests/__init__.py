"""
Tests used to produce output for the real tests.

These tests are not tests of the system, rather, this file is to be considered
as test data.
"""
import unittest


class MetaTest(unittest.TestCase):
    def test_with_docstring(self):
        """I have a docstring
        The first line will be used in the description
        """
        pass

    def test_docstring_leading_line(self):
        """
        The first line was empty, but this is the line to use.
        """
        pass

    def test_without_docstring(self):
        pass

    def test_with_blank_docstring(self):
        """

        """
        pass

    def test_fail(self):
        """I have a docstring and I fail"""
        self.fail()

    def test_error(self):
        """I have a docstring and I raise"""
        raise Exception
