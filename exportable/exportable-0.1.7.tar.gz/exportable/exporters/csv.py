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
import csv

from exportable.exporters.base import Exporter


class CSVExporter(Exporter):
    extension = "csv"
    content_type = "text/csv"

    def __init__(self, dialect="excel", **fmtparams):
        self.dialect = dialect
        self.fmtparams = fmtparams

    def dump(self, table, fo, filename_hint=None, encoding_hint="utf-8"):
        csvf = csv.writer(fo, dialect=self.dialect, **self.fmtparams)
        csvf.writerow([c.label for c in table.column])
        for row in table.rows:
            csvf.writerow([column.to_str(value) for column, value in zip(row, table.columns)])
