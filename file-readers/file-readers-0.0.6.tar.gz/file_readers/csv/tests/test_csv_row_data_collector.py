from unittest import TestCase

from file_readers.csv.csv_row_data_collector import CSVRowDataCollector


class TestCSVRowDataCollector(TestCase):

    def test_collect_data(self):
        data_structure = [
            {'header': 'name', 'index': 0, 'type': str},
            {'header': 'age', 'index': 1, 'type': int},
            {'header': 'title', 'index': 2, 'type': str}
        ]
        collector = CSVRowDataCollector(data_structure_dict=data_structure)
        row = ['John', 24, 'Developer']
        collector.collect_data(row)
        data = collector.data[0]
        self.assertEqual(data['name'], 'John')
        self.assertEqual(data['age'], 24)
        self.assertEqual(data['title'], 'Developer')
