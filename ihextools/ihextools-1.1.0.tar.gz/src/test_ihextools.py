import nose
from nose.tools import assert_equal
import unittest
import ihextools as ihex

class testiHex(unittest.TestCase):

    def test_low_offset(self):
        starting_offset = 0x08004000
        working_offset = starting_offset

        ih = ihex.iHex()
        ih.load_bin('test_collateral/main.bin', starting_offset)

        wl = ih.get_u32_list()

        for w in wl:
            assert_equal(w[0], working_offset)
            working_offset += 4

    def test_hi_offset(self):
        starting_offset = 0x08020000
        working_offset = starting_offset

        ih = ihex.iHex()
        ih.load_bin('test_collateral/main.bin', starting_offset)

        wl = ih.get_u32_list()

        for w in wl:
            assert_equal(w[0], working_offset)
            working_offset += 4

    def test_gcc_output(self):
        starting_offset = 0x08004000
        working_offset = starting_offset

        ih = ihex.iHex()
        gih = ihex.iHex()
        
        ih.load_bin('test_collateral/main.bin', starting_offset)
        gih.load_ihex('test_collateral/main.hex')

        wl = ih.get_u32_list()
        wl2 = gih.get_u32_list()

        for idx in range(len(wl)):
            assert_equal(wl[idx][0], wl2[idx][0])
