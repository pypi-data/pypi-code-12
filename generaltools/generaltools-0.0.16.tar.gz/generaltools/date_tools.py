"""Helper classed to work with time and dates

One useful feature is to extract a timestamp from a GILDAS scan.

"""
import numpy
import time
import datetime
import pytz

from decimal import Decimal


class DateTool(object):
    r'''
    Functions to facilitate working with dates
    '''
    def __init__(self):
        # Convert Gildas month abbreviations to integer numbers.
        self.month_dict = {'jan':1, 'feb':2, 'mar':3, 'apr':4, 'may':5,
                           'jun':6, 'jul':7, 'aug':8, 'sep':9, 'oct':10,
                           'nov':11, 'dec':12}
        self.tzname = time.tzname[0]
        self.berlin = pytz.timezone('Europe/Berlin')
        self.santiago = pytz.timezone('America/Santiago')
        self.utc = pytz.utc
        self.tz_dict = {'CET':self.berlin, 'CLT':self.santiago, 'UTC':self.utc}

    def _decompose_decimal_time(self, ut_time):
        r''' Calculate hours, minute and seconds from a time given as a decimal
        number in hours '''
        self.ut_time = Decimal(float(ut_time))
        self._residual_hour = self.ut_time % 1
        self.ut_hour = int(self.ut_time-self._residual_hour)
        self.ut_minute = self._residual_hour * 60
        self._residual_minute = self.ut_minute % 1
        self.ut_minute = int(self.ut_minute-self._residual_minute)
        self.ut_second = int(self._residual_minute * 60)

    def number_to_utc_datetime(self, dt):
        dt = self.number_to_datetime(dt)
        dt = self.change_tz_date_to_utc(dt)
        return dt

    def number_to_datetime(self, dt):
        dt = datetime.datetime.strptime(time.ctime(dt), "%a %b %d %H:%M:%S %Y")
        return dt

    def change_tz_date_to_utc(self, dt):
        dt = self.tz_dict[self.tzname].localize(dt)
        dt = dt.astimezone(pytz.utc)
        return dt

    def change_tz_date_to_other(self, dt, other_tz):
        dt = self.tz_dict[self.tzname].localize(dt)
        dt = dt.astimezone(self.tz_dict[other_tz])
        return dt

    def change_utc_date_to_other(self, dt, other_tz):
        dt = pytz.utc.localize(dt)
        dt = dt.astimezone(self.tz_dict[other_tz])
        return dt

    def datetime_to_tuple(self, dt):
        return (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

    def tuple_to_datetime(self, tuple_):
        return  datetime.datetime(int(tuple_[0]), int(tuple_[1]),
                                  int(tuple_[2]), int(tuple_[3]),
                                  int(tuple_[4]), int(tuple_[5]))

    def now_at_site(self, other_tz):
        now = datetime.datetime.now()
        now = self.tz_dict[self.tzname].localize(now)
        return now.astimezone(self.tz_dict[other_tz])

    def change_tuple_to_other_tz(self, tuple_, tz, datetime_object=False):
        dt = self.tuple_to_datetime(tuple_)
        dt = self.change_utc_date_to_other(dt, tz)
        if datetime_object:
            return self.datetime_to_tuple(dt), dt
        else:
            return self.datetime_to_tuple(dt)


class GildasTimeStamp(DateTool):
    """Creates a python datetime object for the timestamp of a scan from Gildas.
    """
    def __init__(self, gildas_dict=None, dump=None):
        '''Inherit from DateTools
        Undo Gildas Time encoding madness.  Time expressed as
        fraction of 2pi/24h
        '''
        DateTool.__init__(self)
        self._gildas_dict = gildas_dict
#        print self._gildas_dict
        self.gildas_ut = self._gildas_dict.utobs.__sicdata__
        self.normal_ut = self.gildas_ut / (2. * numpy.pi) * 24
        # Correct the fact that Gildas stores only one timestamp per subscan
        # Assuming that this timestamp is the start of the scan, here the integration
        # time of each dump is added cumulatively.
        if dump > 1:
            self.normal_ut = (self.normal_ut +
                              (self._gildas_dict.time * dump / 60 / 60))
        self._decompose_decimal_time(self.normal_ut)
        self._decompose_gildas_date_string()
        self.timestamp = datetime.datetime(self.ut_year, self.ut_month,
                                           self.ut_day, self.ut_hour,
                                           self.ut_minute, self.ut_second)
        self.timestamp = self.timestamp.replace(tzinfo=self.utc)

    def _decompose_gildas_date_string(self):
        ''' Convert date string to integers representing year, month and day.
        '''
        self._gildas_date = self._gildas_dict.r.head.gen.cdobs.__sicdata__
        self._gildas_date = str(self._gildas_date).split('-')
        self.ut_year = int(self._gildas_date[2])
        self.ut_month = self.month_dict[self._gildas_date[1].lower()]
        self.ut_day = int(self._gildas_date[0])
