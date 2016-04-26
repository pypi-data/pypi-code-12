from file_readers.data_collector import BaseDataCollector


class CSVRowDataCollector(BaseDataCollector):

    def __init__(self, data_structure_dict, header=None):
        """The constructor takes the data sources structure as parameter.

        Args:
            data_structure_dict: The structure of the data source to collect.
                Example structure:
                    data_structure = [
                        {'header': 'name', 'index': 0, 'type': str},
                        {'header': 'age', 'index': 1, 'type': int},
                        {'header': 'title', 'index': 2, 'type': str}
                    ]
            header: The header of the first column.
        """
        self.data_structure = data_structure_dict
        self.header = header
        self.data = []

    def collect_data(self, source):
        """Collects the data from a row data source.

        The data source must be a list containing the data.
        """
        if self.header and self.header in source[0]:  # This header check might be misleading
            return
        values = {}
        for item in self.data_structure:
            header = item['header']
            index = item['index']
            values[header] = source[index]

        self.data.append(values)
