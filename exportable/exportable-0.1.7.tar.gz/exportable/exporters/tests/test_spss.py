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
import os
import string
import tempfile
import time
import datetime
import unittest

import subprocess

from exportable.columns import IntColumn, DateTimeColumn, TextColumn, FloatColumn
from exportable.exporters import SPSSExporter
from exportable.exporters.spss import write_table
from exportable.table import ListTable

class Timer:
    def __enter__(self):
        self.start = time.clock()
        return self

    def __exit__(self, *args):
        self.end = time.clock()
        self.interval = self.end - self.start


class TestSPSSExporter(unittest.TestCase):
    def setUp(self):
        test_date_1 = datetime.datetime(2020, 9, 8)
        test_date_2 = datetime.datetime(2015, 7, 6)
        test_date_3 = datetime.datetime(2010, 5, 4)

        self.ascii_data = [
            [1,     test_date_1, 1.0, "test '  abc"],
            [74321, test_date_2, 3.0, "abc\n this is a really string"*100],
            [4,     test_date_3, 4.0, "asdf \""],
        ]

        self.unicode_data = [
            [1,     test_date_1, 1.0, "\u265d"],
            [74321, test_date_2, 3.0, "\u265c"],
            [4,     test_date_3, 4.0, "\u2704"],
            [5,     test_date_1, 5.0, "\u2704"],
        ]

        self.unicode_with_none_data = [
            [None,  test_date_1, 1.0,  "\u265d"],
            [74321, None,        3.0,  "\u265c"],
            [4,     test_date_3, None, "\u2704"],
            [5,     test_date_1, 5.0,  None]
        ]

        self.ascii_table = ListTable(
            columns=[
                IntColumn("a1"),
                DateTimeColumn("a2"),
                FloatColumn("a3"),
                TextColumn("a4")
            ],
            rows=self.ascii_data
        )

        self.unicode_table = ListTable(
            columns=[
                IntColumn("a1\u26f1"),
                DateTimeColumn("a2\u26fd"),
                FloatColumn("a3"),
                TextColumn("a4")
            ],
            rows=self.unicode_data
        )

        self.unicode_with_none_table = ListTable(
            columns=[
                IntColumn("a1\u26f1"),
                DateTimeColumn("a2\u26fd"),
                FloatColumn("a3"),
                TextColumn("a4")
            ],
            rows=self.unicode_with_none_data
        )

    def test_simple_table(self):
        table = ListTable(
            columns=[
                IntColumn("a1"),
                IntColumn("a2"),
                TextColumn("a3"),
                TextColumn("a4")
            ],
            rows=[
                [1, 2, "ab", "cd"],
                [2, 3, "ef", "gh"],
            ]
        )

        write_table(table, open("/dev/null", "wb"))


    def test_unicode_with_nones(self):
        _, file = tempfile.mkstemp()
        write_table(self.unicode_with_none_table, open(file, "wb"))

        pspp = subprocess.Popen(
            ["pspp", "-b"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        input = b"get file='" + file.encode("utf-8") + b"'.\nlist.\nshow n.\n"
        stdout, stderr = pspp.communicate(input=input, timeout=30)
        self.assertIn(b"N is 4.", stdout)

        os.unlink(file)


    def test_asciitable2sav(self):
        _, file = tempfile.mkstemp()
        write_table(self.ascii_table, open(file, "wb"))

        pspp = subprocess.Popen(
            ["pspp", "-b"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        input = b"get file='" + file.encode("utf-8") + b"'.\nlist.\nshow n.\n"
        stdout, stderr = pspp.communicate(input=input, timeout=30)
        self.assertIn(b"N is 3.", stdout)
        self.assertIn(b"74321", stdout)
        # Testing dates isn't really possible due to strange formatting due to long lines..
        os.unlink(file)

    def test_unitable2sav(self):
        _, file = tempfile.mkstemp()
        write_table(self.unicode_table, open(file, "wb"))

        pspp = subprocess.Popen(
            ["pspp", "-b"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        input = b"get file='" + file.encode("utf-8") + b"'.\nlist.\nshow n.\n"
        stdout, stderr = pspp.communicate(input=input, timeout=30)
        self.assertIn(b"N is 4.", stdout)
        self.assertIn(b"08-SEP-2020 00:00:00", stdout)
        self.assertIn(b"06-JUL-2015 00:00:00", stdout)
        self.assertIn(b"04-MAY-2010 00:00:00", stdout)
        self.assertIn(b"74321", stdout)
        self.assertIn("♜".encode("utf-8"), stdout)
        self.assertIn("♝".encode("utf-8"), stdout)
        self.assertIn("✄".encode("utf-8"), stdout)

        os.unlink(file)


    def test_compressed_writer(self):
        # Create a big file to test compression
        rows = [
            [1, 2, 3, datetime.datetime.now(), ((string.ascii_lowercase)*2)]
            for _ in range(3000)
        ]

        table1 = ListTable(size_hint=3000, rows=rows, columns=[
                IntColumn("a"), IntColumn("b"),
                IntColumn("c"), DateTimeColumn("d"),
                TextColumn("e")
            ]
        )

        table2 = ListTable(size_hint=3000, rows=rows, columns=[
                IntColumn("a"), IntColumn("b"),
                IntColumn("c"), DateTimeColumn("d"),
                TextColumn("e")
            ]
        )

        exporter = SPSSExporter()

        # Export with compression
        response = exporter.dump_http_reponse(table1, filename="test", compress=True, compress_level=1)
        compressed_content = b"".join(response.streaming_content)

        # Export without
        response = exporter.dump_http_reponse(table2, filename="test", compress=False)
        uncompressed_content = b"".join(response.streaming_content)

        # The compress ratio should be very large due to the large number of filling bytes in SPSS
        compress_ratio = len(uncompressed_content) / len(compressed_content)
        self.assertGreaterEqual(compress_ratio, 100)


