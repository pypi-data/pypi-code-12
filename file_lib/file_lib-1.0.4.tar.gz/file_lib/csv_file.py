# -*- coding: utf-8 -*-
import os
import csv
import codecs
import unicodecsv


def convert_unicode_to_str(target, encode):
    if isinstance(target, unicode):
        return target.encode(encode)
    return target


class CsvFileReader(object):
    def __init__(self, file_path, encode='utf-8', quote='"', delimiter=',', line_feed='\r\n', skip_initial_space=False):
        delimiter = convert_unicode_to_str(delimiter, encode)
        quote = convert_unicode_to_str(quote, encode)
        self.__file_path = file_path
        self.__encode = encode
        self.__arg_dict = {'delimiter': delimiter,
                           'lineterminator': line_feed,
                           'skipinitialspace': skip_initial_space}
        if quote:
            self.__arg_dict['quotechar'] = quote
            self.__arg_dict['quoting'] = csv.QUOTE_ALL

    def read_file(self):
        list_file = codecs.open(self.__file_path, 'r')
        reader = unicodecsv.reader(list_file, encoding=self.__encode, **self.__arg_dict)
        for line in reader:
            yield line
        list_file.close()


class CsvFileWriter(object):
    def __init__(self, file_path, encode='utf-8', quote='"', delimiter=',', line_feed='\r\n', skip_initial_space=False,
                 ignore=True):
        delimiter = convert_unicode_to_str(delimiter, encode)
        quote = convert_unicode_to_str(quote, encode)
        self.__file_path = file_path
        self.__encode = encode
        self.__arg_dict = {'delimiter': delimiter,
                           'lineterminator': line_feed,
                           'skipinitialspace': skip_initial_space}
        if quote:
            self.__arg_dict['quotechar'] = quote
            self.__arg_dict['quoting'] = csv.QUOTE_ALL
        self.__write_file_obj = self.__create_file_obj()
        self.__writer = unicodecsv.writer(self.__write_file_obj, encoding=self.__encode, **self.__arg_dict)
        self.__ignore = ignore

    def write_file(self, fetch_data):
        for line_data in fetch_data:
            self.write_one_line(line_data)
        self.__write_file_obj.close()

    def __create_file_obj(self):
        if os.path.isdir(os.path.dirname(self.__file_path)) is False:
            os.makedirs(os.path.dirname(self.__file_path))
        return codecs.open(self.__file_path, 'wb')

    def write_one_line(self, data):
        tmp = map(lambda n: self.__check_data(n), data)
        self.__writer.writerow(tmp)

    def __check_data(self, check_target):
        if self.__ignore is False:
            return check_target
        if isinstance(check_target, unicode):
            return check_target.encode(self.__encode, 'ignore').decode(self.__encode, 'ignore')
        if isinstance(check_target, str):
            return check_target.decode(self.__encode, 'ignore').encode(self.__encode, 'ignore')
        return check_target

    def close(self):
        self.__write_file_obj.close()
