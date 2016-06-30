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

class TestRPMs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mr = modulemd.ModuleRPMs()

    def test_add_package(self):
        self.mr.packages = dict()
        self.mr.add_package("Add")
        self.assertEqual(self.mr.packages, { "Add" : { "rationale" : "" } } )

    def test_add_package_with_rationale(self):
        self.mr.packages = dict()
        self.mr.add_package("AddWithRationale", rationale="rationalestr")
        self.assertEqual(self.mr.packages,
            { "AddWithRationale" : { "rationale" : "rationalestr" } } )

    def test_add_package_with_arches(self):
        self.mr.packages = dict()
        self.mr.add_package("AddWithArches", arches=["x", "y", "z"])
        self.assertEqual(self.mr.packages,
            { "AddWithArches" : { "rationale" : "", "arches" : ["x", "y", "z"] } } )

    def test_add_package_with_multilib(self):
        self.mr.packages = dict()
        self.mr.add_package("AddWithMultilib", multilib=["x", "y", "z"])
        self.assertEqual(self.mr.packages,
            { "AddWithMultilib" : { "rationale" : "", "multilib" : ["x", "y", "z"] } } )

    def test_add_package_with_commit(self):
        self.mr.packages = dict()
        self.mr.add_package("AddWithCommit", commit="commitstr")
        self.assertEqual(self.mr.packages,
            { "AddWithCommit" : { "rationale" : "", "commit" : "commitstr"} } )

    def test_add_package_with_repository(self):
        self.mr.packages = dict()
        self.mr.add_package("AddWithRepository", repository="repostr")
        self.assertEqual(self.mr.packages,
            { "AddWithRepository" : { "rationale" : "", "repository" : "repostr" } } )

    def test_add_package_with_cache(self):
        self.mr.packages = dict()
        self.mr.add_package("AddWithCache", cache="cachestr")
        self.assertEqual(self.mr.packages,
            { "AddWithCache" : { "rationale" : "", "cache" : "cachestr" } } )

    def test_del_package(self):
        self.mr.packages = { "Del" : None }
        self.mr.del_package("Del")
        self.assertEqual(self.mr.packages, dict())

    def test_clear_packages(self):
        self.mr.packages = { "Clear" : None }
        self.mr.clear_packages()
        self.assertEqual(self.mr.packages, dict())

    def test_dependencies(self):
        self.mr.dependencies = False
        self.assertFalse(self.mr.dependencies)
        self.mr.dependencies = True
        self.assertTrue(self.mr.dependencies)

    def test_dependencies_default(self):
        default = modulemd.ModuleRPMs()
        self.assertFalse(default.dependencies)

    def test_add_api(self):
        self.assertNotIn("AddRPMAPI", self.mr.api)
        self.mr.add_api("AddRPMAPI")
        self.assertIn("AddRPMAPI", self.mr.api)

    def test_del_api(self):
        self.mr.api = set(["DelRPMAPI"])
        self.mr.del_api("DelRPMAPI")
        self.assertNotIn("DelRPMAPI", self.mr.api)

    def test_clear_api(self):
        self.mr.api = set(["ClearRPMAPI"])
        self.mr.clear_api()
        self.assertEqual(self.mr.api, set([]))

    def test_add_filter(self):
        self.assertNotIn("AddRPMAPI", self.mr.filter)
        self.mr.add_filter("AddRPMAPI")
        self.assertIn("AddRPMAPI", self.mr.filter)

    def test_del_filter(self):
        self.mr.filter = set(["DelRPMAPI"])
        self.mr.del_filter("DelRPMAPI")
        self.assertNotIn("DelRPMAPI", self.mr.filter)

    def test_clear_filter(self):
        self.mr.filter = set(["ClearRPMAPI"])
        self.mr.clear_filter()
        self.assertEqual(self.mr.filter, set([]))

if __name__ == "__main__":
    unittest.main()
