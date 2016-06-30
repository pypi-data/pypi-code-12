from io import StringIO
import textwrap
from unittest import TestCase

from iso8601 import parse_date as d
import numpy as np
import pandas as pd

import pd2hts


tenmin_test_timeseries = textwrap.dedent("""\
            2008-02-07 09:40,1032.43,
            2008-02-07 09:50,1042.54,
            2008-02-07 10:00,1051.65,
            2008-02-07 10:10,1054.76,
            2008-02-07 10:20,1071.87,
            2008-02-07 10:30,1096.98,
            2008-02-07 10:40,1093.09,
            2008-02-07 10:50,1110.10,
            2008-02-07 11:00,1123.21,
            2008-02-07 11:10,1144.32,
            2008-02-07 11:20,1141.00,
            2008-02-07 11:30,1142.01,MISS
            2008-02-07 11:40,1154.02,
            2008-02-07 11:50,,
            2008-02-07 12:00,1180.04,
            2008-02-07 12:10,1191.49,
            2008-02-07 12:20,1216.06,
            2008-02-07 12:30,1216.07,
            2008-02-07 12:40,1224.08,
            2008-02-07 12:50,1213.09,
            2008-02-07 13:00,1217.10,
            2008-02-07 13:10,1231.11,
            """)

tenmin_test_timeseries_file_version_2 = textwrap.dedent("""\
            Version=2\r
            Unit=°C\r
            Count=22\r
            Title=A test 10-min time series\r
            Comment=This timeseries is extremely important\r
            Comment=because the comment that describes it\r
            Comment=spans five lines.\r
            Comment=\r
            Comment=These five lines form two paragraphs.\r
            Timezone=EET (UTC+0200)\r
            Time_step=10,0\r
            Nominal_offset=0,0\r
            Actual_offset=0,0\r
            Variable=temperature\r
            Precision=1\r
            \r
            2008-02-07 09:40,1032.4,\r
            2008-02-07 09:50,1042.5,\r
            2008-02-07 10:00,1051.7,\r
            2008-02-07 10:10,1054.8,\r
            2008-02-07 10:20,1071.9,\r
            2008-02-07 10:30,1097.0,\r
            2008-02-07 10:40,1093.1,\r
            2008-02-07 10:50,1110.1,\r
            2008-02-07 11:00,1123.2,\r
            2008-02-07 11:10,1144.3,\r
            2008-02-07 11:20,1141.0,\r
            2008-02-07 11:30,1142.0,MISS\r
            2008-02-07 11:40,1154.0,\r
            2008-02-07 11:50,,\r
            2008-02-07 12:00,1180.0,\r
            2008-02-07 12:10,1191.5,\r
            2008-02-07 12:20,1216.1,\r
            2008-02-07 12:30,1216.1,\r
            2008-02-07 12:40,1224.1,\r
            2008-02-07 12:50,1213.1,\r
            2008-02-07 13:00,1217.1,\r
            2008-02-07 13:10,1231.1,\r
            """)

tenmin_test_timeseries_file_version_3 = textwrap.dedent("""\
            Unit=°C\r
            Count=22\r
            Title=A test 10-min time series\r
            Comment=This timeseries is extremely important\r
            Comment=because the comment that describes it\r
            Comment=spans five lines.\r
            Comment=\r
            Comment=These five lines form two paragraphs.\r
            Timezone=EET (UTC+0200)\r
            Time_step=10,0\r
            Nominal_offset=0,0\r
            Actual_offset=0,0\r
            Variable=temperature\r
            Precision=1\r
            Location=24.678900 38.123450 4326\r
            Altitude=219.22\r
            \r
            2008-02-07 09:40,1032.4,\r
            2008-02-07 09:50,1042.5,\r
            2008-02-07 10:00,1051.7,\r
            2008-02-07 10:10,1054.8,\r
            2008-02-07 10:20,1071.9,\r
            2008-02-07 10:30,1097.0,\r
            2008-02-07 10:40,1093.1,\r
            2008-02-07 10:50,1110.1,\r
            2008-02-07 11:00,1123.2,\r
            2008-02-07 11:10,1144.3,\r
            2008-02-07 11:20,1141.0,\r
            2008-02-07 11:30,1142.0,MISS\r
            2008-02-07 11:40,1154.0,\r
            2008-02-07 11:50,,\r
            2008-02-07 12:00,1180.0,\r
            2008-02-07 12:10,1191.5,\r
            2008-02-07 12:20,1216.1,\r
            2008-02-07 12:30,1216.1,\r
            2008-02-07 12:40,1224.1,\r
            2008-02-07 12:50,1213.1,\r
            2008-02-07 13:00,1217.1,\r
            2008-02-07 13:10,1231.1,\r
            """)

