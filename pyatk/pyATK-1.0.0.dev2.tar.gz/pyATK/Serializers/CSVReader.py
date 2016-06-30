#!/usr/bin/python3
# -*- coding: utf-8 -*-

import csv
import pyATK.Filesystem.Encoding as en
import pyATK.Filesystem.Utils as fs


class CSVReader:
    """
    >>> f = open('tst.txt', 'w')
    >>> chars = f.write("header1,header2,header3\\n")
    >>> chars = f.write("field1,field2,field3")
    >>> f.close()
    >>> reader = CSVReader('tst.txt')
    >>> reader.load()
    [{0: 'field1', 1: 'field2', 2: 'field3'}]
    >>> reader = CSVReader('tst.txt', True)
    >>> data = reader.load()
    >>> import os
    >>> os.remove('tst.txt')
    """
    def __init__(self, file_path, first_row_as_header=False, ignore_emtpy_lines=True, separator=';'):
        self.file_path = fs.getAbsolutePath(file_path)
        self.first_row_as_header = first_row_as_header
        self.ignore_emtpy_lines = ignore_emtpy_lines
        self.separator = separator

    def _populate_row(self, data, headers):
        index = 0
        data_dictionary = {}
        for header in headers:
            data_dictionary[header] = data[index]
            index += 1
        return data_dictionary

    def load(self):
        content = []
        row_count = 0
        encoding = en.getEncoding(self.file_path)
        if encoding is None:
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


