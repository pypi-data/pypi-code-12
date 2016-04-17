# Author:  mozman -- <mozman@gmx.at>
# Purpose: test body, region, solid3d
# Created: 03.05.2014
# Copyright (C) 2014, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import unittest
from io import StringIO

from ezdxf.lldxf.classifiedtags import ClassifiedTags
from ezdxf.tools.binarydata import compress_binary_data, CompressedTags, binary_encoded_data_to_bytes


class TestCompressBinaryData(unittest.TestCase):
    def test_one_short_binary_chunk(self):
        tags = ClassifiedTags.from_text(BIN_ONE_SHORT)
        compress_binary_data(tags)
        ole2frame = tags.get_subclass('AcDbOle2Frame')
        compressed_tag = ole2frame[-1]  # last tag
        self.assertTrue(isinstance(compressed_tag, CompressedTags))
        self.assertEqual(310, compressed_tag.code)
        self.assertEqual(len(ole2frame), 10)

    def test_one_long_binary_chunk(self):
        tags = ClassifiedTags.from_text(BIN_ONE_LONG)
        ole2frame = tags.get_subclass('AcDbOle2Frame')
        uncompressed_length = sum(len(tag.value) for tag in ole2frame if tag.code == 310)
        compress_binary_data(tags)
        compressed_tag = ole2frame[-1]  # last tag
        self.assertTrue(isinstance(compressed_tag, CompressedTags))
        compressed_length = len(compressed_tag.value._data)
        self.assertEqual(310, compressed_tag.code)
        self.assertEqual(len(ole2frame), 10)
        self.assertTrue(uncompressed_length/compressed_length > 4)  # ratio > 1:4

    def test_two_short_binary_chunks(self):
        tags = ClassifiedTags.from_text(BIN_TWO_SHORT)
        compress_binary_data(tags)
        ole2frame = tags.get_subclass('AcDbOle2Frame')
        compressed_tag_310 = ole2frame[-2]
        compressed_tag_311 = ole2frame[-1]
        self.assertTrue(isinstance(compressed_tag_310, CompressedTags))
        self.assertTrue(isinstance(compressed_tag_311, CompressedTags))
        self.assertEqual(310, compressed_tag_310.code)
        self.assertEqual(311, compressed_tag_311.code)
        self.assertEqual(len(ole2frame), 11)

    def test_four_binary_chunks(self):
        tags = ClassifiedTags.from_text(BIN_FOUR)
        compress_binary_data(tags)
        ole2frame = tags.get_subclass('AcDbOle2Frame')
        compressed_tag_310 = ole2frame[-4]
        compressed_tag_311 = ole2frame[-3]
        compressed_tag_310_2 = ole2frame[-2]
        compressed_tag_312 = ole2frame[-1]
        self.assertTrue(isinstance(compressed_tag_310, CompressedTags))
        self.assertTrue(isinstance(compressed_tag_311, CompressedTags))
        self.assertTrue(isinstance(compressed_tag_310_2, CompressedTags))
        self.assertTrue(isinstance(compressed_tag_312, CompressedTags))
        self.assertEqual(310, compressed_tag_310.code)
        self.assertEqual(311, compressed_tag_311.code)
        self.assertEqual(310, compressed_tag_310_2.code)
        self.assertEqual(312, compressed_tag_312.code)
        self.assertEqual(len(ole2frame), 13)

    def test_write_four_binary_chunks(self):
        tags = ClassifiedTags.from_text(BIN_FOUR)
        compress_binary_data(tags)
        stream = StringIO()
        tags.write(stream)
        result = stream.getvalue()
        stream.close()
        result_lines = [line.strip() for line in result.splitlines()]
        bin_four_lines = [line.strip() for line in BIN_FOUR.splitlines()]
        self.assertEqual(bin_four_lines, result_lines)

    def test_binary_encoded_data_to_bytes_1(self):
        result = binary_encoded_data_to_bytes(['FFFF'])
        self.assertEqual(b"\xff\xff", result)

    def test_binary_encoded_data_to_bytes_2(self):
        result = binary_encoded_data_to_bytes(['F0F0', '1A1C'])
        self.assertEqual(b"\xF0\xF0\x1A\x1C", result)

