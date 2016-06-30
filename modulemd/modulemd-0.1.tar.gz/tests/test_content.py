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

class TestContent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mc = modulemd.ModuleContent()

    def test_add_package(self):
        self.mc.packages = dict()
        self.mc.add_package("Add")
        self.assertEqual(self.mc.packages, { "Add" : { "rationale" : "" } } )

    def test_add_package_with_rationale(self):
        self.mc.packages = dict()
        self.mc.add_package("AddWithRationale", "rationalestr")
        self.assertEqual(self.mc.packages,
            { "AddWithRationale" : { "rationale" : "rationalestr" } } )

    def test_del_package(self):
        self.mc.packages = { "Del" : None }
        self.mc.del_package("Del")
        self.assertEqual(self.mc.packages, dict())

    def test_clear_packages(self):
        self.mc.packages = { "Clear" : None }
        self.mc.clear_packages()
        self.assertEqual(self.mc.packages, dict())

if __name__ == "__main__":
    unittest.main()
