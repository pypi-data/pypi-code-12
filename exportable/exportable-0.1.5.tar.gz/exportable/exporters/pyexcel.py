###########################################################################
#          (C) Vrije Universiteit, Amsterdam (the Netherlands)            #
#                                                                         #
# This file is part of AmCAT - The Amsterdam Content Analysis Toolkit     #
#                                                                         #
# AmCAT is free software: you can redistribute it and/or modify it under  #
# the terms of the GNU Affero General Public License as published by the  #
# Free Software Foundation, either version 3 of the License, or (at your  #
# option) any later version.                                              #
#                                                                         #
# AmCAT is distributed in the hope that it will be useful, but WITHOUT    #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or   #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public     #
# License for more details.                                               #
#                                                                         #
# You should have received a copy of the GNU Affero General Public        #
# License along with AmCAT.  If not, see <http://www.gnu.org/licenses/>.  #
###########################################################################
import itertools
import pyexcel

from exportable.exporters.base import Exporter


class PyExcelExporter(Exporter):
    def dump(self, table, fo, filename_hint=None, encoding_hint="utf-8"):
        colnames = [col.verbose_name for col in table.columns]
        sheet1 = itertools.chain([colnames], table.rows)
        book = pyexcel.Book(sheets={"Sheet 1": sheet1})
        self.dump_book(book, fo, encoding_hint=encoding_hint)

    def dump_book(self, book: pyexcel.Book, fo, encoding_hint="utf-8"):
        book.save_to_memory(self.extension, fo)


class ODSExporter(PyExcelExporter):
    extension = "ods"
    content_type = "application/vnd.oasis.opendocument.spreadsheet"
    compressable = False


class XLSExporter(PyExcelExporter):
    extension = "xls"
    content_type = "application/vnd.ms-excel"
    compressable = False


class XLSXExporter(PyExcelExporter):
    extension = "xlsx"
    content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    compressable = False


#class CSVExporter(PyExcelExporter):
#    extension = "csv"
#    content_type = "text/csv"
