import operator

from datetime import datetime

from numpy import array     as numpy_array
from numpy import size      as numpy_size

from cfdatetime import Datetime
from .functions import equals
from .functions import inspect as cf_inspect
from .units     import Units

from .data.data import Data


# Define some useful units
_calendar_years  = Units('calendar_years')
_calendar_months = Units('calendar_months')
_days            = Units('days')
_hours           = Units('hours')
_minutes         = Units('minutes')
_seconds         = Units('seconds')


# ====================================================================
#
# TimeDuration object
#
# ====================================================================

class TimeDuration(object):
    '''A duration of time.

The duration of time is a number of either calendar years, calender
months, days, hours, minutes or seconds.


**Creating time intervals**

A time interval of exactly the time duration, starting or ending at a
particular date-time, may be produced with the `interval` method:

>>> t = cf.TimeDuration(6, 'calendar_months')
>>> t
<CF TimeDuration: 6 calendar_months (from Y-01-01 00:00:00)>
>>> t.interval(1999, 12)
(<CF Datetime: 1999-12-01 00:00:00>, <CF Datetime: 2000-06-01 00:00:00>)
>>> t = cf.TimeDuration(5, 'days', hour=6)
>>> t
<CF TimeDuration: 5 days (from Y-01-01 06:00:00)>
>>> t.interval(2004, 3, 2, end=True)
(datetime.datetime(2004, 2, 26, 6, 0), <CF Datetime: 2004-03-02 06:00:00>)
>>> t.interval(2004, 3, 2, end=True, calendar='noleap')
(<CF Datetime: 2004-02-25 06:00:00>, <CF Datetime: 2004-03-02 06:00:00>)
>>> t.interval(2004, 3, 2, end=True, calendar='360_day')
(<CF Datetime: 2004-02-27 06:00:00>, <CF Datetime: 2004-03-02 06:00:00>)
>>> t.interval(2004, 3, 2, end=True, calendar='360_day', iso='start and duration')
'2004-02-27 06:00:00/P5D'


**Arithmetic and comparison operators**

Arithmetic and comparison operations are defined for `cf.TimeDuration`
objects, `cf.Data` objects, `numpy` arrays and numbers:

>>> cf.TimeDuration(2, 'calendar_years') > cf.TimeDuration(1, 'calendar_years')
True
>>> cf.TimeDuration(2, 'calendar_years') < cf.TimeDuration(25, 'calendar_months')
True
>>> cf.TimeDuration(2, 'hours') <= cf.TimeDuration(1, 'days')
True
>>> cf.TimeDuration(2, 'hours') == cf.TimeDuration(1/12.0, 'days')
True
>>> cf.TimeDuration(2, 'days') == cf.TimeDuration(48, 'hours')
True
>>> cf.TimeDuration(2, 'days') == cf.Data(2)
True
>>> cf.TimeDuration(2, 'days') == cf.Data([2.], 'days')
True
>>> cf.TimeDuration(2, 'days') > cf.Data([[60]], 'seconds')
True
>>> cf.TimeDuration(2, 'hours') <= 2
True
>>> cf.TimeDuration(2, 'days') != 30.5
True
>>> cf.TimeDuration(2, 'calendar_years') > numpy.array(1.5)
True
>>> cf.TimeDuration(2, 'calendar_months') < numpy.array([[12]])
True

>>> cf.TimeDuration(30, 'days') + 2
<CF TimeDuration: 32 days (from Y-01-01 00:00:00)>
>>> cf.TimeDuration(64, 'calendar_years') - 2.5
<CF TimeDuration: 61.5 calendar_years (from Y-01-01 00:00:00)>
>>> cf.TimeDuration(64, 'calendar_years') + cf.TimeDuration(23, 'calendar_months')
<CF TimeDuration: 65.9166666667 calendar_years (from Y-01-01 00:00:00)>
>>> cf.TimeDuration(36, 'hours') / numpy.array(8)
<CF TimeDuration: 4 hours (from Y-01-01 00:00:00)>
>>> cf.TimeDuration(36, 'hours') / numpy.array(8.0)
<CF TimeDuration: 4.5 hours (from Y-01-01 00:00:00)>
>>> cf.TimeDuration(36, 'hours') // numpy.array(8.0)
<CF TimeDuration: 4.0 hours (from Y-01-01 00:00:00)>
>>> cf.TimeDuration(36, 'calendar_months') * cf.Data([[2.25]])
<CF TimeDuration: 81.0 calendar_months (from Y-01-01 00:00:00)>
>>> cf.TimeDuration(36, 'calendar_months') // cf.Data([0.825], '10')
<CF TimeDuration: 4.3 calendar_months (from Y-01-01 00:00:00)>
>>> cf.TimeDuration(36, 'calendar_months') % 10
<CF Data: 6 calendar_months>
>>> cf.TimeDuration(36, 'calendar_months') % cf.Data(1, 'calendar_year')
<CF Data: 0.0 calendar_months>
>>> cf.TimeDuration(36, 'calendar_months') % cf.Data(2, 'calendar_year')
<CF Data: 12.0 calendar_months>

The in place operators (``+=``, ``//=``, etc.) are supported in a
similar manner.

**Attributes**

===========  =========================================================
Attribute    Description
===========  =========================================================
`!duration`  The length of the time duration in a `cf.Data` object
             with units.
`!year`      The default year for time interval creation.
`!month`     The default month for time interval creation.
`!day`       The default day for time interval creation.
`!hour`      The default hour for time interval creation.
`!minute`    The default minute for time interval creation.
`!second`    The default second for time interval creation.
===========  =========================================================


**Constructors**

For convenience, the following functions may also be used to create
time duration objects:

========  ============================================================
Function  Description
========  ============================================================
`cf.Y`    Create a time duration of calendar years.
`cf.M`    Create a time duration of calendar months.
`cf.D`    Create a time duration of days.
`cf.h`    Create a time duration of hours.
`cf.m`    Create a time duration of minutes.
`cf.s`    Create a time duration of seconds.
========  ============================================================

.. seealso:: `cf.Data`, `cf.Datetime`

.. versionadded:: 1.0

    '''
    def __init__(self, duration, units=None, year=None, month=1, day=1,
                 hour=0, minute=0, second=0): 
        '''**Initialization**

:Parameters:

    duration : data-like
        The length of the time duration.

    units : str, optional
        The units of the time duration. Only required if *duration* is
        not a `cf.Data` object which contains the units. Must be one
        a units string equivalent to calendar years, calendar months,
        days, hours, minutes or seconds.

    year, month, day, hour, minute, second : ints or None, optional 
        The default date-time elements for defining when a time
        interval based on this time duration (created with the
        `interval` method) begins or ends. See
        `cf.TimeDuration.interval` for details.

:Examples:

>>> t = cf.TimeDuration(cf.Data(3 , 'calendar_years'))
>>> t = cf.TimeDuration(cf.Data(12 , 'hours'))
>>> t = cf.TimeDuration(18 , 'calendar_months')
>>> t = cf.TimeDuration(30 , 'days')
>>> t = cf.TimeDuration(1 , 'day', hour=6)

'''
        if units is not None:
            units = Units(units)
            self.duration = Data(abs(duration), units)
        else:
            self.duration = abs(Data.asdata(duration))
            units = self.duration.Units

        if not (units.iscalendartime or units.istime):
            raise ValueError(
                "Can't create %s of %s" % (self.__class__.__name__, self.duration))

        self.year   = year
        self.month  = month
        self.day    = day
        self.hour   = hour
        self.minute = minute 
        self.second = second
    #--- End: def

    def __array__(self, *dtype):
        '''
'''
        return self.duration.__array__(*dtype)
    #--- End: def

    def __data__(self):
        '''
Returns a new reference to self.duration.

'''
        return self.duration
    #--- End: def

    def __deepcopy__(self, memo):
        '''

Used if copy.deepcopy is called

''' 
        return self.copy()
    #--- End: def

    def __nonzero__(self):
        '''
        
Truth value testing and the built-in operation `bool`

x.__nonzero__() <==> x != 0
'''
        return bool(self.duration)
    #--- End: if

    def __float__(self):
        '''

x.__float__() <==> float(x)

'''
        return float(self.duration)
    #--- End: def

    def __int__(self):
        '''

x.__int__() <==> int(x)

'''
        return int(self.duration)
    #--- End: def

    def __repr__(self):
        '''

x.__repr__() <==> repr(x)

'''
        return '<CF %s: %s>' % (self.__class__.__name__, str(self))
    #--- End: def

    def __str__(self):
        '''

x.__str__() <==> str(x)

'''
        year   = self.year  
        month  = self.month 
        day    = self.day   
        hour   = self.hour  
        minute = self.minute
        second = self.second

        year   = 'Y'  if year   is None else '%d'   % year
        month  = 'MM' if month  is None else '%02d' % month
        day    = 'DD' if day    is None else '%02d' % day
        hour   = 'hh' if hour   is None else '%02d' % hour
        minute = 'mm' if minute is None else '%02d' % minute
        second = 'ss' if second is None else '%02d' % second

        return ('%s (from %s-%s-%s %s:%s:%s)' %
                (self.duration, year, month, day, hour, minute, second))
    #--- End: def
   
    def __ge__(self, other):
        '''

The rich comparison operator ``>=``

x__ge__(y) <==> x>=y

'''
        return bool(self.duration >= other)
    #--- End: def

    def __gt__(self, other):
        '''

The rich comparison operator ``>``

x__gt__(y) <==> x>y

'''
        return bool(self.duration > other)
    #--- End: def

    def __le__(self, other):
        '''

The rich comparison operator ``<=``

x__le__(y) <==> x<=y

'''
        return bool(self.duration <= other)
    #--- End: def

    def __lt__(self, other):
        '''

The rich comparison operator ``<``

x__lt__(y) <==> x<y

'''
        return bool(self.duration < other)
    #--- End: def

    def __eq__(self, other):
        '''

The rich comparison operator ``==``

x__eq__(y) <==> x==y

'''
        return bool(self.duration == other)
    #--- End: def

    def __ne__(self, other):
        '''

The rich comparison operator ``!=``

x__ne__(y) <==> x!=y

'''
        return bool(self.duration != other)
    #--- End: def

    def __add__(self, other):
        '''

The binary arithmetic operation ``+``

x.__add__(y) <==> x + y

'''   
        return self._binary_arithmetic(other, '__add__')
    #--- End: def

    def __sub__(self, other):
        '''

The binary arithmetic operation ``-``

x.__sub__(y) <==> x - y

'''
        return self._binary_arithmetic(other, '__sub__')
    #--- End: def

    def __mul__(self, other):
        '''

The binary arithmetic operation ``*``

x.__mul__(y) <==> x * y

'''   
        return self._binary_arithmetic(other, '__mul__')
    #--- End: def

    def __div__(self, other):
        '''

The binary arithmetic operation ``/``

x.__div__(y) <==> x / y

'''           
        return self._binary_arithmetic(other, '__div__')
    #--- End: def

    def __floordiv__(self, other):
        '''

The binary arithmetic operation ``//``

x.__floordiv__(y) <==> x // y

'''   
        return self._binary_arithmetic(other, '__floordiv__')
    #--- End: def

    def __truediv__(self, other):
        '''

The binary arithmetic operation ``/`` (true division)

x.__truediv__(y) <==> x / y

'''   
        return self._binary_arithmetic(other, '__truediv__')
    #--- End: def

    def __pow__(self, other, modulo=None):
        '''

The binary arithmetic operations ``**`` and ``pow``

x.__pow__(y) <==> x**y

'''   
        if modulo is not None:
            raise NotImplementedError("3-argument power not supported for '%s'" %
                                      self.__class__.__name__)
            
        return self._binary_arithmetic(other, '__pow__')
    #--- End: def

    def __rpow__(self, other, modulo=None):
        '''

The binary arithmetic operations ``**`` and ``pow`` with reflected operands

x.__rpow__(y) <==> y**x

'''   
        if modulo is not None:
            raise NotImplementedError("3-argument power not supported for '%s'" %
                                      self.__class__.__name__)
            
        return self._binary_arithmetic(other, '__rpow__')
    #--- End: def

    def __iadd__(self, other):
        '''

The augmented arithmetic assignment ``+=``

x.__iadd__(y) <==> x += y

'''
        return self._binary_arithmetic(other, '__iadd__', True)
    #--- End: def

    def __idiv__(self, other):
        '''

The augmented arithmetic assignment ``/=``

x.__idiv__(y) <==> x /= y

'''
        return self._binary_arithmetic(other, '__idiv__', True)
    #--- End: def

    def __itruediv__(self, other):
        '''

The augmented arithmetic assignment ``/=`` (true division)

x.__truediv__(y) <==> x/y

'''
        return self._binary_arithmetic(other, '__itruediv__', True)
    #--- End: def

    def __ifloordiv__(self, other):
        '''

The augmented arithmetic assignment ``//=``

x.__ifloordiv__(y) <==> x//=y

'''
        return self._binary_arithmetic(other, '__ifloordiv__', True)
    #--- End: if

    def __imul__(self, other):
        '''

The augmented arithmetic assignment ``*=``

x.__imul__(y) <==> x *= y

'''
        return self._binary_arithmetic(other, '__imul__', True)
    #--- End: def

    def __isub__(self, other):
        '''

The augmented arithmetic assignment ``-=``

x.__isub__(y) <==> x -= y

'''
        return self._binary_arithmetic(other, '__isub__', True)
    #--- End: def

    def __imod__(self, other):
        '''

The augmented arithmetic assignment ``%=``

x.__imod__(y) <==> x %= y

'''
        return NotImplemented
    #--- End: def

    def __ipow__(self, other, modulo=None):
        '''

The augmented arithmetic assignment ``**=``

x.__ipow__(y) <==> x**=yyyy

'''  
        return self._binary_arithmetic(other, '__ipow__', True)
    #--- End: def

    def __iadd__(self, other):
        '''

The augmented arithmetic assignment ``+=``

x.__iadd__(y) <==> x += y

'''
        return self._binary_arithmetic(other, '__iadd__', True)
    #--- End: def

    def __idiv__(self, other):
        '''

The augmented arithmetic assignment ``/=``

x.__idiv__(y) <==> x /= y

'''
        return self._binary_arithmetic(other, '__idiv__', True)
    #--- End: def

    def __itruediv__(self, other):
        '''

The augmented arithmetic assignment ``/=`` (true division)

x.__truediv__(y) <==> x/y

'''
        return self._binary_arithmetic(other, '__itruediv__', True)
    #--- End: def

    def __ifloordiv__(self, other):
        '''

The augmented arithmetic assignment ``//=``

x.__ifloordiv__(y) <==> x//=y

'''
        return self._binary_arithmetic(other, '__ifloordiv__', True)
    #--- End: if

    def __imul__(self, other):
        '''

The augmented arithmetic assignment ``*=``

x.__imul__(y) <==> x *= y

'''
        return self._binary_arithmetic(other, '__imul__', True)
    #--- End: def

    def __radd__(self, other):
        '''

The binary arithmetic operation ``+`` with reflected operands

x.__radd__(y) <==> y+x

'''
        return self._binary_arithmetic(other, '__add__')
    #--- End: def

    def __rmul__(self, other):
        '''

The binary arithmetic operation ``*`` with reflected operands

x.__rmul__(y) <==> y*x

'''
        return self._binary_arithmetic(other, '__rmul__')
    #--- End: def

    def __rsub__(self, other):
        '''

The binary arithmetic operation ``-`` with reflected operands

x.__rsub__(y) <==> y-x

'''
        return self._binary_arithmetic(other, '__rsub__')
    #--- End: def

    def __mod__(self, other):
        '''

The binary arithmetic operation ``%``

x.__mod__(y) <==> x % y

'''   
        return self.duration % other
    #--- End: def

    def __rmod__(self, other):
        '''

The binary arithmetic operation ``%`` with reflected operands

x.__rmod__(y) <==> y % x

'''   
        return other % self.duration
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute
    # ----------------------------------------------------------------


    def _binary_arithmetic(self, other, method, inplace=False):
        '''
        '''
        if inplace:
            new = self
        else:
            new = self.copy()

        duration = getattr(new.duration, method)(other)

        duration.squeeze(i=True)

        if duration.size != 1:           
            raise ValueError("Can't create %s with more than one value: %s" %
                             (self.__class__.__name__, duration))

        if duration < 0:
            raise ValueError("Can't create %s with a negative duration" %
                             self.__class__.__name__)

        units = duration.Units          
        if not (units.iscalendartime or units.istime):
            raise ValueError("Can't create %s of %r" % 
                             (self.__class__.__name__, units))
            
        duration.Units = self.Units

        new.duration = duration

        return new
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def iso(self):
        '''Return the time duration as an ISO 8601 time duration string.

.. versionadded:: 1.0

:Examples:

>>> cf.TimeDuration(45, 'days').iso
'P45D'
>>> cf.TimeDuration(5, 'seconds').iso
'PT5S'
>>> cf.TimeDuration(10, 'calendar_years').iso
'P10Y'
>>> cf.TimeDuration(18, 'calendar_months').iso
'P18M'

'''
        duration = self.duration
        units    = duration.Units

        if units == _calendar_months:
            return 'P%dM' % duration.datum()
        if units == _calendar_years:
            return 'P%dY' % duration.datum()
        if units == _days:
            return 'P%sD' % duration.datum()
        if units == _hours:
            return 'PT%sH' % duration.datum()
        if units == _minutes:
            return 'PT%sM' % duration.datum()
        if units == _seconds:
            return 'PT%sS' % duration.datum()

        raise ValueError("jkbn p7hg un")
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def isint(self):
        '''True if the time duration is a whole number.

.. versionadded:: 1.0

:Examples:

>>> cf.TimeDuration(2, 'hours').isint
True
>>> cf.TimeDuration(2.0, 'hours').isint
True
>>> cf.TimeDuration(2.5, 'hours').isint
False

'''
        duration = self.duration

        if duration.dtype.kind == 'i':
            return True

        duration = duration.datum()
        return int(duration) == float(duration)
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute
    # ----------------------------------------------------------------
    @property
    def Units(self):
        '''The units of the time duration.

.. versionadded:: 1.0

:Examples:

>>> cf.TimeDuration(3, 'days').Units
<CF Units: days>
>>> t = cf.TimeDuration(cf.Data(12, 'calendar_months'))
>>> t.Units
<CF Units: calendar_months>
>>> t.Units = cf.Units('calendar_years')
>>> t.Units
<CF Units: calendar_years>
>>> t
<CF TimeDuration: 1.0 calendar_years (from Y-01-01 00:00:00)>

'''
        return self.duration.Units
    #--- End: def

    @Units.setter
    def Units(self, value):
        duration = getattr(self, 'duration', None)
        if duration is None:
            raise AttributeError("Can't set units when there is no duration attribute")

        self.duration.Units = value
    #--- End: def

    def copy(self):
        '''

Return a deep copy.

``t.copy()`` is equivalent to ``copy.deepcopy(t)``.

.. versionadded:: 1.0

:Returns:	

    out :
        The deep copy.

:Examples:

>>> u = t.copy()

'''
        new = TimeDuration.__new__(TimeDuration)

        new.year   = self.year  
        new.month  = self.month 
        new.day    = self.day   
        new.hour   = self.hour  
        new.minute = self.minute
        new.second = self.second

        new.duration = self.duration.copy()

        return new
    #--- End: def

    def equals(self, other, rtol=None, atol=None, traceback=False):
        '''

True if two time durations are equal.

.. seealso:: `equivalent`

.. versionadded:: 1.0

:Parameters:

    other : 
        The object to compare for equality.

    atol : float, optional
        The absolute tolerance for all numerical comparisons, By
        default the value returned by the `ATOL` function is used.

    rtol : float, optional
        The relative tolerance for all numerical comparisons, By
        default the value returned by the `RTOL` function is used.

    traceback : bool, optional
        If True then print a traceback highlighting where the two
        instances differ.

:Returns: 

    out : bool
        Whether or not the two instances are equal.

:Examples:

>>> t = cf.TimeDuration(36, 'calendar_months')
>>> u = cf.TimeDuration(3, 'calendar_years') 
>>> t == u
True
>>> t.equals(u, traceback=True)
TimeDuration: Different durations: <CF Data: 36 calendar_months>, <CF Data: 3 calendar_years>
False

'''       
        # Check each instance's id
        if self is other:
            return True
 
        # Check that each instance is the same type
        if self.__class__ != other.__class__:
            if traceback:
                print("%s: Different type: %s" %
                      (self.__class__.__name__, other.__class__.__name__))
            return False
        #--- End: if

        self__dict__  = self.__dict__.copy()
        other__dict__ = other.__dict__.copy()

        d0 = self__dict__.pop('duration', None)
        d1 = other__dict__.pop('duration', None)
        if not equals(d0, d1):
            if traceback:
                print("%s: Different durations: %r, %r" %
                      (self.__class__.__name__, d0, d1))
            return False
        #--- End: if

        if self__dict__ != other__dict__:
            if traceback:
                print("%s: Different The default date-time elements: %r != %r" %
                      (self.__class__.__name__, self__dict__, other__dict__))
            return False
        #--- End: if

        return True
    #--- End: def

    def equivalent(self, other, rtol=None, atol=None, traceback=False):
        '''

True if two time durations are logically equivalent.

.. seealso:: `equals`

.. versionadded:: 1.0

:Parameters:

    other : 
        The object to compare for equivalence.

    atol : float, optional
        The absolute tolerance for all numerical comparisons, By
        default the value returned by the `ATOL` function is used.

    rtol : float, optional
        The relative tolerance for all numerical comparisons, By
        default the value returned by the `RTOL` function is used.

    traceback : bool, optional
        If True then print a traceback highlighting where the two
        instances differ.

:Returns: 

    out : bool
        Whether or not the two instances logically equivalent.

:Examples:

>>> t = cf.TimeDuration(36, 'calendar_months')
>>> u = cf.TimeDuration(3, 'calendar_years') 
>>> t == u
True
>>> t.equivalent(u)
True
>>> t.equals(u, traceback=True)
TimeDuration: Different durations: <CF Data: 12 calendar_months>, <CF Data: 1 calendar_years>
False

'''       
        # Check each instance's id
        if self is other:
            return True
 
        # Check that each instance is the same type
        if self.__class__ != other.__class__:
            if traceback:
                print("%s: Different type: %s" %
                      (self.__class__.__name__, other.__class__.__name__))
            return False
        #--- End: if

        self__dict__  = self.__dict__.copy()
        other__dict__ = other.__dict__.copy()

        d0 = self__dict__.pop('duration', None)
        d1 = other__dict__.pop('duration', None)
        if d0 != d0:
            if traceback:
                print("%s: Non-equivalent durations: %r, %r" %
                      (self.__class__.__name__, d0, d1))
            return False
        #--- End: if

        if self__dict__ != other__dict__:
            if traceback:
                print("%s: Non-equivalent default date-time elements: %r != %r" %
                      (self.__class__.__name__, self__dict__, other__dict__))
            return False
        #--- End: if

        return True
    #--- End: def

    def inspect(self):
        '''

Inspect the attributes.

.. seealso:: `cf.inspect`

.. versionadded:: 1.0

:Returns: 

    None

:Examples:

>>> t=cf.TimeDuration(9, 'days')
>>> t.inspect()
<CF TimeDuration: 9 days (from Y-01-01 00:00:00)>
-------------------------------------------------
day: 1
duration: <CF Data: 9 days>
hour: 0
minute: 0
month: 1
second: 0
year: None

'''
        print cf_inspect(self)
    #--- End: def

    def interval(self, year=None, month=None, day=None, hour=None,
                 minute=None, second=None, end=False, calendar=None,
                 iso=None):
        '''Return a time interval of exactly the time duration.

The start (or end, if the *end* parameter is True) date-time of the
time interval is determined by the `!year`, `!month`, `!day`, `!hour`,
`!minute` and `!second` attributes.

.. versionadded:: 1.0

:Parameters:

    year, month, day, hour, minute, second : ints, optional
        The date-time of the start (or end) of the time interval. If
        any parameter is unset then its value defaults to the
        attribute of the same name. The time interval calculation
        requires that all of the parameters have numerical values, so
        if an unset parameter has a corresponding attribute default
        which is `None` then an exception will be raised.
        
          *Example:*
            ``t.interval(year=1999, day=16)`` is equivalent to
            ``t.interval(1999, t.month, 16, t.hour, t.minute,
            t.second)``.

    end : bool, optional
        If True then the date-time given by the *year*, *month*,
        *day*, *hour*, *minute* and *second* parameters defines the
        end of the time interval. By default it defines the start of
        the time interval.

    calendar : str, optional
        Define a CF calendar for the time interval. By default the
        Gregorian calendar is assumed. Ignored for time durations of
        calendar years or calendar months.

    iso : string, optional
        Return the time interval as an ISO 8601 time interval string
        rather than the default of a tuple of date-time objects. Valid
        values are (with example outputs for the time interval "3
        years from 2007-03-01 13:00:00"):

          ========================  =============================================
          iso                       Example output
          ========================  =============================================
          ``'start and end'``       ``'2007-03-01 13:00:00/2010-03-01 13:00:00'``
          ``'start and duration'``  ``'2007-03-01 13:00:00/P3Y'``
          ``'duration and end'``    ``'P3Y/2010-03-01 13:00:00'``
          ========================  =============================================

:Returns:

    out : 2-tuple of cf.Datetime or datetime.datetime; or str
        The date-times at each end of the time interval. The first
        date-time is always earlier than or equal to the second
        date-time. If *iso* has been set then an ISO 8601 time
        interval string is returned instead of a tuple.

:Examples:

>>> cf.TimeDuration(1, 'calendar_months').interval(1999, 12)
(<CF Datetime: 1999-12-01 00:00:00>, <CF Datetime: 2000-01-01 00:00:00>)

>>> cf.TimeDuration(2, 'calendar_years').interval(2000, 2, end=True)
(<CF Datetime: 1998-02-01 00:00:00>, <CF Datetime: 2000-02-01 00:00:00>)

>>> cf.TimeDuration(30, 'days').interval(1983, 12, 1, 6)
(<CF Datetime: 1983-12-01 06:00:00>, <CF Datetime: 1983-12-31 06:00:00>)

>>> cf.TimeDuration(30, 'days').interval(1983, 12, 1, 6, end=True)
(<CF Datetime: 1983-11-01 06:00:00>, <CF Datetime: 1983-12-01 06:00:00>)

>>> cf.TimeDuration(0, 'days').interval(1984, 2, 3)
(<CF Datetime: 1984-02-03 00:00:00>, <CF Datetime: 1984-02-03 00:00:00>)

>>> cf.TimeDuration(5, 'days', hour=6).interval(2004, 3, 2, end=True)
(<CF Datetime: 2004-02-26 06:00:00>, <CF Datetime: 2004-03-02 06:00:00>)

>>> cf.TimeDuration(5, 'days', hour=6).interval(2004, 3, 2, end=True, calendar='noleap')
(<CF Datetime: 2004-02-25 06:00:00>, <CF Datetime: 2004-03-02 06:00:00>)

>>> cf.TimeDuration(5, 'days', hour=6).interval(2004, 3, 2, end=True, calendar='360_day')
(<CF Datetime: 2004-02-27 06:00:00>, <CF Datetime: 2004-03-02 06:00:00>)

>>> cf.TimeDuration(19897.546, 'hours').interval(1984, 2, 3, 0)
(<CF Datetime: 1984-02-03 00:00:00>, <CF Datetime: 1986-05-12 01:32:46>)

>>> cf.TimeDuration(19897.546, 'hours').interval(1984, 2, 3, 0, end=True)
(<CF Datetime: 1981-10-26 22:27:14>, <CF Datetime: 1984-02-03 00:00:00>)

Create `cf.Query` objects for a time interval - one including both
bounds and one which excludes the upper bound:

>>> t = cf.TimeDuration(2, 'calendar_years')
>>> interval = t.interval(1999, 12)
>>> c = cf.wi(*interval)
>>> c
<CF Query: (wi [<CF Datetime: 1999-12-01 00:00:00>, <CF Datetime: 2001-01-01 00:00:00>])>
>>> d = cf.ge(interval[0]) & cf.lt(interval[1])
>>> d
<CF Query: [(ge <CF Datetime: 1999-12-01 00:00:00>) & (lt <CF Datetime: 2000-01-01 00:00:00>)]>
>>> c == cf.dt('2001-1-1')
True
>>> d == cf.dt('2001-1-1')
False

Create a `cf.Query` object which may be used to test where a time
coordinate object's bounds lie inside a time interval:

>>> t = cf.TimeDuration(1, 'calendar_months')
>>> c = cf.cellwi(*t.interval(2000, 1, end=True))
>>> c
<CF Query: [lower_bounds(ge <CF Datetime: 1999-12-01 00:00:00>) & upper_bounds(le <CF Datetime: 2000-01-01 00:00:00>)]>

Create ISO 8601 time interval strings:

>>> t = cf.TimeDuration(6, 'calendar_years')
>>> t.interval(1999, 12, end=True, iso='start and end') 
'1993-12-01 00:00:00/1999-12-01 00:00:00'
>>> t.interval(1999, 12, end=True, iso='start and duration')
'1993-12-01 00:00:00/P6Y'
>>> t.interval(1999, 12, end=True, iso='duration and end')
'P6Y/1999-12-01 00:00:00'

        '''   
        def _dHMS(duration, year, month, day, hour, minute, second, calendar):
            dt = Datetime(year, month, day, hour, minute, second)
            units = Units('%s since %s' % (duration.Units, dt), calendar)

            dt1 = Data(0.0, units) 

            if not end:
                dt1 += duration
            else:
                dt1 -= duration

            dt1 = dt1.asdatetime().datum()
            
            if not end:
                return dt, dt1
            else:
                return dt1, dt   
        #--- End: def

        if year is None:
            year = self.year
            if year is None:
                raise ValueError(
                    "year must have a value when creating a time interval")
        if month is None:
            month = self.month
            if month is None:
                raise ValueError(
                    "month must have a value when creating a time interval")
        if day is None:
            day = self.day
            if day is None:
                raise ValueError(
                    "day must have a value when creating a time interval")
        if hour is None:
            hour = self.hour
            if hour is None:
                raise ValueError(
                    "hour must have a value when creating a time interval")
        if minute is None:
            minute = self.minute
            if minute is None:
                raise ValueError(
                    "minute must have a value when creating a time interval")
        if second is None:
            second = self.second
            if second is None:
                raise ValueError(
                    "second must have a value when creating a time interval")
        
        duration = self.duration
        units    = duration.Units

        if units == _calendar_years:
            months = duration.datum() * 12
            int_months = int(months)
            if int_months != months:
                raise ValueError(
"Can't create a time interval of a non-integer number of calendar months: %s" % months)
        elif units == _calendar_months:
            months = duration.datum()
            int_months = int(months)
            if int_months != months:
                raise ValueError(
"Can't create a time interval of a non-integer number of calendar months: %s" % months)
        else:
            int_months = None

        if int_months is not None:
            if not end:
                y, month1 = divmod(month + int_months, 12)
                
                if not month1:
                    y -= 1
                    month1 = 12
                
                year1 = year + y
        
                dt0 = Datetime(year , month , day, hour, minute, second)
                dt1 = Datetime(year1, month1, day, hour, minute, second)
            else:
                y, month0 = divmod(month - int_months, 12)
                
                if not month0:
                    y -= 1
                    month0 = 12
                
                year0 = year + y
                
                dt0 = Datetime(year0, month0, day, hour, minute, second)
                dt1 = Datetime(year , month , day, hour, minute, second)

        elif units == _days:
            dt0, dt1 = _dHMS(duration, year, month, day, hour, minute, second, calendar)

        elif units == _hours:                                                
            dt0, dt1 = _dHMS(duration, year, month, day, hour, minute, second, calendar)
                                                                             
        elif units == _minutes:                                              
            dt0, dt1 = _dHMS(duration, year, month, day, hour, minute, second, calendar)
                                                                             
        elif units == _seconds:                                              
            dt0, dt1 = _dHMS(duration, year, month, day, hour, minute, second, calendar)

        if not iso:
            return dt0, dt1
             
        if iso == 'start and end':
            return '%s/%s' % (dt0, dt1)
        if iso == 'start and duration':
            return '%s/%s' % (dt0, self.iso)
        if iso == 'duration and end':
            return '%s/%s' % (self.iso, dt1)
    #--- End: def

    def is_day_factor(self):
        '''

:Returns:	

    out : bool

.. versionadded:: 1.0

:Examples:

>>> cf.TimeDuration(1, 'days').is_day_factor()
True
>>> cf.TimeDuration(0.25, 'days').is_day_factor()
True
>>> cf.TimeDuration(0.3, 'days').is_day_factor()
False
>>> cf.TimeDuration(2, 'days').is_day_factor()
False

>>> cf.TimeDuration(24, 'hours').is_day_factor()
True
>>> cf.TimeDuration(6, 'hours').is_day_factor()
True
>>> cf.TimeDuration(7, 'hours').is_day_factor()
False
>>> cf.TimeDuration(27, 'hours').is_day_factor()

>>> cf.TimeDuration(1440, 'minutes').is_day_factor()
True
>>> cf.TimeDuration(15, 'minutes').is_day_factor()
True
>>> cf.TimeDuration(17, 'minutes').is_day_factor()
False
>>> cf.TimeDuration(2007, 'minutes').is_day_factor()
False

>>> cf.TimeDuration(86400, 'seconds').is_day_factor()
True
>>> cf.TimeDuration(45, 'seconds').is_day_factor()
True
>>> cf.TimeDuration(47, 'seconds').is_day_factor()
False
>>> cf.TimeDuration(86401, 'seconds').is_day_factor()
False

>>> cf.TimeDuration(1, 'calendar_months').is_day_factor()
False
>>> cf.TimeDuration(1, 'calendar_years').is_day_factor()
False

'''
        try:
            return not cf.Data(1, 'day') % self.duration
        except ValueError:
            return False
