from netcdftime import utime, JulianDayFromDate, DateFromJulianDay
from netcdftime import datetime as datetimex
from netCDF4 import Dataset, num2date, date2num, date2index, num2date
import copy
import numpy
import random
import sys
import unittest
import os
import tempfile
from datetime import datetime, timedelta
from numpy.testing import assert_almost_equal, assert_equal

# test netcdftime module for netCDF time <--> python datetime conversions.


class netcdftimeTestCase(unittest.TestCase):

    def setUp(self):
        self.cdftime_mixed = utime('hours since 0001-01-01 00:00:00')
        self.cdftime_julian = utime(
            'hours since 0001-01-01 00:00:00', calendar='julian')
        self.cdftime_mixed_tz = utime('hours since 0001-01-01 00:00:00 -06:00')
        self.cdftime_pg = utime('seconds since 0001-01-01 00:00:00',
                                calendar='proleptic_gregorian')
        self.cdftime_noleap = utime(
            'days since 1600-02-28 00:00:00', calendar='noleap')
        self.cdftime_leap = utime(
            'days since 1600-02-29 00:00:00', calendar='all_leap')
        self.cdftime_360day = utime(
            'days since 1600-02-30 00:00:00', calendar='360_day')
        self.cdftime_jul = utime(
            'hours since 1000-01-01 00:00:00', calendar='julian')
        self.cdftime_iso = utime("seconds since 1970-01-01T00:00:00Z")
        self.cdftime_leading_space = utime("days since  850-01-01 00:00:00")
        self.cdftime_mixed_capcal = utime('hours since 0001-01-01 00:00:00',
                                          calendar='Standard')
        self.cdftime_noleap_capcal = utime(
            'days since 1600-02-28 00:00:00', calendar='NOLEAP')

    def runTest(self):
        """testing netcdftime"""
        # test mixed julian/gregorian calendar
        # check attributes.
        self.assertTrue(self.cdftime_mixed.units == 'hours')
        self.assertTrue(
            repr(self.cdftime_mixed.origin) == '   1-01-01 00:00:00')
        self.assertTrue(
            self.cdftime_mixed.unit_string == 'hours since 0001-01-01 00:00:00')
        self.assertTrue(self.cdftime_mixed.calendar == 'standard')
        # check date2num method. (date before switch)
        d = datetime(1582, 10, 4, 23)
        t1 = self.cdftime_mixed.date2num(d)
        assert_almost_equal(t1, 13865687.0)
        # check num2date method.
        d2 = self.cdftime_mixed.num2date(t1)
        self.assertTrue(str(d) == str(d2))
        # this is a non-existant date, should raise ValueError.
        d = datetime(1582, 10, 5, 0)
        self.assertRaises(ValueError, self.cdftime_mixed.date2num, d)
        # check date2num/num2date with date after switch.
        d = datetime(1582, 10, 15, 0)
        t2 = self.cdftime_mixed.date2num(d)
        assert_almost_equal(t2, 13865688.0)
        d2 = self.cdftime_mixed.num2date(t2)
        self.assertTrue(str(d) == str(d2))
        # check day of year.
        ndayr = d.timetuple()[7]
        self.assertTrue(ndayr == 288)
        # test using numpy arrays.
        t = numpy.arange(t2, t2 + 240.0, 12.)
        t = numpy.reshape(t, (4, 5))
        d = self.cdftime_mixed.num2date(t)
        self.assertTrue(d.shape == t.shape)
        d_check = "1582-10-15 00:00:001582-10-15 12:00:001582-10-16 00:00:001582-10-16 12:00:001582-10-17 00:00:001582-10-17 12:00:001582-10-18 00:00:001582-10-18 12:00:001582-10-19 00:00:001582-10-19 12:00:001582-10-20 00:00:001582-10-20 12:00:001582-10-21 00:00:001582-10-21 12:00:001582-10-22 00:00:001582-10-22 12:00:001582-10-23 00:00:001582-10-23 12:00:001582-10-24 00:00:001582-10-24 12:00:00"
        d2 = [str(dd) for dd in d.flat]
        self.assertTrue(d_check == ''.join(d2))
        # test julian calendar with numpy arrays
        d = self.cdftime_julian.num2date(t)
        self.assertTrue(d.shape == t.shape)
        d_check = "1582-10-05 00:00:001582-10-05 12:00:001582-10-06 00:00:001582-10-06 12:00:001582-10-07 00:00:001582-10-07 12:00:001582-10-08 00:00:001582-10-08 12:00:001582-10-09 00:00:001582-10-09 12:00:001582-10-10 00:00:001582-10-10 12:00:001582-10-11 00:00:001582-10-11 12:00:001582-10-12 00:00:001582-10-12 12:00:001582-10-13 00:00:001582-10-13 12:00:001582-10-14 00:00:001582-10-14 12:00:00"
        d2 = [str(dd) for dd in d.flat]
        self.assertTrue(d_check == ''.join(d2))
        # test proleptic gregorian calendar.
        self.assertTrue(self.cdftime_pg.units == 'seconds')
        self.assertTrue(repr(self.cdftime_pg.origin) == '   1-01-01 00:00:00')
        self.assertTrue(
            self.cdftime_pg.unit_string == 'seconds since 0001-01-01 00:00:00')
        self.assertTrue(self.cdftime_pg.calendar == 'proleptic_gregorian')
        # check date2num method.
        d = datetime(1990, 5, 5, 2, 17)
        t1 = numpy.around(self.cdftime_pg.date2num(d))
        self.assertTrue(t1 == 62777470620.0)
        # check num2date method.
        d2 = self.cdftime_pg.num2date(t1)
        self.assertTrue(str(d) == str(d2))
        # check day of year.
        ndayr = d.timetuple()[7]
        self.assertTrue(ndayr == 125)
        # check noleap calendar.
        # this is a non-existant date, should raise ValueError.
        self.assertRaises(
            ValueError, utime, 'days since 1600-02-29 00:00:00', calendar='noleap')
        self.assertTrue(self.cdftime_noleap.units == 'days')
        self.assertTrue(
            repr(self.cdftime_noleap.origin) == '1600-02-28 00:00:00')
        self.assertTrue(
            self.cdftime_noleap.unit_string == 'days since 1600-02-28 00:00:00')
        self.assertTrue(self.cdftime_noleap.calendar == 'noleap')
        assert_almost_equal(
            self.cdftime_noleap.date2num(self.cdftime_noleap.origin), 0.0)
        # check date2num method.
        d1 = datetime(2000, 2, 28)
        d2 = datetime(1600, 2, 28)
        t1 = self.cdftime_noleap.date2num(d1)
        t2 = self.cdftime_noleap.date2num(d2)
        assert_almost_equal(t1, 400 * 365.)
        assert_almost_equal(t2, 0.)
        t12 = self.cdftime_noleap.date2num([d1, d2])
        assert_almost_equal(t12, [400 * 365., 0])
        # check num2date method.
        d2 = self.cdftime_noleap.num2date(t1)
        self.assertTrue(str(d1) == str(d2))
        # check day of year.
        ndayr = d2.timetuple()[7]
        self.assertTrue(ndayr == 59)
        # non-existant date, should raise ValueError.
        date = datetime(2000, 2, 29)
        self.assertRaises(ValueError, self.cdftime_noleap.date2num, date)
        # check all_leap calendar.
        self.assertTrue(self.cdftime_leap.units == 'days')
        self.assertTrue(
            repr(self.cdftime_leap.origin) == '1600-02-29 00:00:00')
        self.assertTrue(
            self.cdftime_leap.unit_string == 'days since 1600-02-29 00:00:00')
        self.assertTrue(self.cdftime_leap.calendar == 'all_leap')
        assert_almost_equal(
            self.cdftime_leap.date2num(self.cdftime_leap.origin), 0.0)
        # check date2num method.
        d1 = datetime(2000, 2, 29)
        d2 = datetime(1600, 2, 29)
        t1 = self.cdftime_leap.date2num(d1)
        t2 = self.cdftime_leap.date2num(d2)
        assert_almost_equal(t1, 400 * 366.)
        assert_almost_equal(t2, 0.)
        # check num2date method.
        d2 = self.cdftime_leap.num2date(t1)
        self.assertTrue(str(d1) == str(d2))
        # check day of year.
        ndayr = d2.timetuple()[7]
        self.assertTrue(ndayr == 60)
        # double check date2num,num2date methods.
        d = datetime(2000, 12, 31)
        t1 = self.cdftime_mixed.date2num(d)
        d2 = self.cdftime_mixed.num2date(t1)
        self.assertTrue(str(d) == str(d2))
        ndayr = d2.timetuple()[7]
        self.assertTrue(ndayr == 366)
        # check 360_day calendar.
        self.assertTrue(self.cdftime_360day.units == 'days')
        self.assertTrue(
            repr(self.cdftime_360day.origin) == '1600-02-30 00:00:00')
        self.assertTrue(
            self.cdftime_360day.unit_string == 'days since 1600-02-30 00:00:00')
        self.assertTrue(self.cdftime_360day.calendar == '360_day')
        assert_almost_equal(
            self.cdftime_360day.date2num(self.cdftime_360day.origin), 0.0)
        # check date2num,num2date methods.
        # use datetime from netcdftime, since this date doesn't
        # exist in "normal" calendars.
        d = datetimex(2000, 2, 30)
        t1 = self.cdftime_360day.date2num(d)
        assert_almost_equal(t1, 360 * 400.)
        d2 = self.cdftime_360day.num2date(t1)
        assert_equal(str(d), str(d2))
        # check day of year.
        d = datetime(2001, 12, 30)
        t = self.cdftime_360day.date2num(d)
        assert_almost_equal(t, 144660.0)
        date = self.cdftime_360day.num2date(t)
        self.assertTrue(str(d) == str(date))
        ndayr = date.timetuple()[7]
        self.assertTrue(ndayr == 360)
        # Check fraction
        d = datetime(1969, 12, 30, 12)
        t = self.cdftime_360day.date2num(d)
        date = self.cdftime_360day.num2date(t)
        assert_equal(str(d), str(date))
        # test proleptic julian calendar.
        d = datetime(1858, 11, 17, 12)
        t = self.cdftime_jul.date2num(d)
        assert_almost_equal(t, 7528932.0)
        d1 = datetime(1582, 10, 4, 23)
        d2 = datetime(1582, 10, 15, 0)
        assert_almost_equal(
            self.cdftime_jul.date2num(d1) + 241.0, self.cdftime_jul.date2num(d2))
        date = self.cdftime_jul.num2date(t)
        self.assertTrue(str(d) == str(date))
        # test julian day from date, date from julian day
        d = datetime(1858, 11, 17)
        mjd = JulianDayFromDate(d)
        assert_almost_equal(mjd, 2400000.5)
        date = DateFromJulianDay(mjd)
        self.assertTrue(str(date) == str(d))
        # test iso 8601 units string
        d = datetime(1970, 1, 1, 1)
        t = self.cdftime_iso.date2num(d)
        assert_equal(numpy.around(t), 3600)
        # test fix for issue 75 (seconds hit 60 at end of month,
        # day goes out of range).
        t = 733499.0
        d = num2date(t, units='days since 0001-01-01 00:00:00')
        dateformat =  '%Y-%m-%d %H:%M:%S'
        assert_equal(d.strftime(dateformat), '2009-04-01 00:00:00')
        # test edge case of issue 75 for numerical problems
        for t in (733498.999, 733498.9999, 733498.99999, 733498.999999, 733498.9999999):
            d = num2date(t, units='days since 0001-01-01 00:00:00')
            t2 = date2num(d, units='days since 0001-01-01 00:00:00')
            assert(abs(t2 - t) < 1e-5)  # values should be less than second
        # Check equality testing
        d1 = datetimex(1979, 6, 21, 9, 23, 12)
        d2 = datetime(1979, 6, 21, 9, 23, 12)
        assert(d1 == d2)
        # check timezone offset
        d = datetime(2012, 2, 29, 15)
        # mixed_tz is -6 hours from UTC, mixed is UTC so
        # difference in elapsed time is 6 hours.
        assert(self.cdftime_mixed_tz.date2num(
            d) - self.cdftime_mixed.date2num(d) == 6)

        # Check comparisons with Python datetime types
        d1 = num2date(0, 'days since 1000-01-01', 'standard')
        d2 = datetime(2000, 1, 1)
        d3 = num2date(0, 'days since 3000-01-01', 'standard')
        assert d1 < d2
        assert d2 < d3

        # check all comparisons
        assert d1 != d2
        assert d1 <= d2
        assert d2 > d1
        assert d2 >= d1

        # check datetime hash
        d1 = datetimex(1995, 1, 1)
        d2 = datetime(1995, 1, 1)
        d3 = datetimex(2001, 2, 30)
        assert hash(d1) == hash(d1)
        assert hash(d1) == hash(d2)
        assert hash(d1) != hash(d3)
        assert hash(d3) == hash(d3)

        # check datetime immutability
        # using assertRaises as a context manager
        # only works with python >= 2.7 (issue #497).
        #with self.assertRaises(AttributeError):
        #    d1.year = 1999
        #with self.assertRaises(AttributeError):
        #    d1.month = 6
        #with self.assertRaises(AttributeError):
        #    d1.day = 5
        #with self.assertRaises(AttributeError):
        #    d1.hour = 10
        #with self.assertRaises(AttributeError):
        #    d1.minute = 33
        #with self.assertRaises(AttributeError):
        #    d1.second = 45
        #with self.assertRaises(AttributeError):
        #    d1.dayofwk = 1
        #with self.assertRaises(AttributeError):
        #    d1.dayofyr = 52
        #with self.assertRaises(AttributeError):
        #    d1.format = '%Y'
        try:
            d1.year = 1999
            d1.month = 6
            d1.day = 5
            d1.hour = 10
            d1.minute = 33
            d1.second = 45
            d1.dayofwk = 1
            d1.dayofyr = 52
            d1.format = '%Y'
        except AttributeError:
            pass

        # Check leading white space
        self.assertEqual(
            repr(self.cdftime_leading_space.origin), ' 850-01-01 00:00:00')

        #issue 330
        units = "seconds since 1970-01-01T00:00:00Z"
        t = utime(units)
        for n in range(10):
            assert n == int(round(t.date2num(t.num2date(n))))

        #issue 344
        units = 'hours since 2013-12-12T12:00:00'
        assert(1.0 == date2num(num2date(1.0, units), units))

        # test rountrip accuracy
        # also tests error found in issue #349
        calendars=['standard', 'gregorian', 'proleptic_gregorian', 'noleap', 'julian',\
                   'all_leap', '365_day', '366_day', '360_day']
        dateformat =  '%Y-%m-%d %H:%M:%S'
        dateref = datetime(2015,2,28,12)
        ntimes = 1001
        for calendar in calendars:
            eps = 100.
            units = 'microseconds since 1800-01-30 01:01:01'
            microsecs1 = date2num(dateref,units,calendar=calendar)
            for n in range(ntimes):
                microsecs1 += 1.
                date1 = num2date(microsecs1, units, calendar=calendar)
                microsecs2 = date2num(date1, units, calendar=calendar)
                date2 = num2date(microsecs2, units, calendar=calendar)
                err = numpy.abs(microsecs1 - microsecs2)
                assert(err < eps)
                assert(date1.strftime(dateformat) == date2.strftime(dateformat))
            units = 'milliseconds since 1800-01-30 01:01:01'
            eps = 0.1
            millisecs1 = date2num(dateref,units,calendar=calendar)
            for n in range(ntimes):
                millisecs1 += 0.001
                date1 = num2date(millisecs1, units, calendar=calendar)
                millisecs2 = date2num(date1, units, calendar=calendar)
                date2 = num2date(millisecs2, units, calendar=calendar)
                err = numpy.abs(millisecs1 - millisecs2)
                assert(err < eps)
                assert(date1.strftime(dateformat) == date2.strftime(dateformat))
            eps = 1.e-4
            units = 'seconds since 0001-01-30 01:01:01'
            secs1 = date2num(dateref,units,calendar=calendar)
            for n in range(ntimes):
                secs1 += 0.1
                date1 = num2date(secs1, units, calendar=calendar)
                secs2 = date2num(date1, units, calendar=calendar)
                date2 = num2date(secs2, units, calendar=calendar)
                err = numpy.abs(secs1 - secs2)
                assert(err < eps)
                assert(date1.strftime(dateformat) == date2.strftime(dateformat))
            eps = 1.e-5
            units = 'minutes since 0001-01-30 01:01:01'
            mins1 = date2num(dateref,units,calendar=calendar)
            for n in range(ntimes):
                mins1 += 0.01
                date1 = num2date(mins1, units, calendar=calendar)
                mins2 = date2num(date1, units, calendar=calendar)
                date2 = num2date(mins2, units, calendar=calendar)
                err = numpy.abs(mins1 - mins2)
                assert(err < eps)
                assert(date1.strftime(dateformat) == date2.strftime(dateformat))
            eps = 1.e-5
            units = 'hours since 0001-01-30 01:01:01'
            hrs1 = date2num(dateref,units,calendar=calendar)
            for n in range(ntimes):
                hrs1 += 0.001
                date1 = num2date(hrs1, units, calendar=calendar)
                hrs2 = date2num(date1, units, calendar=calendar)
                date2 = num2date(hrs2, units, calendar=calendar)
                err = numpy.abs(hrs1 - hrs2)
                assert(err < eps)
                assert(date1.strftime(dateformat) == date2.strftime(dateformat))
            eps = 1.e-5
            units = 'days since 0001-01-30 01:01:01'
            days1 = date2num(dateref,units,calendar=calendar)
            for n in range(ntimes):
                days1 += 0.00001
                date1 = num2date(days1, units, calendar=calendar)
                days2 = date2num(date1, units, calendar=calendar)
                date2 = num2date(days2, units, calendar=calendar)
                err = numpy.abs(days1 - days2)
                assert(err < eps)
                assert(date1.strftime(dateformat) == date2.strftime(dateformat))

        # issue 353
        assert (num2date(0, 'hours since 2000-01-01 0') ==
                datetime(2000,1,1,0))

        # issue 354
        num1 = numpy.array([[0, 1], [2, 3]])
        num2 = numpy.array([[0, 1], [2, 3]])
        dates1 = num2date(num1, 'days since 0001-01-01')
        dates2 = num2date(num2, 'days since 2001-01-01')
        assert( dates1.shape == (2,2) )
        assert( dates2.shape == (2,2) )
        num1b = date2num(dates1, 'days since 0001-01-01')
        num2b = date2num(dates2, 'days since 2001-01-01')
        assert( num1b.shape == (2,2) )
        assert( num2b.shape == (2,2) )
        assert_almost_equal(num1,num1b)
        assert_almost_equal(num2,num2b)

        # issue 357 (make sure time zone offset in units done correctly)
        # Denver time, 7 hours behind UTC
        units = 'hours since 1682-10-15 -07:00 UTC'
        # date after gregorian switch, python datetime used
        date = datetime(1682,10,15) # assumed UTC
        num = date2num(date,units)
        # UTC is 7 hours ahead of units, so num should be 7
        assert (num == 7)
        assert (num2date(num, units) == date)
        units = 'hours since 1482-10-15 -07:00 UTC'
        # date before gregorian switch, netcdftime datetime used
        date = datetime(1482,10,15)
        num = date2num(date,units)
        date2 = num2date(num, units)
        assert (num == 7)
        assert (date2.year == date.year)
        assert (date2.month == date.month)
        assert (date2.day == date.day)
        assert (date2.hour == date.hour)
        assert (date2.minute == date.minute)
        assert (date2.second == date.second)

        # issue 362: case insensitive calendars
        self.assertTrue(self.cdftime_mixed_capcal.calendar == 'standard')
        self.assertTrue(self.cdftime_noleap_capcal.calendar == 'noleap')
        d = datetime(2015, 3, 4, 12, 18, 30)
        units = 'days since 0001-01-01'
        for cap_cal, low_cal in (('STANDARD', 'standard'),
                                 ('NoLeap', 'noleap'),
                                 ('Gregorian', 'gregorian'),
                                 ('ALL_LEAP', 'all_leap')):
            d1 = date2num(d, units, cap_cal)
            d2 = date2num(d, units, low_cal)
            self.assertEqual(d1, d2)
            self.assertEqual(num2date(d1, units, cap_cal),
                             num2date(d1, units, low_cal))
        # issue 415
        t = datetimex(2001, 12, 1, 2, 3, 4)
        self.assertEqual(t, copy.deepcopy(t))

        # issue 442
        units = "days since 0000-01-01 00:00:00"
        # this should fail (year zero not allowed with real-world calendars)
        try:
            date2num(datetime(1, 1, 1), units, calendar='standard')
        except ValueError:
            pass
        # this should not fail (year zero allowed in 'fake' calendars)
        t = date2num(datetime(1, 1, 1), units, calendar='360_day')
        self.assertEqual(t, 360)
        d = num2date(t, units, calendar='360_day')
        self.assertEqual(d, datetimex(1,1,1))
        d = num2date(0, units, calendar='360_day')
        self.assertEqual(d, datetimex(0,1,1))

        # list around missing dates in Gregorian calendar
        # scalar
        units = 'days since 0001-01-01 12:00:00'
        t1 = date2num(datetime(1582, 10, 4), units, calendar='gregorian')
        t2 = date2num(datetime(1582, 10, 15), units, calendar='gregorian')
        self.assertEqual(t1+1, t2)
        # list
        t1, t2 = date2num([datetime(1582, 10, 4), datetime(1582, 10, 15)], units, calendar='gregorian')
        self.assertEqual(t1+1, t2)
        t1, t2 = date2num([datetime(1582, 10, 4), datetime(1582, 10, 15)], units, calendar='standard')
        self.assertEqual(t1+1, t2)
        # this should fail: days missing in Gregorian calendar
        try:
            t1, t2, t3 = date2num([datetime(1582, 10, 4), datetime(1582, 10, 10), datetime(1582, 10, 15)], units, calendar='standard')
        except ValueError:
            pass


