import re
import six
from pytz import utc
from datetime import datetime, date, time, timedelta, tzinfo


date_re = re.compile(
    r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})$'
)

time_re = re.compile(
    r'(?P<hour>\d{1,2}):(?P<minute>\d{1,2})'
    r'(?::(?P<second>\d{1,2})(?:\.(?P<microsecond>\d{1,6})\d{0,6})?)?'
)

datetime_re = re.compile(
    r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})'
    r'[T ](?P<hour>\d{1,2}):(?P<minute>\d{1,2})'
    r'(?::(?P<second>\d{1,2})(?:\.(?P<microsecond>\d{1,6})\d{0,6})?)?'
    r'(?P<tzinfo>Z|[+-]\d{2}:?\d{2})?$'
)


class FormatError(Exception):
    """
        Raised when date input is not well formatted.
    """
    pass


class FixedOffset(tzinfo):
    "Fixed offset in minutes east from UTC."
    def __init__(self, offset):
        if isinstance(offset, timedelta):
            self.offset = offset
            offset = self.offset.seconds // 60
        else:
            self.offset = timedelta(minutes=offset)

        self.name = "%s%02d%02d" % (
            '-' if offset < 0 else '+',
            abs(offset) / 60.,
            abs(offset) % 60
        )

    def __repr__(self):
        return self.name

    def __getinitargs__(self):
        return self.offset,

    def utcoffset(self, dt):
        return self.offset

    def tzname(self, dt):
        return self.name

    def dst(self, dt):
        return timedelta(0)


def parse_date(value):
    """
        Parses a string and return a datetime.date.
        Raises ValueError if the input is well formatted but not a valid date.
        Raises FormatError if input is not well formatted.
    """
    match = date_re.match(value)
    if match:
        kw = dict((k, int(v)) for k, v in six.iteritems(match.groupdict()))
        return date(**kw)
    else:
        raise FormatError("Not well formatted: %s" % (value,))


def parse_time(value):
    """
    Parses a string and return a datetime.time.

    This function doesn't support time zone offsets.

    Raises ValueError if the input is well formatted but not a valid time.
    Raises FormatError if the input isn't well formatted, in particular if it
    contains an offset.
    """
    match = time_re.match(value)
    if match:
        kw = match.groupdict()
        if kw['microsecond']:
            kw['microsecond'] = kw['microsecond'].ljust(6, '0')
        kw = dict((k, int(v)) for k, v in six.iteritems(kw) if v is not None)
        return time(**kw)
    else:
        raise FormatError("Not well formatted: %s" % (value,))


def parse_datetime(value):
    """
    Parses a string and return a datetime.datetime.

    This function supports time zone offsets. When the input contains one,
    the output uses an instance of FixedOffset as tzinfo.

    Raises ValueError if the input is well formatted but not a valid datetime.
    Raises FormatError if the input isn't well formatted.
    """
    match = datetime_re.match(value)
    if match:
        kw = match.groupdict()
        if kw['microsecond']:
            kw['microsecond'] = kw['microsecond'].ljust(6, '0')
        tzinfo = kw.pop('tzinfo')
        if tzinfo == 'Z':
            tzinfo = utc
        elif tzinfo is not None:
            offset = 60 * int(tzinfo[1:3]) + int(tzinfo[-2:])
            if tzinfo[0] == '-':
                offset = -offset
            tzinfo = FixedOffset(offset)
        kw = dict((k, int(v)) for k, v in six.iteritems(kw) if v is not None)
        kw['tzinfo'] = tzinfo
        return datetime(**kw)
    else:
        raise FormatError("Not well formatted: %s" % (value,))