#--- End: class

def Y(duration=1, year=None, month=1, day=1, hour=0, minute=0, second=0):
    '''Return a time duration of calendar years in a `cf.TimeDuration` object.

``cf.Y()`` is equivalent to ``cf.TimeDuration(1, 'calendar_year')``.

.. seealso:: `cf.M`, `cf.D`, `cf.h`, `cf.m`, `cf.s`

.. versionadded:: 1.0

:Parameters:

    duration : int, optional
        The number of calendar years in the time duration. Must be a
        non-negative integer.

    year, month, day, hour, minute, second : ints, optional
        The default date-time elements for defining the start and end
        of a time interval based on this time duration. See
        `cf.TimeDuration` and `cf.TimeDuration.interval` for details.

          *Example:*
            ``cf.Y(month=12)`` is equivalent to ``cf.TimeDuration(1,
            'calendar_years', month=12)``.

:Returns:

    out : cf.TimeDuration
        The new `cf.TimeDuration` object.

:Examples:

>>> cf.Y()
<CF TimeDuration: 1 calendar year (from Y-01-01 00:00:00)>

>>> cf.Y(10, month=12)   
<CF TimeDuration: 10 calendar years (from Y-12-01 00:00:00)>

>>> cf.Y(15, month=4, day=2, hour=12, minute=30, second=2)  
<CF TimeDuration: 15 calendar years (from Y-04-02 12:30:02)>

>>> cf.Y(0)       
<CF TimeDuration: 0 calendar years (from Y-01-01 00:00:00)>

    '''
    return TimeDuration(duration, 'calendar_years', year=year, month=month, day=day, 
                        hour=hour, minute=minute, second=second)
