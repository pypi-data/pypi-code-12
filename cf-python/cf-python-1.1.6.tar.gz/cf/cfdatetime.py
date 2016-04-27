import netCDF4

# Work: Running Sphinx v1.2b1

from datetime import datetime

from numpy import array     as numpy_array
from numpy import ndarray   as numpy_ndarray
from numpy import ndim      as numpy_ndim
from numpy import vectorize as numpy_vectorize

from .functions import inspect as cf_inspect
from .units     import Units

if netCDF4.__version__ <= '1.1.1':
    _netCDF4_netcdftime_parse_date = netCDF4.netcdftime._parse_date
    _netCDF4_netcdftime_strftime   = netCDF4.netcdftime._strftime
else:
    _netCDF4_netcdftime_parse_date = netCDF4.netcdftime.netcdftime._parse_date
    _netCDF4_netcdftime_strftime   = netCDF4.netcdftime._datetime._strftime


# ====================================================================
#
# Datetime object (overrides netCDF4.netcdftime.datetime)
#
# ====================================================================

class Datetime(object):

    # ----------------------------------------------------------------
    # Adapted from Jeff Whitaker's netCDF4.netcdftime.datetime
    # ----------------------------------------------------------------

    '''

A date-time object which supports CF calendars.

Any date and time valid in any CF calendar is allowed.

In many situations, it may be used interchangeably with a built-in
`datetime.datetime` object. For example:

>>> import datetime
>>> d = cf.Datetime(2004, 2, 30)
>>> d > datetime.datetime(2004, 2, 1)
True

**Attributes**

==============  ======================================================
Attribute       Description
==============  ======================================================
`!year`         The year of the date
`!month`        The month of the year of the date
`!day`          The day of the month of the date
`!hour`         The hour of the day of the date
`!minute`       The minute of the hour of the date
`!second`       The second of the minute of the date
`!microsecond`  The microsecond of the second of the date
==============  ======================================================

.. seealso:: `cf.dt`, `cf.TimeDuration`

'''
    def __init__(self, year, month=1, day=1, hour=0, minute=0, second=0,
                 microsecond=0, dayofwk=-1, dayofyr=1):
        '''**Initialization**

:Parameters:

    year : int
        The year.

    month, day, hour, minute, second, microsecond : ints, optional
        The month of the year, the day of the month and time of the
        day. *month* and *day* default to 1 and *hour*; *minute*,
        *second* and *microsecond* default to 0.

:Examples:

>>> cf.Datetime(2003)
<CF Datetime: 2003-01-01 00:00:00>
>>> d = cf.Datetime(2003, 2, 30)
>>> d = cf.Datetime(2003, 2, 30, 0)
>>> d = cf.Datetime(2003, 2, 30, 0, 0)
>>> d = cf.Datetime(2003, 2, 30, 0, 0, 0)
>>> d = cf.Datetime(2003, 4, 5, 12, 30, 15)
>>> d = cf.Datetime(year=2003, month=4, day=5, hour=12, minute=30, second=15)
>>> d.year, d.month, d.day, d.hour, d.minute, d.second
(2003, 4, 5, 12, 30, 15)
>>> d.timetuple()
(2003, 4, 5, 12, 30, 15, -1, 1)

        '''
        # ------------------------------------------------------------
        # NOTE: dayofyr is set to 1 by default, otherwise
        # time.strftime will complain.
        # ------------------------------------------------------------
        self.year        = year
        self.month       = month
        self.day         = day
        self.hour        = hour
        self.minute      = minute
        self.second      = second
        self.microsecond = microsecond
        self.dayofwk     = dayofwk
        self.dayofyr     = dayofyr
        self.format      = '%Y-%m-%d %H:%M:%S'
    #--- End: def

    def __deepcopy__(self, memo):
        '''

Used if copy.deepcopy is called

''' 
        return self.copy()
    #--- End: def

    def __repr__(self):
        '''

x__repr__() <==> repr(x)

'''   
        return '<CF %s: %s>' % (self.__class__.__name__, self)
    #--- End: def

    def __str__(self):
        '''

x__str__() <==> str(x)

'''
        return self.strftime()
    #--- End: def

    def __eq__(self, other):
        '''

x__eq__(y) <==> x==y

'''
        try:
            return self._timetuple6() == other.timetuple()[:6]
        except AttributeError:
            return NotImplemented
    #--- End: def

    def __ne__(self, other):
        '''

x__ne__(y) <==> x!=y

'''
        try:
            return self._timetuple6() != other.timetuple()[:6]
        except AttributeError:
            return NotImplemented
    #--- End: def

    def __ge__(self, other):
        '''

x__ge__(y) <==> x>=y

'''
        try:
            return self._timetuple6() >= other.timetuple()[:6]
        except AttributeError:
            return NotImplemented
    #--- End: def

    def __gt__(self, other):
        '''

x__gt__(y) <==> x>y

'''
        try:
            return self._timetuple6() > other.timetuple()[:6]
        except AttributeError:
            return NotImplemented
    #--- End: def

    def __le__(self, other):
        '''

x__le__(y) <==> x<=y

'''
        try:
            return self._timetuple6() <= other.timetuple()[:6]
        except AttributeError:
            return NotImplemented
    #--- End: def

    def __lt__(self, other):
        '''

x__lt__(y) <==> x<y

'''
        try:
            return self._timetuple6() < other.timetuple()[:6]
        except AttributeError:
            return NotImplemented
    #--- End: def

    def _to_real_datetime(self):
        return datetime(self.year, self.month, self.day,
                        self.hour, self.minute, self.second,
                        self.microsecond)
    #--- End: def

    def __hash__(self):
        try:
            d = self._to_real_datetime()
        except ValueError:
            return hash(self.timetuple())
        else:
            return hash(d)
    #--- End: def

