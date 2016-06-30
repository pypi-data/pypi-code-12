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

class TestValidate(unittest.TestCase):
    def setUp(self):
        self.mmd = modulemd.ModuleMetadata()
        self.mmd.load("tests/test.yaml")

    def test_validate_mdversion(self):
        self.mmd._mdversion = None
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_name1(self):
        self.mmd._name = None
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_name2(self):
        self.mmd.name = ""
        self.assertRaises(ValueError, self.mmd.validate)

    def test_validate_version1(self):
        self.mmd._version = None
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_version2(self):
        self.mmd.version = ""
        self.assertRaises(ValueError, self.mmd.validate)

    def test_validate_release1(self):
        self.mmd._release = None
        self.assertRaises(TypeError, self.mmd.validate)
    
    def test_validate_release2(self):
        self.mmd._release = ""
        self.assertRaises(ValueError, self.mmd.validate)

    def test_validate_summary1(self):
        self.mmd._summary = None
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_summary2(self):
        self.mmd.summary = ""
        self.assertRaises(ValueError, self.mmd.validate)

    def test_validate_description1(self):
        self.mmd._description = None
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_description2(self):
        self.mmd.description = ""
        self.assertRaises(ValueError, self.mmd.validate)

    def test_validate_module_licenses1(self):
        self.mmd._module_licenses = None
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_module_licenses2(self):
        self.mmd._module_licenses = set([1, 2, 3])
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_module_licenses3(self):
        self.mmd.clear_module_licenses()
        self.assertRaises(ValueError, self.mmd.validate)

    def test_validate_content_licenses1(self):
        self.mmd._content_licenses = None
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_content_licenses2(self):
        self.mmd._content_licenses = set([1, 2, 3])
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_requires1(self):
        self.mmd._requires = None
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_requires2(self):
        self.mmd._requires = { "foo" : 1 }
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_requires3(self):
        self.mmd._requires = { 1 : "foo" }
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_requires4(self):
        self.mmd._requires = { 1 : 2 }
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_community(self):
        self.mmd._community = None
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_documentation(self):
        self.mmd._documentation = None
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_tracker(self):
        self.mmd._tracker = None
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_xmd(self):
        self.mmd._xmd = 1
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_profiles1(self):
        self.mmd._profiles = 1
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_profiles2(self):
        self.mmd.profiles = { 1 : modulemd.ModuleProfile() }
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_profiles3(self):
        self.mmd.profiles = { "foo" : 1 }
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_profiles4(self):
        self.mmd.profiles = { "foo" : modulemd.ModuleProfile() }
        self.mmd.profiles["foo"]._rpms = 1
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_profiles5(self):
        self.mmd.profiles = { "foo" : modulemd.ModuleProfile() }
        self.mmd.profiles["foo"]._rpms = set([1, 2, 3])
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_components(self):
        self.mmd._components = None
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_rpms(self):
        self.mmd.components._rpms = 1
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_rpms_dependencies(self):
        self.mmd.components.rpms._dependencies = 1
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_rpms_packages1(self):
        self.mmd.components.rpms._packages = 1
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_rpms_packages2(self):
        self.mmd.components.rpms._packages = { "foo" : 1 }
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_rpms_packages3(self):
        self.mmd.components.rpms._packages = { "foo" : dict() }
        self.assertRaises(ValueError, self.mmd.validate)

    def test_validate_rpms_packages4(self):
        self.mmd.components.rpms._packages = { 1 : None }
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_rpms_packages5(self):
        self.mmd.components.rpms._packages = { "foo" : { "rationale" : "", 1 : None } }
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_rpms_packages6(self):
        self.mmd.components.rpms._packages = { "foo" : { "rationale": "", "arches" : 1 } }
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_rpms_packages7(self):
        self.mmd.components.rpms._packages = { "foo" : { "rationale" : "", "arches" : [1, 2, 3] } }
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_rpms_packages8(self):
        self.mmd.components.rpms._packages = { "foo" : { "rationale" : "", "multilib" : 1 } }
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_rpms_packages9(self):
        self.mmd.components.rpms._packages = { "foo" : { "rationale" : "", "multilib" : [1, 2, 3] } }
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_rpms_packages10(self):
        self.mmd.components.rpms._packages = { "foo" : { "rationale" : "", "commit" : 1 } }
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_rpms_packages11(self):
        self.mmd.components.rpms._packages = { "foo" : { "rationale" : "", "repository" : 1 } }
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_rpms_packages12(self):
        self.mmd.components.rpms._packages = { "foo" : { "rationale" : "", "cache" : 1 } }
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_rpms_api1(self):
        self.mmd.components.rpms._api = None
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_rpms_api2(self):
        self.mmd.components.rpms._api = 42
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_rpms_api3(self):
        self.mmd.components.rpms._api = "foo"
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_rpms_api4(self):
        self.mmd.components.rpms._api = [ "foo", "bar" ]
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_rpms_api5(self):
        self.mmd.components.rpms._api = { "foo", 1 }
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_rpms_filter1(self):
        self.mmd.components.rpms._filter = None
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_rpms_filter2(self):
        self.mmd.components.rpms._filter = 42
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_rpms_filter3(self):
        self.mmd.components.rpms._filter = "foo"
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_rpms_filter4(self):
        self.mmd.components.rpms._filter = [ "foo", "bar" ]
        self.assertRaises(TypeError, self.mmd.validate)

    def test_validate_rpms_filter5(self):
        self.mmd.components.rpms._filter = { "foo", 1 }
        self.assertRaises(TypeError, self.mmd.validate)

if __name__ == "__main__":
    unittest.main()