#--- End: def

def M(duration=1, year=None, month=1, day=1, hour=0, minute=0, second=0):
    '''Return a time duration of calendar months in a `cf.TimeDuration`
object.

``cf.M()`` is equivalent to ``cf.TimeDuration(1, 'calendar_month')``.

.. seealso:: `cf.Y`, `cf.D`, `cf.h`, `cf.m`, `cf.s`

.. versionadded:: 1.0

:Parameters:

    duration : int, optional
        The number of calendar months in the time duration. Must be a
        non-negative integer.

    year, month, day, hour, minute, second : ints, optional
        The default date-time elements for defining the start and end
        of a time interval based on this time duration. See
        `cf.TimeDuration` and `cf.TimeDuration.interval` for details.

          *Example:*
            ``cf.M(day=16)`` is equivalent to ``cf.TimeDuration(1,
            'calendar_months', day=16)``.

:Returns:

    out : cf.TimeDuration
        The new `cf.TimeDuration` object.

:Examples:

>>> cf.M()
<CF TimeDuration: 1 calendar month (from Y-MM-01 00:00:00)>

>>> cf.M(3, day=16)
<CF TimeDuration: 3 calendar months (from Y-MM-16 00:00:00)>

>>> cf.M(24, day=2, hour=12, minute=30, second=2)
<CF TimeDuration: 24 calendar months (from Y-MM-02 12:30:02)>

>>> cf.M(0)
<CF TimeDuration: 0 calendar months (from Y-MM-01 00:00:00)>

    '''
    return TimeDuration(duration, 'calendar_months', year=year, month=month, day=day, 
                        hour=hour, minute=minute, second=second)
