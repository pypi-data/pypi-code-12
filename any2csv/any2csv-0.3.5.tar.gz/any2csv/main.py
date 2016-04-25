# -*- encoding: utf-8 -*-
import logging
import csv
from csv import DictWriter
import shutil
import codecs
from pyjon.utils import get_secure_filename
import six
from any2.exceptions import Any2Error
from any2.exceptions import ColumnMappingError
from any2 import DictAdapter as CSVAddon

log = logging.getLogger(__name__)


class Any2CSVError(Any2Error):
    pass


class Any2Dialect(csv.Dialect, object):

    def __init__(
        self, delimiter, quoting, quotechar, lineterminator, escapechar,
        doublequote
    ):
        self.delimiter = delimiter
        self.quoting = quoting
        self.quotechar = quotechar
        self.lineterminator = lineterminator
        self.doublequote = doublequote
        self.escapechar = escapechar
        super(Any2Dialect, self).__init__()


class Any2CSV(object):

    def __init__(
            self, target_filename, column_mappings,
            encoding='UTF-8',
            delimiter=';',
            quoting=csv.QUOTE_ALL,
            quotechar='"',
            doublequote=False,
            escapechar='\\',
            lineterminator='\n',
            show_first_line=False,
            addbom=False,
    ):
        """Initialize the Any2CSV.

        :param target_filename: The target csv file name
        :type target_filename: String

        :param column_mappings: Mapping to use
        :type column_mappings: list of dictionary with keys :
            - attr
            - colname
            - renderer (callback function or string)

            The renderer callback must accept one argument the object,
            the result must be unicode type

        :param encoding: The encoding to use to write the final csv file
        :type encoding:String

        :param delimiter: The delimiter to use to separate each field on
        the final csv file, default delimiter is ";"
        :type delimiter: String

        :param quoting: The quoting policy for the CSV writer, default is
        csv.QUOTE_ALL
        :type quoting: one of csv.QUOTE_*

        :param quotechar: The character to be used as a quote, default='"'
        :type quotechar: string

        :param doublequote: Controls if the quote character should be
        doubled if it is found inside the data, default=False
        :type doublequote: Boolean

        :param escapechar: The character to be used as an escape if the
        quotechar is used in the data and the double quote is note active,
        default='\\'
        :type escapechar: string

        :param lineterminator: The line terminator to use in our CSV dialect
        :type lineterminator: binary string

        :param show_first_line: Show the csv header with all column names,
        default is False
        :type show_first_line: Boolean
        """
        self.encoding = encoding
        self.target_filename = target_filename
        self.column_mappings = column_mappings
        self.check_column_mappings()
        self.delimiter = delimiter
        self.doublequote = doublequote
        self.escapechar = escapechar
        self.show_first_line = show_first_line

        self.__tmp_filename = get_secure_filename()
        if six.PY2:
            self.__tmp_file = open(self.__tmp_filename, 'wb+')

        elif six.PY3:
            self.__tmp_file = codecs.open(
                self.__tmp_filename,
                'wb+',
                self.encoding
            )
        if addbom:
            # Excel needs this to open UTF-8 files properly
            self.__tmp_file.write(u'\ufeff'.encode('utf8'))

        csv.register_dialect(
            'any2csv_dialect',
            Any2Dialect(
                delimiter, quoting, quotechar, lineterminator,
                escapechar, doublequote
            ),
        )

        self.csvengine = DictWriter(
            self.__tmp_file,
            self.__get_column_names(),
            dialect='any2csv_dialect'
        )

    def check_column_mappings(self):
        attr = None
        renderer = None
        colname = None

        for column_mapping in self.column_mappings:
            attr = column_mapping.get('attr', None)
            renderer = column_mapping.get('renderer', None)
            colname = column_mapping.get('colname', None)

        if colname is None:
            raise ColumnMappingError(
                'The colname is mandatory on the column mapping'
            )

        if renderer is not None:
            if not (
                isinstance(renderer, six.string_types) or callable(renderer)
            ):
                msg = "Renderer definition error from the column_mapping,"
                msg += " renderer must be only string/unicode or "
                msg += "callable, not %s" % type(renderer)

                raise ColumnMappingError(msg)

        if renderer is None and attr is None:
            msg = 'On the column mapping definition,'
            msg += ' you must define at least attr or renderer'
            raise ColumnMappingError(msg)

        if attr is None and callable(renderer):
            msg = 'You cannot use a callable renderer if attr is not defined.'
            raise ColumnMappingError(msg)

    def __get_column_attributes(self):
        return [col_def['attr'] for col_def in self.column_mappings]

    def __get_column_names(self):
        return [col_def['colname'] for col_def in self.column_mappings]

    def __write_firstrow(self):
        firstrow = dict()
        for colname in self.__get_column_names():
            firstrow[colname] = colname
        self.csvengine.writerow(firstrow)

    def encode(self, row):
        """
        This method is a special helper to transform all text types (unicode
        in python2 and str in python3) to binary types (str in python2 and
        bytes in python3) to allow writing in a CSV.

        This should normally only be used by python2 code because in Python3
        the CSV writer supports unicode and this is the preferred way of doing

        :param row: the row that will be passed to CSV writer
        :return: a new encoded row
        """
        res = {}
        for k, v in row.items():
            if isinstance(v, six.text_type):
                newv = v.encode(self.encoding)
            else:
                # we don't encode non unicode objects (ie: int, bool, ...)
                newv = v

            res[k] = newv

        return res

    def write(self, data_generator):
        if self.show_first_line:
            self.__write_firstrow()

        for data in data_generator:
            if isinstance(data, dict):
                adapted_data = data
            else:
                adapted_data = CSVAddon(
                    data,
                    self.column_mappings,
                )

            if six.PY2:
                # encode before writing
                adapted_data = self.encode(adapted_data)

            self.csvengine.writerow(adapted_data)

        self.__tmp_file.close()
        self.__write_target_file(self.__tmp_filename)

    def __write_target_file(self, temp_filename):
        shutil.move(temp_filename, self.target_filename)
