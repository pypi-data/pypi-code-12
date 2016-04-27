from zope.interface import Interface, Attribute
from zope.schema.interfaces import IMinMax, IField


class IMonthClass(Interface):
    """Static methods of Month"""

    def current():
        """Return a month instance for the current month."""

    def fromString(string):
        """Get instance from a string.

        Raises ValueError if not convertable to month.
        """


class IMonth(Interface):
    """A datatype which stores a year and a month."""

    month = Attribute(
        'Month part of the date. Must be an int between 1 and 12')
    year = Attribute('Four digit year.')

    def __cmp__(other):
        """Compare to other.

        If other is not adaptable to IMonth it is always less than self.
        """

    def isBetween(a, b):
        r"""Test if the month is between two other months

        self \element [a,b]

        if a or b is None, the interval is open in this direction

        if a or b not an IMonth or None, raises TypeError

        DEPRECATED: Use `month in month_interval` instead.

        """

    def firstOfMonth():
        """Get the date object which represents the first day of the month."""

    def lastOfMonth():
        """Get the date object which represents the last day of the month."""

    def __sub__(other):
        """Substract from this month.

        Given an `int` compute a previous month.
        Given an `IMonth` compute the interval.

        """

    def __add__(months):
        """Add a given number of months."""

    def __str__():
        """Return a string representation."""

    def __hash__():
        """Return the hash."""

    def __iter__():
        """Return an iterator over the days of the month.

        Represents each day as a datetime.date.
        """

    def __contains__(date):
        """Return whether the `date` is in the month."""


class IMonthInterval(Interface):
    """represents an interval between two months"""

    def intersects(other):
        """check if the given interval has an intersection"""

    def normalized():
        """Create a normalized form of this interval.

        The following conditions apply to normalized intervals:

        - start <= end

        """

    def __iter__():
        """Iterate over all months that are in the interval,

        Including start and end.
        """

    def __contains__(month):
        """Return true if the given month is within the interval."""

    def __len__():
        """Return the number of months in the normalized interval.

        An interval with the same start and end has the length of 1!
        """

    def forYear(year):
        """(classmethod) Returns an interval of months for the given year."""


class IMonthField(IMinMax, IField):
    u"""Field containing a Month."""


class IDate(Interface):
    """A date containing of month and year.

    This is provided by `datetime.date` and can be adapted to `IMonth`.
    """

    month = Attribute('month')
    year = Attribute('year')