#--- End: def

def D(duration=1, year=None, month=1, day=1, hour=0, minute=0, second=0):
    '''Return a time duration of days in a `cf.TimeDuration` object.

``cf.D()`` is equivalent to ``cf.TimeDuration(1, 'day')``.

.. seealso:: `cf.Y`, `cf.M`, `cf.h`, `cf.m`, `cf.s`

.. versionadded:: 1.0

:Parameters:

    duration : number, optional
        The number of days in the time duration. Must be non-negative.

    year, month, day, hour, minute, second : ints, optional
        The default date-time elements for defining the start and end
        of a time interval based on this time duration. See
        `cf.TimeDuration` and `cf.TimeDuration.interval` for details.

          *Example:*
             ``cf.D(hour=12)`` is equivalent to ``cf.TimeDuration(1,
             'day', hour=12)``.

:Returns:

    out : cf.TimeDuration
        The new `cf.TimeDuration` object.

:Examples:

>>> cf.D()
<CF TimeDuration: 1 day (from Y-MM-DD 00:00:00)>

>>> cf.D(5, hour=12)       
<CF TimeDuration: 5 days (from Y-MM-DD 12:00:00)>

>>> cf.D(48.5, minute=30)
<CF TimeDuration: 48.5 days (from Y-MM-DD 00:30:00)>

>>> cf.D(0.25, hour=6, minute=30, second=20)
<CF TimeDuration: 0.25 days (from Y-MM-DD 06:30:20)>

>>> cf.D(0)
<CF TimeDuration: 0 days (from Y-MM-DD 00:00:00)>

'''
    return TimeDuration(duration, 'days', year=year, month=month, day=day, 
                        hour=hour, minute=minute, second=second)