tenmin_test_timeseries_file_version_4 = textwrap.dedent("""\
            Unit=°C\r
            Count=22\r
            Title=A test 10-min time series\r
            Comment=This timeseries is extremely important\r
            Comment=because the comment that describes it\r
            Comment=spans five lines.\r
            Comment=\r
            Comment=These five lines form two paragraphs.\r
            Timezone=EET (UTC+0200)\r
            Time_step=10,0\r
            Timestamp_rounding=0,0\r
            Timestamp_offset=0,0\r
            Variable=temperature\r
            Precision=1\r
            Location=24.678900 38.123450 4326\r
            Altitude=219.22\r
            \r
            2008-02-07 09:40,1032.4,\r
            2008-02-07 09:50,1042.5,\r
            2008-02-07 10:00,1051.7,\r
            2008-02-07 10:10,1054.8,\r
            2008-02-07 10:20,1071.9,\r
            2008-02-07 10:30,1097.0,\r
            2008-02-07 10:40,1093.1,\r
            2008-02-07 10:50,1110.1,\r
            2008-02-07 11:00,1123.2,\r
            2008-02-07 11:10,1144.3,\r
            2008-02-07 11:20,1141.0,\r
            2008-02-07 11:30,1142.0,MISS\r
            2008-02-07 11:40,1154.0,\r
            2008-02-07 11:50,,\r
            2008-02-07 12:00,1180.0,\r
            2008-02-07 12:10,1191.5,\r
            2008-02-07 12:20,1216.1,\r
            2008-02-07 12:30,1216.1,\r
            2008-02-07 12:40,1224.1,\r
            2008-02-07 12:50,1213.1,\r
            2008-02-07 13:00,1217.1,\r
            2008-02-07 13:10,1231.1,\r
            """)

tenmin_test_timeseries_file_no_altitude = textwrap.dedent("""\
            Unit=°C\r
            Count=22\r
            Title=A test 10-min time series\r
            Comment=This timeseries is extremely important\r
            Comment=because the comment that describes it\r
            Comment=spans five lines.\r
            Comment=\r
            Comment=These five lines form two paragraphs.\r
            Timezone=EET (UTC+0200)\r
            Time_step=10,0\r
            Timestamp_rounding=0,0\r
            Timestamp_offset=0,0\r
            Variable=temperature\r
            Precision=1\r
            Location=24.678900 38.123450 4326\r
            \r
            2008-02-07 09:40,1032.4,\r
            2008-02-07 09:50,1042.5,\r
            2008-02-07 10:00,1051.7,\r
            2008-02-07 10:10,1054.8,\r
            2008-02-07 10:20,1071.9,\r
            2008-02-07 10:30,1097.0,\r
            2008-02-07 10:40,1093.1,\r
            2008-02-07 10:50,1110.1,\r
            2008-02-07 11:00,1123.2,\r
            2008-02-07 11:10,1144.3,\r
            2008-02-07 11:20,1141.0,\r
            2008-02-07 11:30,1142.0,MISS\r
            2008-02-07 11:40,1154.0,\r
            2008-02-07 11:50,,\r
            2008-02-07 12:00,1180.0,\r
            2008-02-07 12:10,1191.5,\r
            2008-02-07 12:20,1216.1,\r
            2008-02-07 12:30,1216.1,\r
            2008-02-07 12:40,1224.1,\r
            2008-02-07 12:50,1213.1,\r
            2008-02-07 13:00,1217.1,\r
            2008-02-07 13:10,1231.1,\r
            """)

