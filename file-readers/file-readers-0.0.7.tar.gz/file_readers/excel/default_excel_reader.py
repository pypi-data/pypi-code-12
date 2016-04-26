from file_readers.file_reader import BaseFileReader
from file_readers.excel.excel_data_collector import ExcelDataCollector
from file_readers.excel.excel_reader import ExcelReader


class DefaultExcelReader(BaseFileReader):
    """A excel file reader that uses the default
    excel data collector.
    """

    def __init__(self):
        self.data_collector = ExcelDataCollector()
        self.reader = ExcelReader(self.data_collector)
        self.data = []
        self.sheet_to_read = None

    def set_sheet_to_read(self, sheet_name):
        self.sheet_to_read = sheet_name

    def get_sheet_names(self, filename):
        return ExcelReader.get_sheet_names(filename)

    def read_file(self, filename):
        self.reader.set_sheet_to_read(self.sheet_to_read)
        self.reader.read_file(filename)
        self.data = self.data_collector.data

    def get_data(self):
        return self.data