#--- End: def

def h(duration=1, year=None, month=1, day=1, hour=0, minute=0, second=0):
    '''Return a time duration of hours in a `cf.TimeDuration` object.

``cf.h()`` is equivalent to ``cf.TimeDuration(1, 'hour')``.

.. seealso:: `cf.Y`, `cf.M`, `cf.D`, `cf.m`, `cf.s`

.. versionadded:: 1.0

:Parameters:

    duration : number, optional
        The number of hours in the time duration. Must be non-negative.

    year, month, day, hour, minute, second : ints, optional
        The default date-time elements for defining the start and end
        of a time interval based on this time duration. See
        `cf.TimeDuration` and `cf.TimeDuration.interval` for details.

          *Example:*
            ``cf.h(minute=30)`` is equivalent to ``cf.TimeDuration(1,
            'hour', minute=30)``.

:Returns:

    out : cf.TimeDuration
        The new `cf.TimeDuration` object.

:Examples:

>>> cf.h()
<CF TimeDuration: 1 hour (from Y-MM-DD hh:00:00)>

>>> cf.h(3, minute=15)
<CF TimeDuration: 3 hours (from Y-MM-DD hh:15:00)>

>>> cf.h(0.5)
<CF TimeDuration: 0.5 hours (from Y-MM-DD hh:00:00)>

>>> cf.h(6.5, minute=15, second=45)
<CF TimeDuration: 6.5 hours (from Y-MM-DD hh:15:45)>

>>> cf.h(0)
<CF TimeDuration: 0 hours (from Y-MM-DD hh:00:00)>

'''
    return TimeDuration(duration, 'hours', year=year, month=month, day=day, 
                        hour=hour, minute=minute, second=second)
