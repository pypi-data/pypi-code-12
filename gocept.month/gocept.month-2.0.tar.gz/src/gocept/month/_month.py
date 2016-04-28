from gocept.month.interfaces import IMonth
import datetime
import functools
import gocept.month
import re
import zope.interface


@zope.interface.implementer(IMonth)
@functools.total_ordering
class Month(object):
    """A datatype which stores a year and a month.

    >>> from zope.interface.verify import verifyObject
    >>> verifyObject(IMonth, Month(11, 1977))
    True
    """

    month = property(lambda self: self.__month)
    year = property(lambda self: self.__year)

    def __init__(self, month, year):
        """Constructor

        >>> Month()
        Traceback (most recent call last):
        ...
        TypeError: __init__() ... arguments...
        >>> Month(13,2005)
        Traceback (most recent call last):
        ...
        ValueError: Month must be between 1 and 12.
        >>> Month(0,2005)
        Traceback (most recent call last):
        ...
        ValueError: Month must be between 1 and 12.
        >>> Month(11,2005)
        Month 11/2005
        >>> Month(11,5)
        Month 11/5
        >>> Month(11,99)
        Month 11/99
        >>> Month(11,-20)
        Traceback (most recent call last):
        ...
        ValueError: Year must be at least 1.
        """
        month = int(month)
        if not(1 <= month <= 12):
            raise ValueError('Month must be between 1 and 12.')
        self.__month = month

        year = int(year)
        if year <= 0:
            raise ValueError("Year must be at least 1.")
        self.__year = year

    def __repr__(self):
        return "Month %s/%s" % (self.month, self.year)

    def __eq__(self, other):
        """Compare for equality. Not implementing IMonth means inequality."""
        try:
            other = IMonth(other)
        except TypeError:
            return False
        else:
            return (self.year, self.month) == (other.year, other.month)

    def __gt__(self, other):
        """Compare for strict ordering (greater than other).

        If other is not adaptable to IMonth it is considered a TypeError.

        """
        other = IMonth(other)
        return (self.year, self.month) > (other.year, other.month)

    date_regex = re.compile(r"^([0-9]{1,2})[,./-]?([0-9]{2}|[0-9]{4})$")

    @classmethod
    def current(cls):
        """Return a month instance for the current month.

        >>> Month.current() # doctest: +ELLIPSIS
        Month .../...

        """
        now = datetime.date.today()
        return Month(now.month, now.year)

    @classmethod
    def fromString(cls, string):
        """Get instance from a string. The Month must come first in string.

        >>> Month.fromString('11/2005')
        Month 11/2005
        >>> Month.fromString('11.2005')
        Month 11/2005
        >>> Month.fromString('11-2005')
        Month 11/2005
        >>> Month.fromString('11.2005')
        Month 11/2005
        >>> Month.fromString('1.2005')
        Month 1/2005
        >>> Month.fromString('01.2005')
        Month 1/2005
        >>> Month.fromString('11.05')
        Month 11/2005
        >>> Month.fromString('11/05')
        Month 11/2005
        >>> Month.fromString('1105')
        Month 11/2005
        >>> Month.fromString('112005')
        Month 11/2005
        >>> Month.fromString('105')
        Month 1/2005
        >>> Month.fromString('12005')
        Month 1/2005
        >>> Month.fromString('0105')
        Month 1/2005
        >>> Month.fromString('0501')
        Month 5/2001
        >>> Month.fromString('012005')
        Month 1/2005

        Empty strings result in None instead of a Month instance

        >>> Month.fromString('') is None
        True

        Format Errors result in a ValueError

        >>> Month.fromString('2005-11')
        Traceback (most recent call last):
        ...
        ValueError: Date must be MM/YYYY.
        """
        if string == '':
            return None
        result = cls.date_regex.match(string)
        if result is None:
            raise ValueError('Date must be MM/YYYY.')
        month, year = result.groups()
        if len(year) == 2:
            year = "20%s" % year
        return Month(int(month), int(year))

    def firstOfMonth(self):
        """Get the datetime.date which represents the first day of the month.

        >>> Month(11, 2005).firstOfMonth()
        datetime.date(2005, 11, 1)
        >>> Month(1, 2000).firstOfMonth()
        datetime.date(2000, 1, 1)
        """
        return datetime.date(self.year, self.month, 1)

    def lastOfMonth(self):
        """Get the datetime.date which represents the last day of the month.

        >>> Month(11, 2005).lastOfMonth()
        datetime.date(2005, 11, 30)
        >>> Month(12, 2005).lastOfMonth()
        datetime.date(2005, 12, 31)
        >>> Month(2, 2008).lastOfMonth()
        datetime.date(2008, 2, 29)
        """
        next_month = self + 1
        return next_month.firstOfMonth() - datetime.timedelta(days=1)

    def __sub__(self, other):
        """Substract from this month.

        Given an `int` a previous month is computed:

        >>> Month(11, 2005) - 10
        Month 1/2005
        >>> Month(1, 2005) - 13
        Month 12/2003
        >>> Month(1, 2005) - 5
        Month 8/2004

        Given an `IMonth` an interval is computed:

        >>> Month(11, 2005) - Month(1, 2005)
        <MonthInterval from Month 11/2005 to Month 1/2005>
        >>> Month(1, 2005) - Month(11, 2005)
        <MonthInterval from Month 1/2005 to Month 11/2005>

        Trying to subtract other types raises an error:
        >>> Month(11, 2005) - '1'
        Traceback (most recent call last):
        TypeError: Can't subtract <... 'str'> from month.

        """
        if isinstance(other, int):
            months = other
            year = self.year - (months // 12)
            month = self.month - months % 12
            if month <= 0:
                year -= 1
                month += 12
            return Month(month, year)
        elif IMonth.providedBy(other):
            return gocept.month.MonthInterval(self, other)
        raise TypeError("Can't subtract %r from month." % type(other))

    def __add__(self, months):
        """Add months and return a new IMonth.

        >>> m1 = Month(12,2005)
        >>> m2 = Month(1,2005)
        >>> m1 + 1
        Month 1/2006
        >>> m2 + 1
        Month 2/2005
        >>> m2 + 13
        Month 2/2006
        """
        return self - (-months)

    def __str__(self):
        """Returns a string representation.

        >>> str(Month(10,2000))
        '10/2000'
        >>> str(Month(1,2005))
        '01/2005'
        """
        return "%02i/%s" % (self.month, self.year)

    def __hash__(self):
        """Returns the hash.

        Make sure Month is immutable:

        >>> Month(5,2003).year = 2005
        Traceback (most recent call last):
        ...
        AttributeError: can't set attribute
        >>> Month(5,2003).month = 4
        Traceback (most recent call last):
        ...
        AttributeError: can't set attribute

        Check the hash

        >>> hash(Month(10,2000))
        102000
        >>> hash(Month(1,2005))
        12005
        >>>
        """
        return int("%s%s" % (self.month, self.year))

    def __iter__(self):
        """Returns an iterator over the days of the month.

        Represents each day as a datetime.date.

        >>> days = iter(Month(5, 2009))
        >>> next(days)
        datetime.date(2009, 5, 1)
        >>> next(days)
        datetime.date(2009, 5, 2)
        >>> for day in days: pass
        >>> day
        datetime.date(2009, 5, 31)

        """
        return (datetime.date(self.year, self.month, day)
                for day in range(1, self.lastOfMonth().day + 1))

    def __contains__(self, date):
        """Returns whether the `date` is in the month.

        >>> import datetime
        >>> datetime.date(2009, 4, 30) in Month(5, 2009)
        False
        >>> datetime.date(2009, 5, 1) in Month(5, 2009)
        True
        >>> datetime.date(2009, 5, 2) in Month(5, 2009)
        True
        >>> datetime.date(2009, 5, 31) in Month(5, 2009)
        True
        >>> datetime.date(2009, 6, 1) in Month(5, 2009)
        False
        >>> datetime.date(2012, 2, 29) in Month(2, 2012)
        True
        >>> datetime.datetime(2012, 2, 29, 15, 7, 34) in Month(2, 2012)
        True
        >>> object() in Month(2, 2012)
        False

        """
        if not isinstance(date, datetime.date):
            return False
        return date.year == self.year and date.month == self.month
