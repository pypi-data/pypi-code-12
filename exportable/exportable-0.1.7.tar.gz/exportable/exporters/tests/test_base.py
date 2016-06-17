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
import io
import unittest

from exportable.exporters.base import Exporter
from exportable.table import ListTable


class RandomExporter(Exporter):
    def __init__(self, n):
        self.n = n

    def dump(self, table, fo, filename_hint=None, encoding_hint="utf-8"):
        for i in map(str, range(self.n)):
            fo.write(i.encode(encoding_hint))


class ErrorExporter(Exporter):
    def dump(self, table, fo, filename_hint=None, encoding_hint="utf-8"):
        fo.write(b"OK")
        raise ValueError("Woops.")


class TestBaseExporter(unittest.TestCase):
    def test_randomised(self):
        """Methods such as dump_iter use threads. We test their implementation by running it
        through thousands of randomised values in order to detect threading issues."""
        table = ListTable(rows=[], columns=[])
        re = RandomExporter(n=1000)

        # Test dump()
        buffer = io.BytesIO()
        re.dump(table, buffer)
        expected = "".join(map(str, range(1000))).encode()
        self.assertEqual(expected, buffer.getvalue())

        # Test dump_iter()
        for i, enc in enumerate(re.dump_iter(table)):
            self.assertEqual(str(i).encode(), enc)
        self.assertEqual(1000, sum(1 for _ in re.dump_iter(table)))

    def test_error_handling_dump_iter(self):
        """Are error messages correctly surfaced?"""
        table = ListTable(rows=[], columns=[])
        seq = ErrorExporter().dump_iter(table)
        self.assertRaises(ValueError, list, seq)
