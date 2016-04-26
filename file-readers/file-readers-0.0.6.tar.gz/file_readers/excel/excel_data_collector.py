from file_readers.data_collector import BaseDataCollector
from openpyxl.cell import column_index_from_string


class ExcelDataCollector(BaseDataCollector):

    def __init__(self, debug=False):
        self.debug = debug
        self.data = []
        self.headers = []

    def collect_data(self, source):
        """Collects all data from a sheet

        Args:
            source: A list or tuple of Cell objects
        """

        row = {}
        for cell_object in source:
            if "1" in cell_object.coordinate:
                self.headers.append(cell_object.value)
                continue

            index = column_index_from_string(cell_object.coordinate[0]) - 1
            header = self.headers[index]
            row[header] = cell_object.value
        if self.debug:
            print(row)
        if row:
            self.data.append(row)