#--- End: def

def m(duration=1, year=None, month=1, day=1, hour=0, minute=0, second=0):
    '''Return a time duration of minutes in a `cf.TimeDuration` object.

``cf.m()`` is equivalent to ``cf.TimeDuration(1, 'minute')``.

.. seealso:: `cf.Y`, `cf.M`, `cf.D`, `cf.h`, `cf.s`

.. versionadded:: 1.0

:Parameters:

    duration : number, optional
        The number of hours in the time duration. Must be non-negative.

    year, month, day, hour, minute, second : ints, optional
        The default date-time elements for defining when a time
        interval based on this time duration begins or ends. See
        `cf.TimeDuration` and `cf.TimeDuration.interval` for details.

          *Example:*
            ``cf.m(second=30)`` is equivalent to ``cf.TimeDuration(1,
            'minute', second=30)``.

:Returns:

    out : cf.TimeDuration
        The new `cf.TimeDuration` object.

:Examples:

>>> cf.m()
<CF TimeDuration: 1 minute (from Y-MM-DD hh:mm:00)>

>>> cf.m(30, second=15)
<CF TimeDuration: 30 minutes (from Y-MM-DD hh:mm:15)>

>>> cf.m(0.5)
<CF TimeDuration: 0.5 minutes (from Y-MM-DD hh:mm:00)>

>>> cf.m(2.5, second=45)
<CF TimeDuration: 2.5 minutes (from Y-MM-DD hh:mm:45)>

>>> cf.m(0)
<CF TimeDuration: 0 minutes (from Y-MM-DD hh:mm:00)>

'''
    return TimeDuration(duration, 'minutes', year=year, month=month, day=day, 
                        hour=hour, minute=minute, second=second)