#    @property
#    def year(self): return self._year
#
#    @property
#    def month(self): return self._month 
#        
#    @property
#    def day(self): return self._day         
#        
#    @property
#    def hour(self):return  self._hour       
#        
#    @property
#    def minute(self): return self._minute   
#        
#    @property
#    def second(self): return self._second   
#        
#    @property
#    def microsecond(self): return self._microsecond 
#        
#    @property
#    def dayofwk(self): return self._dayofwk    
#        
#    @property
#    def dayofyr(self): return self._dayofyr     
    
    def _timetuple6(self):
        '''

Return a tuple of the first six date-time attributes.

``d._timetuple6()`` is equivalent to ``(d.year, d.month, d.day,
d.hour, d.minute, d.second)``.

:Returns:

    out : tuple
        The first six date-time attributes.

:Examples:

>>> d = cf.Datetime(2005, 6, 7, 23, 45, 57)
>>> d._timetuple6()
(2005, 6, 7, 23, 45, 57)

'''
        return (self.year, self.month, self.day,
                self.hour, self.minute, self.second)
    #--- End: def

    def copy(self):
        '''

Return a deep copy.

``d.copy()`` is equivalent to ``copy.deepcopy(d)``.

:Returns:	

    out :
        The deep copy.

:Examples:

>>> e = d.copy()

'''
        return type(self)(*self.timetuple()[:-1])
    #--- End: def

    def inspect(self):
        '''

Inspect the attributes.

.. seealso:: `cf.inspect`

:Returns: 

    None

'''
        print cf_inspect(self)
    #--- End: def

    def strftime(self, format=None):
        if format is None:
            format = self.format
    
        return _netCDF4_netcdftime_strftime(self, format)
    #--- End: def

    def timetuple(self):
        '''

Return a tuple of the date-time attributes.

``d.timetuple()`` is equivalent to ``(d.year, d.month, d.day, d.hour,
d.minute, d.second, d.dayofwk, d.dayofyr, -1)``.

:Returns:

    out : tuple
        The date-time attributes.

:Examples:

>>> d = cf.Datetime(2005, 6, 7, 23, 45, 57, 999888)
>>> d.timetuple()
(2005, 6, 7, 23, 45, 57, -1, 1, -1)

'''
        return (self.year, self.month, self.day,
                self.hour, self.minute, self.second,
                self.dayofwk, self.dayofyr, -1)
    #--- End: def

    @classmethod
    def utcnow(cls):
        '''

Return the current Gregorian calendar UTC date and time.

:Returns:

    out: cf.Datetime
        The current UTC date and time.

:Examples:

>>> cf.Datetime.utcnow()
<CF Datetime: 2013-11-19 17:55:59>
>>> d = cf.Datetime(2005, 6, 7)
>>> d.utcnow()
<CF Datetime: 2013-11-19 17:56:07>
>>> d
<CF Datetime: 2005-06-07 00:00:00>

'''

        return cls(*datetime.utcnow().timetuple()[:-1])
    #--- End: def