tenmin_test_timeseries_file_no_location = textwrap.dedent("""\
            Unit=°C\r
            Count=22\r
            Title=A test 10-min time series\r
            Comment=This timeseries is extremely important\r
            Comment=because the comment that describes it\r
            Comment=spans five lines.\r
            Comment=\r
            Comment=These five lines form two paragraphs.\r
            Timezone=EET (UTC+0200)\r
            Time_step=10,0\r
            Timestamp_rounding=0,0\r
            Timestamp_offset=0,0\r
            Variable=temperature\r
            Precision=1\r
            \r
            2008-02-07 09:40,1032.4,\r
            2008-02-07 09:50,1042.5,\r
            2008-02-07 10:00,1051.7,\r
            2008-02-07 10:10,1054.8,\r
            2008-02-07 10:20,1071.9,\r
            2008-02-07 10:30,1097.0,\r
            2008-02-07 10:40,1093.1,\r
            2008-02-07 10:50,1110.1,\r
            2008-02-07 11:00,1123.2,\r
            2008-02-07 11:10,1144.3,\r
            2008-02-07 11:20,1141.0,\r
            2008-02-07 11:30,1142.0,MISS\r
            2008-02-07 11:40,1154.0,\r
            2008-02-07 11:50,,\r
            2008-02-07 12:00,1180.0,\r
            2008-02-07 12:10,1191.5,\r
            2008-02-07 12:20,1216.1,\r
            2008-02-07 12:30,1216.1,\r
            2008-02-07 12:40,1224.1,\r
            2008-02-07 12:50,1213.1,\r
            2008-02-07 13:00,1217.1,\r
            2008-02-07 13:10,1231.1,\r
            """)

tenmin_test_timeseries_file_no_precision = textwrap.dedent("""\
            Unit=°C\r
            Count=22\r
            Title=A test 10-min time series\r
            Comment=This timeseries is extremely important\r
            Comment=because the comment that describes it\r
            Comment=spans five lines.\r
            Comment=\r
            Comment=These five lines form two paragraphs.\r
            Timezone=EET (UTC+0200)\r
            Time_step=10,0\r
            Timestamp_rounding=0,0\r
            Timestamp_offset=0,0\r
            Variable=temperature\r
            Location=24.678900 38.123450 4326\r
            Altitude=219.22\r
            \r
            2008-02-07 09:40,1032.430000,\r
            2008-02-07 09:50,1042.540000,\r
            2008-02-07 10:00,1051.650000,\r
            2008-02-07 10:10,1054.760000,\r
            2008-02-07 10:20,1071.870000,\r
            2008-02-07 10:30,1096.980000,\r
            2008-02-07 10:40,1093.090000,\r
            2008-02-07 10:50,1110.100000,\r
            2008-02-07 11:00,1123.210000,\r
            2008-02-07 11:10,1144.320000,\r
            2008-02-07 11:20,1141.000000,\r
            2008-02-07 11:30,1142.010000,MISS\r
            2008-02-07 11:40,1154.020000,\r
            2008-02-07 11:50,,\r
            2008-02-07 12:00,1180.040000,\r
            2008-02-07 12:10,1191.490000,\r
            2008-02-07 12:20,1216.060000,\r
            2008-02-07 12:30,1216.070000,\r
            2008-02-07 12:40,1224.080000,\r
            2008-02-07 12:50,1213.090000,\r
            2008-02-07 13:00,1217.100000,\r
            2008-02-07 13:10,1231.110000,\r
            """)

