import csv
from file_readers.file_reader import BaseFileReader
from file_readers.data_collector import BaseDataCollector


class CSVFileReader(BaseFileReader):

    def __init__(self, data_collector, delimiter, quotechar=None, debug=False):
        """
        Args:
            data_collector: A data collector which is a subclass of BaseDataCollector.
            delimiter: Delimiter to be used when reading the CSV file.
            quotechar:
            debug: If set to True, then each row is printed out to stdout.


        Raises:
            AttributeError: Provided data collector is not a subclass of BaseDataCollector.
        """
        if not isinstance(data_collector, BaseDataCollector):
            raise AttributeError('Provided data collector is not a subclass of BaseDataCollector!')
        self.data_collector = data_collector
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.debug = debug

    def read_file(self, filename):
        """Reads the given file and collects data from each row.

        Args:
            filename: name of the file to read, including the path.
        """
        with open(filename, 'r', newline='') as csv_file:
            if self.quotechar:
                reader = csv.reader(csv_file, delimiter=self.delimiter, quotechar=self.quotechar)
            else:
                reader = csv.reader(csv_file, delimiter=self.delimiter)
            for row in reader:
                if self.debug:
                    print(row)
                self.data_collector.collect_data(row)

    @staticmethod
    def read_data_from_file(filename, func, header=None, delimiter=' ', quotechar='|', debug=False):
        """Reads the given file and collects data from each row.

            Args:
                filename: name of the file to read, including the path.
                func: A function that collects the data into a list.
                header: The header of the first column. Default: None
                delimiter: Delimiter to be used when reading the CSV file.
                quotechar:
                debug: If set to True, then each row is printed out to stdout.

            Returns:
                A list with items added by func.
            """
        data = []
        with open(filename, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=delimiter, quotechar=quotechar)
            for row in reader:
                if debug:
                    print(row)
                if header and header in row[0]:
                    continue
                func(data, row)
        return data