#--- End: class
netCDF4.netcdftime.datetime = Datetime


def dt(*args, **kwargs):
    '''Return a date-time variable for a given date and time.

The date and time may be specified with an ISO 8601-like date-time
string (in which non-Gregorian calendar dates are allowed) or by
providing a value for the year and, optionally, the month, day, hour,
minute, second and microsecond.

.. seealso:: `cf.Datetime`

:Parameters:

    args, kwargs :
        If the first positional argument is a string, then it must be
        an ISO 8601-like date-time string from which a `cf.Datetime`
        object is initialized. Otherwise, the positional and keyword
        arguments are used to explicitly initialize a `cf.Datetime`
        object, so see `cf.Datetime` for details.

:Returns:

    out : cf.Datetime
        The new date-time object.

:Examples:

>>> d = cf.dt(2003, 2, 30)
>>> d = cf.dt(2003, 2, 30, 0, 0, 0)
>>> d = cf.dt('2003-2-30')
>>> d = cf.dt('2003-2-30 0:0:0')

>>> d = cf.dt(2003, 4, 5, 12, 30, 15)
>>> d = cf.dt(year=2003, month=4, day=5, hour=12, minute=30, second=15)
>>> d = cf.dt('2003-04-05 12:30:15')
>>> d.year, d.month, d.day, d.hour, d.minute, d.second
(2003, 4, 5, 12, 30, 15)

    '''
    if kwargs:
        return Datetime(*args, **kwargs)
    elif not args:
        raise ValueError("34 woah!")
    else:
        arg0 = args[0]
        if isinstance(arg0, basestring):
            return st2Datetime(arg0)
        else:
            return Datetime(*args)
#--- End: def

def st2dt(array, units_in, dummy0=None, dummy1=None):
    '''
    
The returned array is always independent.

:Parameters:

    array : numpy array-like

    units_in : cf.Units

    dummy0 : *optional*
        Ignored.

    dummy1 : *optional*
        Ignored.

:Returns: 

    out : numpy array
        An array of `cf.Datetime` or `datetime.datetime` objects with
        the same shape as *array*.

:Examples:

'''
    if units_in._calendar in ('gregorian' 'standard', 'none'):
        return array_st2datetime(array)
    else:
        return array_st2Datetime(array)
#--- End: def

def st2datetime(date_string):
    '''

Parse an ISO 8601 date-time string into a datetime.datetime object.

:Parameters:

    date_string : str

:Returns:

    out : datetime.datetime

'''
    if date_string.count('-') != 2:
        raise ValueError("A string must contain a year, a month and a day")

    year,month,day,hour,minute,second,utc_offset = _netCDF4_netcdftime_parse_date(date_string)
    if utc_offset:
        raise ValueError("Can't specify a time offset from UTC")
            
    return datetime(year, month, day, hour, minute, second)
#--- End: def

array_st2datetime = numpy_vectorize(st2datetime, otypes=[object])

def st2Datetime(date_string):
    '''

Parse an ISO 8601 date-time string into a `cf.Datetime` object.

:Parameters:

    date_string : str

:Returns:

    out : cf.Datetime

'''
    if date_string.count('-') != 2:
        raise ValueError("A string must contain a year, a month and a day")

    year,month,day,hour,minute,second,utc_offset = _netCDF4_netcdftime_parse_date(date_string)
    if utc_offset:
        raise ValueError("Can't specify a time offset from UTC")
            
    return Datetime(year, month, day, hour, minute, second)
#--- End: def

array_st2Datetime = numpy_vectorize(st2Datetime, otypes=[object])

def rt2dt(array, units_in, dummy0=None, dummy1=None):
    '''

The returned array is always independent.

:Parameters:

    array : numpy array-like

    units_in : cf.Units

    dummy0 :
        Ignored.

    dummy1 :
        Ignored.

:Returns: 

    out : numpy array
        An array of `cf.Datetime` or `datetime.datetime` objects with
        the same shape as *array*.

'''           
    ndim = numpy_ndim(array)
    
    array = units_in._utime.num2date(array)
    if not ndim:
        array = numpy_array(array, dtype=object)

    return array
#--- End: def

