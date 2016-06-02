
from datetime import datetime
import re
import sys

from dateutil import parser
import pytz
import six

from . text import levenshtein

UTC_EPOCH = datetime(1970, 1, 1).replace(tzinfo=pytz.utc)
MAX_POSIX_TIMESTAMP = pow(2, 32) - 1

DAYS = {
    'monday',
    'tuesday',
    'wednesday',
    'thursday',
    'friday',
    'saturday',
    'sunday'
}

DAYS_ABBR = [day[:3] for day in DAYS]


class timestamp_ms(object):
    """Build UTC timestamp in milliseconds
    """

    TIMEZONE_PARENTHESIS = re.compile('(.*)\(([a-zA-Z]+)[-+0-9:.]*\)$')
    TIMEZONE_SEPARATOR = re.compile('(.* .*)(\d\d)[.-](\d\d)$')
    QUOTED_TIMEZONE = re.compile("""(.*)['"]([\w:+-]+)['"]?$""")
    START_WITH_DAY_OF_WEEK = re.compile('^([a-zA-Z]*)[\s,](.*)')

    @classmethod
    def feeling_lucky(cls, obj):
        """Tries to convert given object to an UTC timestamp is ms, based
        on its type.
        """
        if isinstance(obj, six.string_types):
            return cls.from_str(obj)
        elif isinstance(obj, six.integer_types) and obj <= MAX_POSIX_TIMESTAMP:
            return cls.from_posix_timestamp(obj)
        elif isinstance(obj, datetime):
            return cls.from_datetime(obj)
        else:
            raise ValueError(
                u"Don't know how to get timestamp from '{}'".format(obj)
            )

    @classmethod
    def fix_mispelled_day(cls, timestr):
        """fix mispelled day when written in english

        :return: `None` if the day was not modified, the new date otherwise
        """
        day_extraction = cls.START_WITH_DAY_OF_WEEK.match(timestr)
        if day_extraction is not None:
            day = day_extraction.group(1).lower()
            if len(day) == 3:
                dataset = DAYS_ABBR
            else:
                dataset = DAYS
            if day not in dataset:
                days = list(dataset)
                days.sort(key=lambda e: levenshtein(day, e))
                return days[0] + day_extraction.group(2)

    @classmethod
    def remove_parenthesis_around_tz(cls, timestr):
        """get rid of parenthesis around timezone: (GMT) => GMT

        :return: the new string if parenthesis were found, `None` otherwise
        """
        parenthesis = cls.TIMEZONE_PARENTHESIS.match(timestr)
        if parenthesis is not None:
            return parenthesis.group(1)

    @classmethod
    def remove_quotes_around_tz(cls, timestr):
        """Remove quotes (single and double) around timezone otherwise
        `dateutil.parser.parse` raises
        """
        quoted = cls.QUOTED_TIMEZONE.match(timestr)
        if quoted is not None:
            return quoted.group(1) + quoted.group(2)

    @classmethod
    def remove_timezone(cls, timestr):
        """Completely remove timezone information, if any.

        :return: the new string if timezone was found, `None` otherwise
        """
        if re.match(r".*[\-+]?\d{2}:\d{2}$", timestr):
            return re.sub(
                r"(.*)(\s[\+-]?\d\d:\d\d)$",
                r"\1",
                timestr
            )

    @classmethod
    def fix_timezone_separator(cls, timestr):
        """Replace invalid timezone separator to prevent
        `dateutil.parser.parse` to raise.

        :return: the new string if invalid separators were found,
                 `None` otherwise
        """
        tz_sep = cls.TIMEZONE_SEPARATOR.match(timestr)
        if tz_sep is not None:
            return tz_sep.group(1) + tz_sep.group(2) + ':' + tz_sep.group(3)
        return timestr

    @classmethod
    def from_str(cls, timestr, shaked=False):
        """Use `dateutil` module to parse the give string

        :param basestring timestr: string representing a date to parse
        :param bool shaked: whether the input parameter been already
        cleaned or not.
        """
        orig = timestr
        if not shaked:
            timestr = cls.fix_timezone_separator(timestr)
        try:
            date = parser.parse(timestr)
        except ValueError:
            if not shaked:
                shaked = False
                for shaker in [
                        cls.fix_mispelled_day,
                        cls.remove_parenthesis_around_tz,
                        cls.remove_quotes_around_tz]:
                    new_timestr = shaker(timestr)
                    if new_timestr is not None:
                        timestr = new_timestr
                        shaked = True
                if shaked:
                    try:
                        return cls.from_str(timestr, shaked=True)
                    except ValueError:
                        # raise ValueError below with proper message
                        pass
            msg = u"Unknown string format: {!r}".format(orig)
            raise ValueError(msg), None, sys.exc_info()[2]
        else:
            try:
                return cls.from_datetime(date)
            except ValueError:
                new_str = cls.remove_timezone(orig)
                if new_str is not None:
                    return cls.from_str(new_str)
                else:
                    raise

    @classmethod
    def from_ymd(cls, year, month=1, day=1):
        return cls.from_datetime(datetime(
            year=year, month=month, day=day
        ))

    @classmethod
    def from_posix_timestamp(cls, ts):
        return cls.from_datetime(datetime.utcfromtimestamp(ts))

    @classmethod
    def from_datetime(cls, date):
        if date.tzinfo is None:
            date = date.replace(tzinfo=pytz.utc)
        seconds = (date - UTC_EPOCH).total_seconds() * 1e3
        micro_seconds = date.microsecond / 1e3
        return int(seconds + micro_seconds)

    @classmethod
    def now(cls):
        return cls.from_datetime(datetime.utcnow())
