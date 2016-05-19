# -*- coding: utf-8 -*-

import os
import unittest

from ..opencsp import OpenCSPOutput


class TestOpenCSPOutput(unittest.TestCase):

    def setUp(self):
        here = os.path.dirname(os.path.abspath(__file__))
        filepah = os.path.join(here, "opencsp_output.csv")
        self.fixture = OpenCSPOutput(filepah)

    def tearDown(self):
        del self.fixture

    def test_read_from_csv(self):
        self.assertIsNotNone(self.fixture)

    def test_original_column_names(self):
        column_names = [
            'frame',
            'blob index',
            'x',
            'y',
            'head x',
            'head y',
            'tail x',
            'tail y',
            'is_merged'
        ]
        original_column_names = self.fixture.raw_data.columns.tolist()
        self.assertEqual(column_names, original_column_names)

    def test_remove_useless_columns(self):
        self.fixture.remove_unnecessary_columns()
        self.assertEquals(
            self.fixture.raw_data.columns.tolist(),
            ['frame',
             'blob index',
             'x',
             'y',
             'head x',
             'head y',
             'tail x',
             'tail y',
             'is_merged']
        )

    def test_remove_all_columns(self):
        all_columns = self.fixture.raw_data.columns.tolist()
        self.fixture.remove_unnecessary_columns(all_columns)
        self.assertEquals(self.fixture.raw_data.columns.tolist(), [])

    def test_remove_spaces_in_column_names(self):
        self.fixture.remove_unnecessary_columns()
        column_names = self.fixture.raw_data.columns.tolist()
        self.assertFalse(" " in column_names[0])  # 'frame'
        self.assertTrue(" " in column_names[-2])  # 'tail y'
        self.fixture.fix_column_names()
        fixed_column_names = self.fixture.raw_data.columns.tolist()
        self.assertFalse(" " in fixed_column_names[0])  # 'frame'
        self.assertFalse(" " in fixed_column_names[-1])  # 'tail_y'
        self.assertTrue("_" in fixed_column_names[-1])  # 'tail_y'

    def test_split_by_gender(self):
        self.assertIsNone(self.fixture.female)
        self.assertIsNone(self.fixture.male)
        self.fixture.split_by_gender('blob index')
        self.assertIsNotNone(self.fixture.female)
        self.assertIsNotNone(self.fixture.male)

    def test_split_by_gender_with_wrong_indexes(self):
        self.assertRaises(
            ValueError, self.fixture.split_by_gender, 'blob index', fbi=2)
        self.assertRaises(
            ValueError, self.fixture.split_by_gender, 'blob index', mbi=2)

    def test_split_by_gender_removes_blobindex_column(self):
        self.assertIn('blob index', self.fixture.raw_data.columns)
        self.fixture.split_by_gender('blob index')
        self.assertNotIn('blob index', self.fixture.female.columns)
        self.assertNotIn('blob index', self.fixture.male.columns)

    def test_split_by_gender_removes_fixed_blobindex_column(self):
        self.fixture.fix_column_names()
        self.assertIn('blob_index', self.fixture.raw_data.columns)
        self.fixture.split_by_gender('blob_index')
        self.assertNotIn('blob index', self.fixture.female.columns)
        self.assertNotIn('blob index', self.fixture.male.columns)
