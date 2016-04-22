from api_star.compat import text_type
import coreapi
import datetime
import decimal
import json
import re
import uuid


ZERO = datetime.timedelta(0)


class JSONEncoder(json.JSONEncoder):
    """
    JSONEncoder subclass that deals with various built-in types.
    """
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            representation = obj.isoformat()
            if representation.endswith('+00:00'):
                representation = representation[:-6] + 'Z'
            return representation
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, datetime.time):
            return obj.isoformat()
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, uuid.UUID):
            return text_type(obj)
        elif isinstance(obj, coreapi.Document):
            return dict(obj.items())
        elif isinstance(obj, coreapi.Link):
            return obj.url
        return super(JSONEncoder, self).default(obj)


class UTC(datetime.tzinfo):
    """
    UTC implementation taken from Python's docs.
    Used only when pytz isn't available.
    """

    def __repr__(self):
        return "<UTC>"

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO

    def __eq__(self, other):
        return self.utcoffset(None) == other.utcoffset(None)


class FixedOffset(datetime.tzinfo):
    """
    Fixed offset in minutes east from UTC. Taken from Python's docs.
    Kept as close as possible to the reference version. __init__ was changed
    to make its arguments optional, according to Python's requirement that
    tzinfo subclasses can be instantiated without arguments.
    """

    def __init__(self, offset=None, name=None):
        if offset is not None:
            self.__offset = datetime.timedelta(minutes=offset)
        if name is not None:
            self.__name = name

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return ZERO

    def __eq__(self, other):
        return self.utcoffset(None) == other.utcoffset(None)


utc = UTC()


def get_fixed_timezone(offset):
    """
    Returns a tzinfo instance with a fixed offset from UTC.
    """
    if isinstance(offset, datetime.timedelta):
        offset = offset.seconds // 60
    sign = '-' if offset < 0 else '+'
    hhmm = '%02d%02d' % divmod(abs(offset), 60)
    name = sign + hhmm
    return FixedOffset(offset, name)


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
    r'(?P<tzinfo>Z|[+-]\d{2}(?::?\d{2})?)?$'
)


def parse_iso8601_date(value):
    """
    Parses a string and return a datetime.date.

    Raises ValueError if the input is invalid.
    """
    match = date_re.match(value)
    if match:
        kw = {k: int(v) for k, v in match.groupdict().items()}
        return datetime.date(**kw)
    raise ValueError('Not a valid date format')


def parse_iso8601_time(value):
    """
    Parses a string and return a datetime.time.
    This function doesn't support time zone offsets.

    Raises ValueError if the input is invalid.
    """
    match = time_re.match(value)
    if match:
        kw = match.groupdict()
        if kw['microsecond']:
            kw['microsecond'] = kw['microsecond'].ljust(6, '0')
        kw = {k: int(v) for k, v in kw.items() if v is not None}
        return datetime.time(**kw)
    raise ValueError('Not a valid time format')


def parse_iso8601_datetime(value, default_timezone=None):
    """
    Parses a string and return a datetime.datetime.
    This function supports time zone offsets. When the input contains one,
    the output uses a timezone with a fixed offset from UTC.

    Raises ValueError if the input is invalid.
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
            offset_mins = int(tzinfo[-2:]) if len(tzinfo) > 3 else 0
            offset = 60 * int(tzinfo[1:3]) + offset_mins
            if tzinfo[0] == '-':
                offset = -offset
            tzinfo = get_fixed_timezone(offset)
        else:
            tzinfo = default_timezone
        kw = {k: int(v) for k, v in kw.items() if v is not None}
        kw['tzinfo'] = tzinfo
        return datetime.datetime(**kw)
    raise ValueError('Not a valid datetime format')


def parse_header_params(media_type):
    """
    Parse any media type parameters returning them as a dictionary.
    (Eg in Accept or Content-Type headers,)
    """
    main_type, sep, param_string = media_type.partition(';')
    params = {}
    for token in param_string.strip().split(','):
        key, sep, value = token.partition('=')
        key = key.strip()
        value = value.strip()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        if key:
            params[key] = value
    return params
