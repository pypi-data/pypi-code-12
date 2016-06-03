import os

import numpy as np
import pytest

from atrcopy import DefaultSegment, SegmentData, get_xex


class TestDiff(object):
    def test1(self):
        d = np.arange(4096, dtype=np.uint8)
        r = SegmentData(d)
        s1 = DefaultSegment(r, 0)
        d = np.arange(4096, dtype=np.uint8)
        d[10:20] = 0
        d[100] = 0xfe
        d[101] = 0xfe
        d[102] = 0xfe
        d[104] = 0xfe
        d[400:405] = 2
        r = SegmentData(d)
        s2 = DefaultSegment(r, 0)
        
        s1.compare_segment(s2)
        ranges = s1.get_style_ranges(diff=True)
        print ranges
        assert ranges[0] == (10, 20)
        assert ranges[1] == (100, 103)
        assert ranges[2] == (104, 105)
        assert ranges[3] == (400, 405)


if __name__ == "__main__":
    t = TestDiff()
    t.test1()
