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
from exportable.exporters.base import Exporter
from exportable.exporters.csv import CSVExporter
from exportable.exporters.pyexcel import ODSExporter, XLSXExporter, XLSExporter
from exportable.exporters.spss import SPSSExporter
from exportable.exporters.json import JSONExporter

DEFAULT_EXPORTERS = [
    JSONExporter,
    ODSExporter,
    XLSXExporter,
    XLSExporter,
    CSVExporter,
    SPSSExporter
]


def get_exporter_by_extension(extension):
    for exporter in DEFAULT_EXPORTERS:
        if exporter.extension == extension:
            return exporter
    raise ValueError("No exporter with extension {} in DEFAULT_EXPORTERS.".format(extension))