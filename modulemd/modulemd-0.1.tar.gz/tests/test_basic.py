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

class TestBasic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mmd = modulemd.ModuleMetadata()
        cls.mmd.name = "test"
        cls.mmd.version = "42"
        cls.mmd.release = "1"
        cls.mmd.summary = "A test module"
        cls.mmd.description = "It's only used for testing purposes."
        cls.mmd.module_licenses = set([ "MIT" ])
        cls.mmd.content_licenses = set([ "ISC" ])
        cls.mmd.buildrequires = { "builddepenency" : "123-456" }
        cls.mmd.requires = { "dependency" : "1.00-1" }
        cls.mmd.community = "http://www.example.com/community"
        cls.mmd.documentation = "http://www.example.com/documentation"
        cls.mmd.tracker = "http://www.example.com/tracker"
        cls.mmd.xmd = { "key" : "value" }
        cls.mmd.profiles = { "default" : modulemd.ModuleProfile() }
        cls.mmd.profiles["default"].rpms = set([ "prof", "ile" ])
        cls.mmd.components = modulemd.ModuleComponents()
        cls.mmd.components.rpms = modulemd.ModuleRPMs()
        cls.mmd.components.rpms.dependencies = True
        cls.mmd.components.rpms.api = set([ "api" ])
        cls.mmd.components.rpms.packages = { "rpm" : { "rationale" : "" } }
        cls.mmd.components.rpms.filter = set([ "filter_1", "filter_2" ])

    def test_mdversion(self):
        self.assertIn(self.mmd.mdversion, modulemd.supported_mdversions)

    def test_name(self):
        self.assertEqual(self.mmd.name, "test")

    def test_version(self):
        self.assertEqual(self.mmd.version, "42")

    def test_release(self):
        self.assertEqual(self.mmd.release, "1")

    def test_summary(self):
        self.assertEqual(self.mmd.summary, "A test module")

    def test_description(self):
        self.assertEqual(self.mmd.description, "It's only used for testing purposes.")

    def test_module_licenses(self):
        self.assertEqual(self.mmd.module_licenses, set(["MIT"]))

    def test_content_licenses(self):
        self.assertEqual(self.mmd.content_licenses, set(["ISC"]))

    def test_buildrequires(self):
        self.assertEqual(self.mmd.buildrequires, {"builddepenency" : "123-456"})

    def test_requires(self):
        self.assertEqual(self.mmd.requires, {"dependency" : "1.00-1"})

    def test_community(self):
        self.assertEqual(self.mmd.community, "http://www.example.com/community")

    def test_documentation(self):
        self.assertEqual(self.mmd.documentation, "http://www.example.com/documentation")

    def test_tracker(self):
        self.assertEqual(self.mmd.tracker, "http://www.example.com/tracker")

    def test_xmd(self):
        self.assertEqual(self.mmd.xmd, { "key" : "value" })

    def test_profiles(self):
        self.assertEqual(list(self.mmd.profiles.keys()), ["default"])

    def test_profiles_rpms(self):
        self.assertEqual(self.mmd.profiles["default"].rpms, set(["prof", "ile"]))

    def test_components(self):
        self.assertIsInstance(self.mmd.components, modulemd.ModuleComponents)

    def test_rpms(self):
        self.assertIsInstance(self.mmd.components.rpms, modulemd.ModuleRPMs)

    def test_rpm_dependencies(self):
        self.assertTrue(self.mmd.components.rpms.dependencies)

    def test_rpm_api(self):
        self.assertEqual(self.mmd.components.rpms.api, set(["api"]))

    def test_rpm_packages(self):
        self.assertEqual(self.mmd.components.rpms.packages, { "rpm" : { "rationale" : "" } })

    def test_rpm_filter(self):
        self.assertEqual(self.mmd.components.rpms.filter, set([ "filter_1", "filter_2" ]))

if __name__ == "__main__":
    unittest.main()
