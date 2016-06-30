#/usr/bin/python3
# -*- coding: utf-8 -*-


# Copyright (c) 2016  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Petr Šabata <contyk@redhat.com>

import unittest

import os
import sys

DIR = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(DIR, ".."))

import modulemd

class TestLicenses(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mmd = modulemd.ModuleMetadata()

    def test_add_module_license(self):
        self.assertNotIn("AddModuleLicense", self.mmd.module_licenses)
        self.mmd.add_module_license("AddModuleLicense")
        self.assertIn("AddModuleLicense", self.mmd.module_licenses)

    def test_del_module_license(self):
        self.mmd.module_licenses = set(["DelModuleLicense"])
        self.mmd.del_module_license("DelModuleLicense")
        self.assertNotIn("DelModuleLicense", self.mmd.module_licenses)

    def test_clear_module_licenses(self):
        self.mmd.module_licenses = set(["ClearModuleLicenses"])
        self.mmd.clear_module_licenses()
        self.assertEqual(self.mmd.module_licenses, set([]))

    def test_add_content_license(self):
        self.assertNotIn("AddContentLicense", self.mmd.content_licenses)
        self.mmd.add_content_license("AddContentLicense")
        self.assertIn("AddContentLicense", self.mmd.content_licenses)

    def test_del_content_license(self):
        self.mmd.content_licenses = set(["DelContentLicense"])
        self.mmd.del_content_license("DelContentLicense")
        self.assertNotIn("DelContentLicense", self.mmd.content_licenses)

    def test_clear_content_licenses(self):
        self.mmd.content_licenses = set(["ClearContentLicenses"])
        self.mmd.clear_content_licenses()
        self.assertEqual(self.mmd.content_licenses, set([]))

if __name__ == "__main__":
    unittest.main()