#--- End: def

def s(duration=1, year=None, month=1, day=1, hour=0, minute=0, second=0):
    '''Return a time duration of seconds in a `cf.TimeDuration` object.

``cf.s()`` is equivalent to ``cf.TimeDuration(1, 'second')``.

.. seealso:: `cf.Y`, `cf.M`, `cf.D`, `cf.h`, `cf.m`

.. versionadded:: 1.0

:Parameters:

    duration : number, optional
        The number of hours in the time duration. Must be
        non-negative.

    year, month, day, hour, minute, second : ints, optional
        The default date-time elements for defining the start and end
        of a time interval based on this time duration. See
        `cf.TimeDuration` and `cf.TimeDuration.interval` for details.

          *Example:*
            ``cf.s(hour=6)`` is equivalent to ``cf.TimeDuration(1,
            'seconds', hour=6)``.

:Returns:

    out : cf.TimeDuration
        The new `cf.TimeDuration` object.

:Examples:

>>> cf.s()   
<CF TimeDuration: 1 second (from Y-01-01 00:00:00)>

>>> cf.s().interval(1999, 12, 1)
(<CF Datetime: 1999-12-01 00:00:00>, datetime.datetime(1999, 12, 1, 0, 0, 1))

>>> cf.s(30)
<CF TimeDuration: 30 seconds (from Y-01-01 00:00:00)>

>>> cf.s(0.5)
<CF TimeDuration: 0.5 seconds (from Y-01-01 00:00:00)>

>>> cf.s(12.25)
<CF TimeDuration: 12.25 seconds (from Y-01-01 00:00:00)>

>>> cf.s(2.5, year=1999, hour=12)
<CF TimeDuration: 2.5 seconds (from 1999-01-01 12:00:00)>

>>> cf.s(0)
<CF TimeDuration: 0 seconds (from Y-01-01 00:00:00)>

'''
    return TimeDuration(duration, 'seconds', year=year, month=month, day=day, 
                        hour=hour, minute=minute, second=second)
#--- End: def
