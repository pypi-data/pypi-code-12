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
import datetime
import json
import unittest

from exportable import columns
from exportable.table import ListTable


class TestJSONExporter(unittest.TestCase):
    def test_dump(self):
        test_date_1 = datetime.datetime(2020, 9, 8, 12, 11, 10)
        test_date_2 = datetime.datetime(2015, 7, 6)
        test_date_3 = datetime.datetime(2010, 5, 4)

        unicode_with_none_data = iter([
            [None,  test_date_1, 1.0,  "\u265d"],
            [74321, None,        3.0,  "\u265c"],
            [4,     test_date_2, None, "\u2704"],
            [5,     test_date_3, 0,     None]
        ])

        table = ListTable(rows=unicode_with_none_data, columns=[
            columns.IntColumn("a"),
            columns.DateTimeColumn("b"),
            columns.FloatColumn("c"),
            columns.TextColumn("d"),
        ])

        data = json.loads(table.dumps("json").decode())

        expected_data = [
            {'d': '♝', 'b': '2020-09-08T12:11:10', 'c': 1.0, 'a': None},
            {'d': '♜', 'b': None, 'c': 3.0, 'a': 74321},
            {'d': '✄', 'b': '2015-07-06T00:00:00', 'c': None, 'a': 4},
            {'d': None, 'b': '2010-05-04T00:00:00', 'c': 0, 'a': 5}
        ]

        self.assertEqual(data, expected_data)
