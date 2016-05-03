#!/usr/bin/python3
# -*- coding: utf-8 -*-

import csv
import pyATK.filesystem.Encoding as en
import pyATK.filesystem.Utils as fs


class CSVReader:
    def __init__(self, file_path, first_row_as_header=False, ignore_emtpy_lines=True, separator=';'):
        self.file_path = fs.get_absolute_path(file_path)
        self.first_row_as_header = first_row_as_header
        self.ignore_emtpy_lines = ignore_emtpy_lines
        self.separator = separator

    def _populate_row(self, data, headers):
        index = 0
        data_dictionary = {}
        for header in headers:
            data_dictionary[header] = data[index]
        return data_dictionary

    def load(self):
        content = []
        row_count = 0
        encoding = en.get_encoding(self.file_path)
        if encoding is None:
            print("Unable to detect file encoding. Using ASCII")
            encoding = 'us-ascii'
        file = open(self.file_path, encoding=encoding)
        reader = csv.reader(file, delimiter=self.separator)
        for row in reader:
            if row_count == 0:
                if self.first_row_as_header is True:
                    headers = row
                else:
                    headers = list(range(len(row)))
            else:
                if self.ignore_emtpy_lines is True and len(row) == 0:
                    row_count += 1
                    continue
                else:
                    if len(row) == 0:
                        row = len(headers) * ['']
                    content.append(self._populate_row(row, headers))

            row_count += 1

        file.close()
        return content


