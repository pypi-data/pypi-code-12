#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_reqgen
----------------------------------

Tests for `reqgen` module.
"""

from os import path, remove
from reqgen import reqgen
import requirements
from unittest2 import TestCase


class TestReqgen(TestCase):

    def setUp(self):
        self.high = requirements.parse('package==0.4')
        self.low = requirements.parse('package==0.1')

    def test_gt_gt(self):
        self.assertTrue(reqgen.gt(next(self.high), next(self.low)))

    def test_gt_lt(self):
        self.assertFalse(reqgen.gt(next(self.low), next(self.high)))

    def test_gt_nov(self):
        self.assertFalse(reqgen.gt(next(self.low), next(self.high)))

    def test_gt_vc(self):
        self.high = requirements.parse('git+https://github.com/author/package@master#egg=package')
        self.assertFalse(reqgen.gt(next(self.low), next(self.high)))


class TestLoadDeps(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.expected_indexes = ['DUMMY', 'FOO', 'BAR', 'BAZ']
        cls.deps = reqgen.load_deps(
            path.join(path.dirname(__file__),
                      'files',
                      'samplefolder',
                      'requirements.txt')
        )

    def test_return_type(self):
        """ The method should return a dict """
        self.assertIsInstance(self.deps, dict)

    def test_keys(self):
        """ The dict indexes must match the expected
        (if you change the reqs files, remember to change here too)
        """
        self.assertItemsEqual(self.expected_indexes, self.deps.keys())


class TestMergeRqs(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.expected_values = [
            ('DUMMY', '0.2'),
            ('FOO', ''),
            ('BAR', '0.3'),
            ('BAZ', '')]
        cls.deps1 = reqgen.load_deps(
            path.join(
                path.dirname(__file__),
                'files',
                'requirements.txt')
        )
        cls.deps2 = reqgen.load_deps(
            path.join(
                path.dirname(__file__),
                'files',
                'samplefolder',
                'requirements.txt')
        )
        cls.merged = reqgen.merge_requirements(cls.deps1, cls.deps2)

    def test_merge_deps(self):
        self.assertItemsEqual([dep[0] for dep in self.expected_values], self.merged.keys())

    def test_versions(self):
        self.assertItemsEqual(
            [dep[1] for dep in self.expected_values],
            [req.specs[0][1] if len(req.specs) >= 1 else '' for req in self.merged.values()])


class TestSaveRequirements(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.full_requirements = 'full_requirements.txt'
        cls.reqs = path.join(path.dirname(__file__), 'files', 'requirements.txt')

    def _load_lines(self, file_name):
        with open(file_name, 'r') as text:
            lines = text.readlines()
        return lines

    def test_savefile(self):
        reqgen.save_requirements(
            self.reqs,
            self.full_requirements)
        lines_expected = self._load_lines(self.reqs)
        lines = self._load_lines(self.full_requirements)
        self.assertItemsEqual(lines_expected, lines)

    @classmethod
    def tearDownClass(cls):
        remove(cls.full_requirements)


class TestSearch(TestCase):

    def test_search_files(self):
        expected_files = [
            'tests/files/requirements.txt',
            'tests/files/samplefolder/requirements.txt'
        ]
        files = reqgen.search_reqs_files('tests')
        self.assertItemsEqual(expected_files, files)

# class TestMergedFile(TestCase):
#
#     def test_merge_file(self):