class TestDate2index(unittest.TestCase):

    class TestTime:

        """Fake a netCDF time variable."""

        def __init__(self, start, n, step, units, calendar='standard'):
            """Create an object that fakes a netCDF time variable.

            Internally, this object has a _data array attribute whose values
            corresponds to dates in the given units and calendar. `start`, `n`
            and `step` define the starting date, the length of the array and
            the distance between each date (in units).

            :Example:
            >>> t = TestTime(datetime(1989, 2, 18), 45, 6, 'hours since 1979-01-01')
            >>> print num2date(t[1], t.units)
            1989-02-18 06:00:00
            """
            self.units = units
            self.calendar = calendar
            t0 = date2num(start, units, calendar)
            self._data = (t0 + numpy.arange(n) * step).astype('float')
            self.dtype = numpy.float

        def __getitem__(self, item):
            return self._data[item]

        def __len__(self):
            return len(self._data)

        def shape():
            def fget(self):
                return self._data.shape
            return locals()

        shape = property(**shape())

    def setUp(self):
        self.standardtime = self.TestTime(datetime(1950, 1, 1), 366, 24,
                                          'hours since 1900-01-01', 'standard')

        self.file = tempfile.NamedTemporaryFile(suffix='.nc', delete=False).name
        f = Dataset(self.file, 'w')
        f.createDimension('time', None)
        time = f.createVariable('time', float, ('time',))
        time.units = 'hours since 1900-01-01'
        time[:] = self.standardtime[:]
        f.createDimension('time2', 1)
        time2 = f.createVariable('time2', 'f8', ('time2',))
        time2.units = 'days since 1901-01-01'
        self.first_timestamp = datetime(2000, 1, 1)
        time2[0] = date2num(self.first_timestamp, time2.units)
        ntimes = 21
        f.createDimension("record", ntimes)
        time3 = f.createVariable("time3", numpy.int32, ("record", ))
        time3.units = "seconds since 1970-01-01 00:00:00"
        date = datetime(2037,1,1,0)
        dates = [date]
        for ndate in range(ntimes-1):
            date += (ndate+1)*timedelta(hours=1)
            dates.append(date)
        time3[:] = date2num(dates,time3.units)
        f.close()

    def tearDown(self):
        os.remove(self.file)

    def test_simple(self):
        t = date2index(datetime(1950, 2, 1), self.standardtime)
        assert_equal(t, 31)

    def test_singletime(self):
        # issue 215 test (date2index with time variable length == 1)
        f = Dataset(self.file)
        time2 = f.variables['time2']
        result_index = date2index(self.first_timestamp, time2, select="exact")
        assert_equal(result_index, 0)
        f.close()

    def test_list(self):
        t = date2index(
            [datetime(1950, 2, 1), datetime(1950, 2, 3)], self.standardtime)
        assert_equal(t, [31, 33])

    def test_nonuniform(self):
        """Check that the fallback mechanism works. """
        nutime = self.TestTime(datetime(1950, 1, 1), 366, 24,
                               'hours since 1900-01-01', 'standard')

        # Let's remove the second entry, so that the computed stride is not
        # representative and the bisection method is needed.
        nutime._data = nutime._data[numpy.r_[0, slice(2, 200)]]

        t = date2index(datetime(1950, 2, 1), nutime)
        assert_equal(t, 30)

        t = date2index([datetime(1950, 2, 1), datetime(1950, 2, 3)], nutime)
        assert_equal(t, [30, 32])

    def test_failure(self):
        nutime = self.TestTime(datetime(1950, 1, 1), 366, 24,
                               'hours since 1900-01-01', 'standard')
        try:
            t = date2index(datetime(1949, 2, 1), nutime)
        except ValueError:
            pass
        else:
            raise ValueError('This test should have failed.')

    def test_select_dummy(self):
        nutime = self.TestTime(datetime(1950, 1, 1), 366, 24,
                               'hours since 1400-01-01', 'standard')

        dates = [datetime(1950, 1, 2, 6), datetime(
            1950, 1, 3), datetime(1950, 1, 3, 18)]

        t = date2index(dates, nutime, select='before')
        assert_equal(t, [1, 2, 2])

        t = date2index(dates, nutime, select='after')
        assert_equal(t, [2, 2, 3])

        t = date2index(dates, nutime, select='nearest')
        assert_equal(t, [1, 2, 3])

    def test_select_nc(self):
        f = Dataset(self.file, 'r')
        nutime = f.variables['time']

        dates = [datetime(1950, 1, 2, 6), datetime(
            1950, 1, 3), datetime(1950, 1, 3, 18)]

        t = date2index(dates, nutime, select='before')
        assert_equal(t, [1, 2, 2])

        t = date2index(dates, nutime, select='after')
        assert_equal(t, [2, 2, 3])

        t = date2index(dates, nutime, select='nearest')
        assert_equal(t, [1, 2, 3])

        # Test dates outside the support with select
        t = date2index(datetime(1949, 12, 1), nutime, select='nearest')
        assert_equal(t, 0)

        t = date2index(datetime(1978, 1, 1), nutime, select='nearest')
        assert_equal(t, 365)

        # Test dates outside the support with before
        self.assertRaises(
            ValueError, date2index, datetime(1949, 12, 1), nutime, select='before')

        t = date2index(datetime(1978, 1, 1), nutime, select='before')
        assert_equal(t, 365)

        # Test dates outside the support with after
        t = date2index(datetime(1949, 12, 1), nutime, select='after')
        assert_equal(t, 0)

        self.assertRaises(
            ValueError, date2index, datetime(1978, 1, 1), nutime, select='after')
        # test microsecond and millisecond units
        unix_epoch = "milliseconds since 1970-01-01T00:00:00Z"
        d = datetime(2038, 1, 19, 3, 14, 7)
        millisecs = int(
            date2num(d, unix_epoch, calendar='proleptic_gregorian'))
        assert_equal(millisecs, (2 ** 32 / 2 - 1) * 1000)
        unix_epoch = "microseconds since 1970-01-01T00:00:00Z"
        microsecs = int(date2num(d, unix_epoch))
        assert_equal(microsecs, (2 ** 32 / 2 - 1) * 1000000)
        # test microsecond accuracy in date2num/num2date roundtrip
        # note: microsecond accuracy lost for time intervals greater
        # than about 270 years.
        units = 'microseconds since 1776-07-04 00:00:00-12:00'
        dates =\
            [datetime(1962, 10, 27, 6, 1, 30, 9001), datetime(
                1993, 11, 21, 12, 5, 25, 999), datetime(1995, 11, 25, 18, 7, 59, 999999)]
        times2 = date2num(dates, units)
        dates2 = num2date(times2, units)
        for date, date2 in zip(dates, dates2):
            assert_equal(date, date2)
        f.close()

    def test_issue444(self):
        # make sure integer overflow not causing error in
        # calculation of nearest index when sum of adjacent
        # time values won't fit in 32 bits.
        ntimes = 20
        f = Dataset(self.file, 'r')
        query_time = datetime(2037, 1, 3, 21, 12)
        index = date2index(query_time, f.variables['time3'], select='nearest')
        assert(index == 11)
        f.close()

if __name__ == '__main__':
    unittest.main()
