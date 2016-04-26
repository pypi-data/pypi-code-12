from unittest import TestCase
import os
from file_readers.excel.excel_reader import ExcelReader
from file_readers.excel.excel_data_collector import ExcelDataCollector

base_path = os.path.dirname(__file__)


class TestExcelReader(TestCase):

    def test_get_sheet_names(self):
        test_file = base_path + "/data/test.xlsx"
        sheets = ExcelReader.get_sheet_names(test_file)
        self.assertEqual('Personnel', sheets[0])

    def test_read_file(self):
        test_file = base_path + "/data/test.xlsx"
        collector = ExcelDataCollector()
        reader = ExcelReader(data_collector=collector)
        reader.set_sheet_to_read("Personnel")
        reader.read_file(test_file)
        result_row = collector.data[0]
        self.assertEqual(result_row['Name'], 'John')
        self.assertEqual(result_row['Age'], 24)
        self.assertEqual(result_row['Title'], "Developer")