BIN_ONE_SHORT = """  0
OLE2FRAME
  5
21C
330
1F
100
AcDbEntity
  8
0
100
AcDbOle2Frame
 70
     2
  3
Microsoft Office Excel-Arbeitsblatt
 10
1757.922
 20
1740.495
 30
0.0
 11
1821.671954614981
 21
1688.014230748349
 31
0.0
 71
     2
 72
     0
 73
     2
 90
    32896
310
8055E846590CB1779B40985EBC2DFB319B400000000000000000F8DEDE14B076
"""

BIN_TWO_SHORT = """  0
OLE2FRAME
  5
21C
330
1F
100
AcDbEntity
  8
0
100
AcDbOle2Frame
 70
     2
  3
Microsoft Office Excel-Arbeitsblatt
 10
1757.922898669198
 20
1740.495291655801
 30
0.0
 11
1821.671954614981
 21
1688.014230748349
 31
0.0
 71
     2
 72
     0
 73
     2
 90
    32896
310
8055E846590CB1779B40985EBC2DFB319B400000000000000000F8DEDE14B076
311
8055E846590CB1779B40985EBC2DFB319B400000000000000000F8DEDE14B076"""

BIN_ONE_LONG = """  0
OLE2FRAME
  5
21C
330
1F
100
AcDbEntity
  8
0
100
AcDbOle2Frame
 70
     2
  3
Microsoft Office Excel-Arbeitsblatt
 10
1757.922898669198
 20
1740.495291655801
 30
0.0
 11
1821.671954614981
 21
1688.014230748349
 31
0.0
 71
     2
 72
     0
 73
     2
 90
    32896
310
8055E846590CB1779B40985EBC2DFB319B400000000000000000F8DEDE14B076
310
9C40985EBC2DFB319B400000000000000000F8DEDE14B0769C40085B81920E60
310
9A400000000000000000E846590CB1779B40085B81920E609A40000000000000
310
0000E818AC140100000000010000010000000100000000000100000000800000
310
D0CF11E0A1B11AE1000000000000000000000000000000003E000300FEFF0900
310
0600000000000000000000000100000001000000000000000010000002000000
310
01000000FEFFFFFF0000000000000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
310
FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
310
FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
310
FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
310
FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
310
FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
310
FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
310
FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
310
FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
310
FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
310
FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
310
FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
310
FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
310
FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
310
FDFFFFFF21000000FEFFFFFFFEFFFFFF05000000060000000700000008000000
310
090000000A0000000B0000000C0000000D0000000E0000000F00000010000000
310
1100000012000000130000001400000015000000160000001700000018000000
310
190000001A0000001B0000001C0000001D0000001E0000001F00000020000000"""

BIN_FOUR = """  0
OLE2FRAME
  5
21C
330
1F
100
AcDbEntity
  8
0
100
AcDbOle2Frame
 70
     2
  3
Microsoft Office Excel-Arbeitsblatt
 10
1757.922
 20
1740.495
 30
0.0
 11
1821.671
 21
1688.014
 31
0.0
 71
     2
 72
     0
 73
     2
 90
    32896
310
8055E846590CB1779B40985EBC2DFB319B400000000000000000F8DEDE14B076
310
9C40985EBC2DFB319B400000000000000000F8DEDE14B0769C40085B81920E60
310
9A400000000000000000E846590CB1779B40085B81920E609A40000000000000
310
0000E818AC140100000000010000010000000100000000000100000000800000
310
D0CF11E0A1B11AE1000000000000000000000000000000003E000300FEFF0900
310
0600000000000000000000000100000001000000000000000010000002000000
310
01000000FEFFFFFF0000000000000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
310
FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
310
FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
310
FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
311
FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
311
FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
311
FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
311
FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
311
FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
311
FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
310
FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
310
FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
310
FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
310
FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
310
FDFFFFFF21000000FEFFFFFFFEFFFFFF05000000060000000700000008000000
310
090000000A0000000B0000000C0000000D0000000E0000000F00000010000000
310
1100000012000000130000001400000015000000160000001700000018000000
312
190000001A0000001B0000001C0000001D0000001E0000001F00000020000000"""

if __name__ == '__main__':
    unittest.main()