tenmin_test_timeseries_file_zero_precision = textwrap.dedent("""\
            Unit=°C\r
            Count=22\r
            Title=A test 10-min time series\r
            Comment=This timeseries is extremely important\r
            Comment=because the comment that describes it\r
            Comment=spans five lines.\r
            Comment=\r
            Comment=These five lines form two paragraphs.\r
            Timezone=EET (UTC+0200)\r
            Time_step=10,0\r
            Timestamp_rounding=0,0\r
            Timestamp_offset=0,0\r
            Variable=temperature\r
            Precision=0\r
            Location=24.678900 38.123450 4326\r
            Altitude=219.22\r
            \r
            2008-02-07 09:40,1032,\r
            2008-02-07 09:50,1043,\r
            2008-02-07 10:00,1052,\r
            2008-02-07 10:10,1055,\r
            2008-02-07 10:20,1072,\r
            2008-02-07 10:30,1097,\r
            2008-02-07 10:40,1093,\r
            2008-02-07 10:50,1110,\r
            2008-02-07 11:00,1123,\r
            2008-02-07 11:10,1144,\r
            2008-02-07 11:20,1141,\r
            2008-02-07 11:30,1142,MISS\r
            2008-02-07 11:40,1154,\r
            2008-02-07 11:50,,\r
            2008-02-07 12:00,1180,\r
            2008-02-07 12:10,1191,\r
            2008-02-07 12:20,1216,\r
            2008-02-07 12:30,1216,\r
            2008-02-07 12:40,1224,\r
            2008-02-07 12:50,1213,\r
            2008-02-07 13:00,1217,\r
            2008-02-07 13:10,1231,\r
            """)


tenmin_test_timeseries_file_negative_precision = textwrap.dedent("""\
            Unit=°C\r
            Count=22\r
            Title=A test 10-min time series\r
            Comment=This timeseries is extremely important\r
            Comment=because the comment that describes it\r
            Comment=spans five lines.\r
            Comment=\r
            Comment=These five lines form two paragraphs.\r
            Timezone=EET (UTC+0200)\r
            Time_step=10,0\r
            Timestamp_rounding=0,0\r
            Timestamp_offset=0,0\r
            Variable=temperature\r
            Precision=-1\r
            Location=24.678900 38.123450 4326\r
            Altitude=219.22\r
            \r
            2008-02-07 09:40,1030,\r
            2008-02-07 09:50,1040,\r
            2008-02-07 10:00,1050,\r
            2008-02-07 10:10,1050,\r
            2008-02-07 10:20,1070,\r
            2008-02-07 10:30,1100,\r
            2008-02-07 10:40,1090,\r
            2008-02-07 10:50,1110,\r
            2008-02-07 11:00,1120,\r
            2008-02-07 11:10,1140,\r
            2008-02-07 11:20,1140,\r
            2008-02-07 11:30,1140,MISS\r
            2008-02-07 11:40,1150,\r
            2008-02-07 11:50,,\r
            2008-02-07 12:00,1180,\r
            2008-02-07 12:10,1190,\r
            2008-02-07 12:20,1220,\r
            2008-02-07 12:30,1220,\r
            2008-02-07 12:40,1220,\r
            2008-02-07 12:50,1210,\r
            2008-02-07 13:00,1220,\r
            2008-02-07 13:10,1230,\r
            """)