def dt2rt(array, dummy0, units_out, dummy1=None):
    '''
    
The returned array is always independent.

:Parameters:

    array : numpy array-like of date-time objects

    dummy0 :
        Ignored.

    units_out : cf.Units

    dummy1 :
        Ignored.

:Returns: 

    out : numpy array
        An array of numbers with the same shape as *array*.

'''
    ndim = numpy_ndim(array)
    
    if not ndim and isinstance(array, numpy_ndarray):
        # This necessary because date2num gets upset if you pass
        # it a scalar numpy array
        array = array.item()

    array = units_out._utime.date2num(array)
    
    if not ndim:
        array = numpy_array(array)

    return array
#--- End: def

def _JulianDayFromDate(date, calendar='standard'):
    '''

Create a Julian Day from a 'datetime-like' object.  Returns the
fractional Julian Day (resolution 1 second).

if calendar='standard' or 'gregorian' (default), Julian day follows
Julian Calendar on and before 1582-10-5, Gregorian calendar after
1582-10-15.

if calendar='proleptic_gregorian', Julian Day follows gregorian
calendar.

if calendar='julian', Julian Day follows julian calendar.

Algorithm:

Meeus, Jean (1998) Astronomical Algorithms (2nd
Edition). Willmann-Bell, Virginia. p. 63

This is taken from netCDF4.netcdftime.JulianDayFromDate, with an error
check added.

'''
    # based on redate.py by David Finlayson.

    year=date.year; month=date.month; day=date.day
    hour=date.hour; minute=date.minute; second=date.second

    try:
        datetime(year, month, day, hour, minute, second)
    except ValueError:
        raise ValueError("Bad %s calendar date: %s" % (calendar, date))

    # Convert time to fractions of a day
    day = day + hour/24.0 + minute/1440.0 + second/86400.0

    # Start Meeus algorithm (variables are in his notation)
    if (month < 3):
        month = month + 12
        year = year - 1

    A = int(year/100)

    # MC
    # jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + \
    #      day - 1524.5
    jd = 365.*year + int(0.25 * year + 2000.) + int(30.6001 * (month + 1)) + \
         day + 1718994.5

    # optionally adjust the jd for the switch from
    # the Julian to Gregorian Calendar
    # here assumed to have occurred the day after 1582 October 4
    if calendar in ['standard','gregorian']:
        if jd >= 2299170.5:
            # 1582 October 15 (Gregorian Calendar)
            B = 2 - A + int(A/4)
        elif jd < 2299160.5:
            # 1582 October 5 (Julian Calendar)
            B = 0
        else:
            raise ValueError('impossible date (falls in gap between end of Julian calendar and beginning of Gregorian calendar')
    elif calendar == 'proleptic_gregorian':
        B = 2 - A + int(A/4)
    elif calendar == 'julian':
        B = 0
    else:
        raise ValueError('unknown calendar, must be one of julian,standard,gregorian,proleptic_gregorian, got %s' % calendar)

    # adjust for Julian calendar if necessary
    jd = jd + B

    return jd
#--- End: def
netCDF4.netcdftime.JulianDayFromDate = _JulianDayFromDate

def _NoLeapDayFromDate(date):
    '''

Creates a Julian Day for a calendar with no leap years from a
date-time instance.  Returns the fractional Julian Day (resolution 1
second).

'''
    year=date.year; month=date.month; day=date.day
    hour=date.hour; minute=date.minute; second=date.second

    if month == 2 and day > 28:
        raise ValueError("Bad 365_day calendar date: %s" % date)

    if year != 0:
        try:
            datetime(year, month, day, hour, minute, second)
        except ValueError:
            raise ValueError("Bad 365_day calendar date: %s" % date)
    
    # Convert time to fractions of a day
    day = day + hour/24.0 + minute/1440.0 + second/86400.0

    # Start Meeus algorithm (variables are in his notation)
    if (month < 3):
        month = month + 12
        year = year - 1

    jd = int(365. * (year + 4716)) + int(30.6001 * (month + 1)) + \
         day - 1524.5

    return jd
#--- End: def
if netCDF4.__version__ <= '1.1.1':
    netCDF4.netcdftime._NoLeapDayFromDate = _NoLeapDayFromDate
else:
    netCDF4.netcdftime.netcdftime._NoLeapDayFromDate = _NoLeapDayFromDate
