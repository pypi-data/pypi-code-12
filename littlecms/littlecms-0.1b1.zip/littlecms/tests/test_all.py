
import unittest
import doctest

from littlecms import *

# Define a helper function to set a fixed datetime in profiles to allow the tests
# to compare Profile IDs with a reference.
def set_fixed_datetime(Lab_profile):
    default_datetime = cmsDateTimeNumber()
    default_datetime.year = 2016
    default_datetime.month = 1
    default_datetime.day = 1
    default_datetime.hours = 0
    default_datetime.minutes = 0
    default_datetime.seconds = 0
    set_datetime(Lab_profile, default_datetime)


class littlecms_tests(unittest.TestCase):
    def test_01_definitions(self):
        """Confirm a random selection of definitions"""
        self.assertEqual(cmsSigCurveType, int.from_bytes(b'curv', byteorder='big'))
        self.assertEqual(cmsSigMultiProcessElementType, int.from_bytes(b'mpet', byteorder='big'))

        self.assertEqual(cmsSigCopyrightTag, int.from_bytes(b'cprt', byteorder='big'))
        self.assertEqual(cmsSigMediaWhitePointTag, int.from_bytes(b'wtpt', byteorder='big'))

        self.assertEqual(cmsSigAToB1Tag, int.from_bytes(b'A2B1', byteorder='big'))
        self.assertEqual(cmsSigBToA2Tag, int.from_bytes(b'B2A2', byteorder='big'))

        self.assertEqual(cmsSigLabData, int.from_bytes(b'Lab ', byteorder='big'))
        self.assertEqual(cmsSigCmykData, int.from_bytes(b'CMYK', byteorder='big'))

        self.assertEqual(cmsSigDisplayClass, int.from_bytes(b'mntr', byteorder='big'))
        self.assertEqual(cmsSigAbstractClass, int.from_bytes(b'abst', byteorder='big'))

        self.assertEqual(cmsSigCLutElemType, int.from_bytes(b'clut', byteorder='big'))
        self.assertEqual(cmsSigLabV4toV2, int.from_bytes(b'4 2 ', byteorder='big'))

        self.assertEqual(cmsSigStatusT, int.from_bytes(b'StaT', byteorder='big'))
        self.assertEqual(cmsMatte, 2)

    def test_02_Lab_profile(self):
        """Create a default Lab profile"""
        white = cmsD50_xyY()    # Set white point for D50
        Lab_profile = cmsCreateLab4Profile(white)
        devclass = cmsGetDeviceClass(Lab_profile)
        set_fixed_datetime(Lab_profile)
        cmsMD5computeID(Lab_profile)
        id = cmsGetHeaderProfileID(Lab_profile)
        cmsCloseProfile(Lab_profile)

        ref_id_win = (175, 43, 95, 93, 111, 109, 219, 189, 185, 239, 195, 123, 184, 171, 20, 151)
        ref_id_linux = (75, 11, 238, 124, 137, 35, 87, 88, 15, 43, 42, 7, 28, 215, 191, 128)
        self.assertEqual(devclass, cmsSigAbstractClass)
        self.assertIn(id, [ref_id_win, ref_id_linux])

    def test_03_sRGB_profile(self):
        """Create a default sRGB profile"""
        sRGB_profile = cmsCreate_sRGBProfile()
        devclass = cmsGetDeviceClass(sRGB_profile)
        set_fixed_datetime(sRGB_profile)
        cmsMD5computeID(sRGB_profile)
        id = cmsGetHeaderProfileID(sRGB_profile)
        cmsCloseProfile(sRGB_profile)

        ref_id_win = (212, 202, 237, 197, 244, 183, 129, 89, 190, 157, 56, 110, 20, 241, 74, 85)
        ref_id_linux = (145, 166, 91, 73, 138, 125, 48, 157, 89, 122, 19, 227, 11, 32, 132, 161)
        self.assertEqual(devclass, cmsSigDisplayClass)
        self.assertIn(id, [ref_id_win, ref_id_linux])

    def test_04_triples(self):
        """Create and convert between some colour triples"""
        D50 = cmsD50_XYZ()
        xyY = cmsCIExyY()
        cmsXYZ2xyY(xyY, D50)

        XYZ = cmsCIEXYZ()
        Lab = cmsCIELab()
        XYZ.X, XYZ.Y, XYZ.Z = 0.3, 0.5, 0.8
        cmsXYZ2Lab(D50, Lab, XYZ)

        encoded_Lab = uint16Array(3)
        cmsFloat2LabEncoded(encoded_Lab, Lab)

        ref_xyY = (0.345702914918791, 0.3585385966799326, 1.0)
        ref_Lab = (76.06926101415557, -58.04143830964814, -39.226935058654576)
        ref_encoded_Lab_tuple = (49852, 17979, 22815)
        xyY_tuple = (xyY.x, xyY.y, xyY.Y)
        Lab_tuple = (Lab.L, Lab.a, Lab.b)
        encoded_Lab_tuple = (encoded_Lab[0], encoded_Lab[1], encoded_Lab[2])
        for i in range(3):
            self.assertAlmostEqual(xyY_tuple[i], ref_xyY[i], places = 14)
            self.assertAlmostEqual(Lab_tuple[i], ref_Lab[i], places = 14)
        self.assertTupleEqual(encoded_Lab_tuple, ref_encoded_Lab_tuple)

    def test_05_transform_rgb_Lab(self):
        """RGB->Lab transforms"""
        ctxt = cmsCreateContext(None, None)

        white = cmsD50_xyY()    # Set white point for D50
        Lab_profile = cmsCreateLab4Profile(white)
        sRGB_profile = cmsCreate_sRGBProfile()
        transform = cmsCreateTransform(sRGB_profile, TYPE_RGB_16, Lab_profile, TYPE_Lab_16,
                                      INTENT_RELATIVE_COLORIMETRIC, cmsFLAGS_NOCACHE)

        # colour in & out data
        n_pixels = 10
        in_comps = 3
        out_comps = 3
        rgb_float = (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,
                     0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,
                     0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)
        rgb_in = uint16Array(in_comps * n_pixels)
        Lab_out = uint16Array(out_comps * n_pixels)
        for i in range(in_comps * n_pixels):
            rgb_in[i] = int(rgb_float[i] * 65535)

        # Transform the sRGB values to Lab
        cmsDoTransform(transform, rgb_in, Lab_out, n_pixels)

        ref_Lab = (5443, 32641, 27728, 27479, 31752, 28400, 46832, 31673, 28769, 32100,
                   52118, 47286, 20533, 31858, 28226, 40583, 31681, 28666, 56976, 26492,
                   54427, 13242, 32108, 28018, 34146, 31702, 28545, 52923, 31672, 28860)
        Lab_tuple = tuple(Lab_out[i] for i in range(out_comps * n_pixels))
        self.assertEqual(Lab_tuple, ref_Lab)

    def test_06_transform_rgb_cmyk(self):
        """RGB->CMYK transforms"""
        ctxt = cmsCreateContext(None, None)

        white = cmsD50_xyY()    # Set white point for D50
        cmyk_profile = cmsOpenProfileFromFile('littlecms/tests/data/simple_cmyk_profile.icc', 'r')
        sRGB_profile = cmsCreate_sRGBProfile()
        transform = cmsCreateTransform(sRGB_profile, TYPE_RGB_16, cmyk_profile, TYPE_CMYK_16,
                                      INTENT_RELATIVE_COLORIMETRIC, cmsFLAGS_NOCACHE)

        # colour in & out data
        n_pixels = 10
        in_comps = 3
        out_comps = 4
        rgb_float = (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,
                     0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,
                     0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)
        rgb_in = uint16Array(in_comps * n_pixels)
        cmyk_out = uint16Array(out_comps * n_pixels)
        for i in range(in_comps * n_pixels):
            rgb_in[i] = int(rgb_float[i] * 65535)

        # Transform the sRGB values to cmyk
        cmsDoTransform(transform, rgb_in, cmyk_out, n_pixels)

        ref_cmyk = (60519, 57235, 36888, 47208, 51351, 37794, 21587, 12308, 26185, 14308,
                    6907, 1500, 1546, 61808, 63027, 0, 58454, 46012, 26023, 21517, 34245,
                    21095, 11419, 3307, 8665, 62, 64669, 0, 62645, 53830,
                    31540, 33555, 42752, 28925, 16360, 6857, 18880, 8849, 4116, 500)
        cmyk_tuple = tuple(cmyk_out[i] for i in range(out_comps * n_pixels))
        self.assertEqual(cmyk_tuple, ref_cmyk)

    def test_07_sampler(self):
        """Create a 6-colour CMYKOG profile using a sampler to populate the CLUTs"""
        from littlecms.tests import n_colour_profile
        ctxt, prof = n_colour_profile.setup()
        n_colour_profile.create_profile(ctxt, prof, False)
        set_fixed_datetime(prof)
        cmsMD5computeID(prof)
        id = cmsGetHeaderProfileID(prof)
        n_colour_profile.teardown(ctxt, prof)

        ref_id_win = (95, 72, 188, 94, 197, 198, 62, 13, 212, 240, 132, 105, 198, 245, 144, 229)
        ref_id_linux = (233, 106, 18, 189, 174, 87, 152, 206, 84, 251, 112, 178, 238, 164, 63, 66)
        self.assertIn(id, [ref_id_win, ref_id_linux])

    def test_08_pipelines(self):
        """Replace and remove pipelines and stages within pipelines"""
        from littlecms.tests import reduce_profile_size
        from littlecms.tests import n_colour_profile

        # We're going to reduce the CMYKOG profile from the sampler test
        ctxt, prof = n_colour_profile.setup()
        n_colour_profile.create_profile(ctxt, prof, False)

        reduce_profile_size.reduce_profile(ctxt, prof, False)
        set_fixed_datetime(prof)
        cmsMD5computeID(prof)
        id = cmsGetHeaderProfileID(prof)

        # No need to teardown reduce_profile_size because we didn't call setup
        n_colour_profile.teardown(ctxt, prof)

        ref_id_win = (210, 67, 128, 67, 189, 160, 116, 215, 39, 156, 177, 252, 217, 73, 42, 229)
        ref_id_linux = (197, 139, 110, 161, 143, 195, 75, 235, 4, 97, 2, 152, 3, 240, 109, 228)
        self.assertIn(id, [ref_id_win, ref_id_linux])

    def test_09_transform_cmyk_cmykog(self):
        """CMYK->CMYKOG transforms"""
        from littlecms.tests import n_colour_profile
        ctxt, cmykog_profile = n_colour_profile.setup()
        n_colour_profile.create_profile(ctxt, cmykog_profile, False)
        cmyk_profile = cmsOpenProfileFromFile('littlecms/tests/data/simple_cmyk_profile.icc', 'r')
        transform = cmsCreateTransform(cmyk_profile, TYPE_CMYK_16, cmykog_profile, TYPE_CMYK6_16,
                                      INTENT_RELATIVE_COLORIMETRIC, cmsFLAGS_NOCACHE)

        # colour in & out data
        n_pixels = 10
        in_comps = 4
        out_comps = 6
        cmyk_float = (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0,
                      0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0,
                      0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0,
                      0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6)
        cmyk_in = uint16Array(in_comps * n_pixels)
        cmykog_out = uint16Array(out_comps * n_pixels)
        for i in range(in_comps * n_pixels):
            cmyk_in[i] = int(cmyk_float[i] * 65535)

        # Transform the nominal sRGB values to cmykog
        cmsDoTransform(transform, cmyk_in, cmykog_out, n_pixels)

        ref_cmykog = (8632, 11804, 14020, 8469, 1645, 0, 22843, 24632, 25621, 22606,
                      981, 0, 19948, 25403, 24396, 19848, 2764, 0, 13118, 16203,
                      18266, 12961, 1599, 0, 25081, 26199, 26918, 24799, 663, 0,
                      31551, 35557, 15028, 15028, 0, 0, 16977, 19874, 21188, 16786,
                      1519, 3, 26747, 27744, 27687, 26432, 615, 0, 57254, 18917,
                      8281, 8281, 0, 0, 20171, 22596, 23548, 19960, 1290, 0)
        cmykog_tuple = tuple(cmykog_out[i] for i in range(out_comps * n_pixels))
        self.assertEqual(cmykog_tuple, ref_cmykog)

class swig_workaround_tests(unittest.TestCase):
    def test_uint64Array(self):
        """uint64 arrays"""
        a = uint64Array(3)
        for i in range(3):
            a[i] = i

        a_tuple = tuple(a[i] for i in range(3))
        self.assertEqual((0, 1, 2), a_tuple)

    def test_carray_len(self):
        """Len of C arrays"""
        a = uint64Array(3)

        self.assertEqual(len(a), 3)

    def test_zz_carray_iteration(self):
        """Iteration over C arrays shouldn't crash Python
           Without the SWIG workaround this would crash
        """
        a = uint64Array(3)
        for i in a:
            a[i] = i

        a_tuple = tuple(a[i] for i in a)
        self.assertEqual((0, 1, 2), a_tuple)
