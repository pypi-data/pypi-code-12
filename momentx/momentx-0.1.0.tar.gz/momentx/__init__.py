# -*- encoding: utf-8 -*-
"""
MomentX
"""

__author__ = "Ulf Bartel <elastic.code@gmail.com>"
__version__ = "0.1.4"
__copyright__ = "Copyright (c) Ulf Bartel / Zach Williams"
__license__ = "New-style BSD"
__url__ = "https://github.com/berlincode/momentx"

import os, pytz
from datetime import datetime

from .date import add, replace
from .core import parse_date, get_timezone

# you may use the tzlocal module to set local timezone
DEFAULT_TIMEZONE = os.environ.get('TZ', 'UTC')
DEFAULT_DATETIME_FORMAT_TZ = '%Y-%m-%d %H:%M:%S%z'

class MomentX(object):
    """A class to abstract date difficulties.
    """

    def __init__(self, *args, **kwargs):
        self._zero = kwargs.pop("zero", False)

        formula = None
        if len(args) == 1:
            date = args[0]
        elif len(args) == 2:
            date = args[0]
            formula = args[1]
        else:
            date = args

        if not date:
            # if no date is supplied take "now"
            date = datetime.utcnow().replace(tzinfo=pytz.utc)

        date = parse_date(date, formula, timezone=kwargs.get('timezone', None))

        self._date = date

    @classmethod
    def date(cls, *args, **kwargs):
        """Create a moment using the default timezone as default."""
        return cls(*args, timezone=kwargs.get("timezone", DEFAULT_TIMEZONE))

    @classmethod
    def now(cls, **kwargs):
        """Create a date from the present time."""
        return cls(timezone=kwargs.get("timezone", DEFAULT_TIMEZONE))

    @classmethod
    def utc(cls, *args, **kwargs): # pylint:disable=no-self-use
        """Create a date using the UTC time zone as default."""
        return cls(*args, timezone=kwargs.get("timezone", "UTC"))

    @classmethod
    def utcnow(cls): # pylint:disable=no-self-use
        """UTC equivalent to `now` function."""
        return cls(timezone="UTC")

    def add(self, key=None, amount=None, **kwds):
        """Add time to moment."""
        date = add(self._date, key=key, amount=amount, **kwds)
        return MomentX(date)

    def sub(self, key=None, amount=None, **kwds):
        """Just in case."""
        return self.subtract(key, amount, **kwds)

    def subtract(self, key=None, amount=None, **kwds):
        """Subtract time from the original moment."""
        return self.add(key=key, amount=amount, factor=-1, **kwds)

    def replace(self, **kwds):
        """A Pythonic way to replace various date attributes."""
        date = replace(self._date, **kwds)
        return MomentX(date)

    def zero(self):
        """Get rid of hour, minute, second, and microsecond information."""
        date = replace(self._date, hours=0, minutes=0, seconds=0, microseconds=0)
        return MomentX(date, zero=True)

    def astimezone(self, timezone="UTC"):
        """ change timezone """
        date = self._date.astimezone(get_timezone(timezone))
        return MomentX(date)

    def isoformat(self):
        """Return the date's ISO 8601 string."""
        return self._date.isoformat()

    def strftime(self, formula):
        """Display the moment in a given format."""
        return self._date.strftime(formula)

    def __repr__(self):
        if self._date is not None:
            return "<Moment(%s / %s)>" % (str(self), str(self._date.tzinfo))
        return "<Moment>"

    def __str__(self):
        # we want our default datetime representation without the timezone
        return self._date.strftime(DEFAULT_DATETIME_FORMAT_TZ)

    @property
    def year(self):
        return self._date.year

    @property
    def month(self):
        return self._date.month

    @property
    def day(self):
        return self._date.day

    @property
    def weekday(self):
        return self._date.isoweekday()

    @property
    def hour(self):
        return self._date.hour

    @property
    def hours(self):
        return self._date.hour

    @property
    def minute(self):
        return self._date.minute

    @property
    def minutes(self):
        return self._date.minute

    @property
    def second(self):
        return self._date.second

    @property
    def seconds(self):
        return self._date.second

    @property
    def microsecond(self):
        return self._date.microsecond

    @property
    def microseconds(self):
        return self._date.microsecond

    @property
    def tzinfo(self):
        return str(self._date.tzinfo)

    # pylint:disable=protected-access
    def __lt__(self, other):
        if isinstance(other, datetime):
            return self._date < other
        elif isinstance(other, type(self)):
            return self._date < other._date

    def __le__(self, other):
        if isinstance(other, datetime):
            return self._date <= other
        elif isinstance(other, type(self)):
            return self._date <= other._date

    def __eq__(self, other):
        if isinstance(other, datetime):
            return self._date == other
        elif isinstance(other, type(self)):
            return self._date == other._date

    def __ne__(self, other):
        if isinstance(other, datetime):
            return self._date != other
        elif isinstance(other, type(self)):
            return self._date != other._date

    def __gt__(self, other):
        if isinstance(other, datetime):
            return self._date > other
        elif isinstance(other, type(self)):
            return self._date > other._date

    def __ge__(self, other):
        if isinstance(other, datetime):
            return self._date >= other
        elif isinstance(other, type(self)):
            return self._date >= other._date
    # pylint:enable=protected-access
