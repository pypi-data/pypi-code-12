from unittest import TestCase
import os
from file_readers.csv.csv_filereader import CSVFileReader
from file_readers.data_collector import BaseDataCollector

base_path = os.path.dirname(__file__)


class DummyDataCollector(BaseDataCollector):
    def __init__(self):
        self.data_structure = [
            {'header': 'name', 'index': 0, 'type': str},
            {'header': 'age', 'index': 1, 'type': int},
            {'header': 'title', 'index': 2, 'type': str}
        ]
        self.data = []

    def collect_data(self, source):
        values = {}
        for item in self.data_structure:
            header = item['header']
            index = item['index']
            values[header] = source[index]
        self.data.append(values)


def data_collector(data, row):
    values = {'name': row[0], 'age': int(row[1]), 'title': row[2]}
    data.append(values)


class TestCSVFileReader(TestCase):

    def test_read_file(self):
        test_file = base_path + "/data/test.csv"
        collector = DummyDataCollector()
        reader = CSVFileReader(data_collector=collector, delimiter=";")
        reader.read_file(test_file)
        row = collector.data[1]
        self.assertEqual(row['name'], 'John')
        self.assertEqual(int(row['age']), 24)
        self.assertEqual(row['title'], 'Developer')

    def test_read_data_from_file(self):
        test_file = base_path + "/data/test.csv"
        data = CSVFileReader.read_data_from_file(test_file, func=data_collector, header='Name', delimiter=";")
        row = data[0]
        self.assertEqual(row['name'], 'John')
        self.assertEqual(row['age'], 24)
        self.assertEqual(row['title'], 'Developer')
