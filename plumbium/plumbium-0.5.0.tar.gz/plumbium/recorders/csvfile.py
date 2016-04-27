"""
plumbium.recorders.csvfile
**************************
"""

import os
import csv


class CSVFile(object):
    """Records results to a CSV file

    :param path: The file to which results should be written
    :type path: str
    :param values: a mapping from table columns to values
    :type values: dict
    """

    def __init__(self, path, values):
        self.path = path
        self.values = values

    def write(self, results):
        """Write results to the file specified

        .. note:: If the specified does not exist it will be created and a
            header will be written , otherwise the new result is appended.

        :param results: A dictionary of results to record
        :type results: dict
        """

        field_names = self.values.keys()
        write_header = not os.path.exists(self.path)
        with open(self.path, 'a') as output_file:
            writer = csv.DictWriter(output_file, fieldnames=field_names)
            if write_header:
                writer.writeheader()
            row = {}
            for field in self.values:
                row[field] = self.values[field](results)
            writer.writerow(row)
