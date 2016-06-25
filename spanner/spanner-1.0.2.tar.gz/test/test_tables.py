import os
import unittest

from spanner import tables


test_file = os.path.join(os.path.dirname(__file__), 'flatfile_test_file.txt')


class TablesTestCase(unittest.TestCase):

    def test_rows_cols(self):
        with open(test_file, 'r') as fh:
            nrows = len(fh.readlines()) - 1

        for rownum, cols in enumerate(tables.row_iterator(test_file)):
            self.assertTrue(len(cols) == 2)

        self.assertTrue(rownum + 1 == nrows)

    def test_dict(self):
        key_cols = ['key']
        val_cols = ['value']
        map = tables.load_dict(test_file, key_cols, val_cols)
        for key in map:
            if 'redundant' not in key:
                self.assertTrue(len(map[key]) == len(val_cols))
                self.assertTrue(len(map[key]) == 1)
            else:
                self.assertTrue(len(map[key]) > 1)

        self.assertTrue(len(map.keys()) == 3)
