"""
unittests
"""

# we dont need database access for the existing tests ( for now )
# from django.test import TestCase
from unittest import TestCase
import GenSettingDict


class SettingTest(TestCase):

    def test_simple_getsetting(self):
        """
        Tests that getsetting works correct
        """

        a = GenSettingDict.GenSettingDict()

        a.addsetting("a", 1)

        self.assertEqual(a.getsetting("a"), 1)

    def test_nested_getsetting(self):
        """
        Tests that a nested getsetting works correct
        """

        a = GenSettingDict.GenSettingDict()

        a.addsetting("test.a.b.c", 1)

        self.assertEqual(a.getsetting("test.a.b.c"), 1)


    def test_simple_overlay(self):
        """
        Tests that overlay works correct
        """

        a = GenSettingDict.GenSettingDict()
        b = GenSettingDict.GenSettingDict()

        a.addsetting("test.a", 1)
        b.addsetting("test.b", 2)


        c = GenSettingDict.overlaysettings(a, b)

        self.assertEqual(c.getsetting("test.a"), 1)
        self.assertEqual(c.getsetting("test.b"), 2)

    def test_simple_overlay2(self):
        """
        Tests that overlay works correct, eg the value will be overlayed
        """

        a = GenSettingDict.GenSettingDict()
        b = GenSettingDict.GenSettingDict()

        a.addsetting("test.a", 1)
        b.addsetting("test.a", 2)

        c = GenSettingDict.overlaysettings(a, b)

        self.assertEqual(c.getsetting("test.a"), 2)

    def test_simple_overlay3(self):
        """
        Tests that overlay works correct
        """

        a = GenSettingDict.GenSettingDict()
        b = GenSettingDict.GenSettingDict()

        a.addsetting("test.a.a", 1)
        b.addsetting("test.b", 2)

        c = GenSettingDict.overlaysettings(a, b)

        self.assertEqual(c.getsetting("test.a.a"), 1)
        self.assertEqual(c.getsetting("test.b"), 2)

    def test_addsetting(self):
        """
        Tests that overlay works correct
        """

        a = GenSettingDict.GenSettingDict()

        a.addsetting("test.a.a", 1)
        a.addsetting("test.b", 2)

        self.assertEqual(a.getsetting("test.a.a"), 1)
        self.assertEqual(a.getsetting("test.b"), 2)