class Pd2htsTestCase(TestCase):

    def setUp(self):
        self.reference_ts = pd.read_csv(
            StringIO(tenmin_test_timeseries), parse_dates=[0],
            usecols=['date', 'value', 'flags'], index_col=0, header=None,
            names=('date', 'value', 'flags'),
            converters={'flags': lambda x: x}).asfreq('10T')
        self.reference_ts.timestamp_rounding = '0,0'
        self.reference_ts.timestamp_offset = '0,0'
        self.reference_ts.unit = '°C'
        self.reference_ts.title = "A test 10-min time series"
        self.reference_ts.precision = 1
        self.reference_ts.time_step = "10,0"
        self.reference_ts.timezone = "EET (UTC+0200)"
        self.reference_ts.variable = "temperature"
        self.reference_ts.comment = ("This timeseries is extremely important\n"
                                     "because the comment that describes it\n"
                                     "spans five lines.\n\n"
                                     "These five lines form two paragraphs.")
        self.reference_ts.location = {'abscissa': 24.6789,
                                      'ordinate': 38.12345, 'srid': 4326,
                                      'altitude': 219.22, 'asrid': None}

    def test_write_empty(self):
        ts = pd.Series()
        s = StringIO()
        pd2hts.write(ts, s)
        self.assertEqual(s.getvalue(), '')

    def test_write(self):
        data = np.array(
            [[d("2005-08-23 18:53"),         93,   ''],
             [d("2005-08-24 19:52"),        108.7, ''],
             [d("2005-08-25 23:59"),         28.3, 'HEARTS SPADES'],
             [d("2005-08-26 00:02"), float('NaN'), ''],
             [d("2005-08-27 00:02"), float('NaN'), 'DIAMONDS']])
        ts = pd.DataFrame(data[:, [1, 2]], index=data[:, 0],
                          columns=('value', 'flags'))
        s = StringIO()
        pd2hts.write(ts, s)
        self.assertEqual(s.getvalue(), textwrap.dedent("""\
            2005-08-23 18:53,93,\r
            2005-08-24 19:52,108.7,\r
            2005-08-25 23:59,28.3,HEARTS SPADES\r
            2005-08-26 00:02,,\r
            2005-08-27 00:02,,DIAMONDS\r
            """))

    def test_write_file(self):
        outstring = StringIO()
        pd2hts.write_file(self.reference_ts, outstring, version=2)
        self.assertEqual(outstring.getvalue(),
                         tenmin_test_timeseries_file_version_2)

        outstring = StringIO()
        pd2hts.write_file(self.reference_ts, outstring, version=3)
        self.assertEqual(outstring.getvalue(),
                         tenmin_test_timeseries_file_version_3)

        outstring = StringIO()
        pd2hts.write_file(self.reference_ts, outstring, version=4)
        self.assertEqual(outstring.getvalue(),
                         tenmin_test_timeseries_file_version_4)

    def test_read_empty(self):
        s = StringIO()
        apd = pd2hts.read(s)
        self.assertEqual(len(apd), 0)

    def test_read(self):
        s = StringIO(tenmin_test_timeseries)
        s.seek(0)
        apd = pd2hts.read(s)
        self.assertEqual(len(apd), 22)
        np.testing.assert_array_equal(
            apd.index, pd.date_range('2008-02-07 09:40',
                                     periods=22, freq='10T'))
        expected = np.array([
            [1032.43, ''],
            [1042.54, ''],
            [1051.65, ''],
            [1054.76, ''],
            [1071.87, ''],
            [1096.98, ''],
            [1093.09, ''],
            [1110.10, ''],
            [1123.21, ''],
            [1144.32, ''],
            [1141.00, ''],
            [1142.01, 'MISS'],
            [1154.02, ''],
            [float('NaN'), ''],
            [1180.04, ''],
            [1191.49, ''],
            [1216.06, ''],
            [1216.07, ''],
            [1224.08, ''],
            [1213.09, ''],
            [1217.10, ''],
            [1231.11, '']], dtype=object)
        np.testing.assert_allclose(apd.values[:, 0].astype(float),
                                   expected[:, 0].astype(float))
        np.testing.assert_array_equal(apd.values[:, 1], expected[:, 1])

    def test_read_file(self):
        s = StringIO(tenmin_test_timeseries_file_version_4)
        s.seek(0)
        apd = pd2hts.read_file(s)

        # Check metadata
        self.assertEqual(apd.unit, '°C')
        self.assertEqual(apd.title, 'A test 10-min time series')
        self.assertEqual(apd.comment, textwrap.dedent('''\
            This timeseries is extremely important
            because the comment that describes it
            spans five lines.

            These five lines form two paragraphs.'''))
        self.assertEqual(apd.timezone, 'EET (UTC+0200)')
        self.assertEqual(apd.time_step, '10,0')
        self.assertEqual(apd.timestamp_rounding, '0,0')
        self.assertEqual(apd.timestamp_offset, '0,0')
        self.assertEqual(apd.variable, 'temperature')
        self.assertEqual(apd.precision, 1)
        self.assertAlmostEqual(apd.location['abscissa'], 24.678900, places=6)
        self.assertAlmostEqual(apd.location['ordinate'], 38.123450, places=6)
        self.assertEqual(apd.location['srid'], 4326)
        self.assertAlmostEqual(apd.location['altitude'], 219.22, places=2)
        self.assertTrue(apd.location['asrid'] is None)

        # Check time series data
        self.assertEqual(len(apd), 22)
        np.testing.assert_array_equal(
            apd.index, pd.date_range('2008-02-07 09:40',
                                     periods=22, freq='10T'))
        expected = np.array([
            [1032.4, ''],
            [1042.5, ''],
            [1051.7, ''],
            [1054.8, ''],
            [1071.9, ''],
            [1097.0, ''],
            [1093.1, ''],
            [1110.1, ''],
            [1123.2, ''],
            [1144.3, ''],
            [1141.0, ''],
            [1142.0, 'MISS'],
            [1154.0, ''],
            [float('NaN'), ''],
            [1180.0, ''],
            [1191.5, ''],
            [1216.1, ''],
            [1216.1, ''],
            [1224.1, ''],
            [1213.1, ''],
            [1217.1, ''],
            [1231.1, '']], dtype=object)
        np.testing.assert_allclose(apd.values[:, 0].astype(float),
                                   expected[:, 0].astype(float))
        np.testing.assert_array_equal(apd.values[:, 1], expected[:, 1])

    def test_no_location(self):
        """Test that all works correctly whenever some items are missing from
        location."""

        # Try with altitude None
        self.reference_ts.location['altitude'] = None
        outstring = StringIO()
        pd2hts.write_file(self.reference_ts, outstring, version=4)
        self.assertEqual(outstring.getvalue(),
                         tenmin_test_timeseries_file_no_altitude)

        # Try without altitude at all
        del self.reference_ts.location['altitude']
        outstring = StringIO()
        pd2hts.write_file(self.reference_ts, outstring, version=4)
        self.assertEqual(outstring.getvalue(),
                         tenmin_test_timeseries_file_no_altitude)

        # Try with location None
        self.reference_ts.location = None
        outstring = StringIO()
        pd2hts.write_file(self.reference_ts, outstring, version=4)
        self.assertEqual(outstring.getvalue(),
                         tenmin_test_timeseries_file_no_location)

        # Try with no location at all
        delattr(self.reference_ts, 'location')
        outstring = StringIO()
        pd2hts.write_file(self.reference_ts, outstring, version=4)
        self.assertEqual(outstring.getvalue(),
                         tenmin_test_timeseries_file_no_location)

    def test_precision(self):
        """Test that all works correctly whenever precision is missing."""

        # Try with precision None
        self.reference_ts.precision = None
        outstring = StringIO()
        pd2hts.write_file(self.reference_ts, outstring, version=4)
        self.assertEqual(outstring.getvalue(),
                         tenmin_test_timeseries_file_no_precision)

        # Try with no precision at all
        delattr(self.reference_ts, 'precision')
        outstring = StringIO()
        pd2hts.write_file(self.reference_ts, outstring, version=4)
        self.assertEqual(outstring.getvalue(),
                         tenmin_test_timeseries_file_no_precision)

        # Try with zero precision
        self.reference_ts.precision = 0
        outstring = StringIO()
        pd2hts.write_file(self.reference_ts, outstring, version=4)
        self.assertEqual(outstring.getvalue(),
                         tenmin_test_timeseries_file_zero_precision)

        # Try with negative precision
        self.reference_ts.precision = -1
        outstring = StringIO()
        pd2hts.write_file(self.reference_ts, outstring, version=4)
        self.assertEqual(outstring.getvalue(),
                         tenmin_test_timeseries_file_negative_precision)
