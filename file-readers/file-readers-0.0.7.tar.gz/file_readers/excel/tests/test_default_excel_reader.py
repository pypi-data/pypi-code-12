from unittest import TestCase
import os
from file_readers.excel.default_excel_reader import DefaultExcelReader

base_path = os.path.dirname(__file__)


class TestDefaultExcelReader(TestCase):

    def test_get_sheet_names(self):
        test_file = base_path + "/data/test.xlsx"
        reader = DefaultExcelReader()
        sheets = reader.get_sheet_names(test_file)
        self.assertEqual('Personnel', sheets[0])

    def test_read_file(self):
        test_file = base_path + "/data/test.xlsx"
        reader = DefaultExcelReader()
        reader.set_sheet_to_read("Personnel")
        reader.read_file(test_file)
        result_row = reader.data[0]
        self.assertEqual(result_row['Name'], 'John')
        self.assertEqual(result_row['Age'], 24)
        self.assertEqual(result_row['Title'], "Developer")
