
"""
Based on RFC5322
"""


import re
import datetime

import wayround_org.utils.datetime_iso8601


DATE_EXPRESSION = (
    r'\s*'
    r'(?P<day>\d+)'
    r'\s+'
    r'(?P<month>[a-zA-Z]{3})'
    r'\s+'
    r'(?P<year>\d+)'
    r'\s*'
    )

TIMEOFDAY_EXPRESSION = (
    r'\s*'
    r'(?P<hour>\d+)'
    r'\:(?P<minute>\d+)'
    r'(\:(?P<second>\d+))?'
    r'\s*'
    )

ZONE_EXPRESSION = (
    r'\s*'
    r'(?P<zone_sign>[+-]?)'
    r'(?P<zone_val>(?P<zone_hours>\d{2})(?P<zone_minutes>\d{2}))'
    r'\s*'
    )

TIME_EXPRESSION = (
    r'\s*'
    r'(?P<timeofday>{timeofday})'
    r'\s+'
    r'(?P<zone>{zone})'
    r'\s*'.format(
        timeofday=TIMEOFDAY_EXPRESSION,
        zone=ZONE_EXPRESSION
        )
    )

DATETIME_EXPRESSION = (
    r'\s*'
    r'((?P<dayofweek>[a-zA-Z]{{3}})\,)?'
    r'\s+'
    r'(?P<date>{date})'
    r'\s+'
    r'(?P<time>{time})'
    r'\s*'
    r'').format(
    date=DATE_EXPRESSION,
    time=TIME_EXPRESSION
    )


DATETIME_EXPRESSION_C = re.compile(DATETIME_EXPRESSION)

MONTHES = [
    "Jan", "Feb", "Mar", "Apr",
    "May", "Jun", "Jul", "Aug",
    "Sep", "Oct", "Nov", "Dec"
    ]

DAYSOFWEEK = [
    "Mon", "Tue", "Wed", "Thu",
    "Fri", "Sat", "Sun"
    ]


def str_to_datetime(value):
    """
    Parse string and make datetime.datetime of it
    """

    if not isinstance(value, str):
        raise TypeError("`value' must be inst of str")

    ret = None

    ret_attributes = set()
    re_res = DATETIME_EXPRESSION_C.match(value)

    if re_res:

        month = MONTHES.index(re_res.group('month')) + 1

        second = re_res.group('second')
        if second is None:
            second = 0
        else:
            second = int(second)
            ret_attributes.add('second')

        zonesign = '+'
        if re_res.group('zone_sign') == '-':
            zonesign = '-'

        tzinfo = wayround_org.utils.datetime_iso8601.gen_tz(
            int(re_res.group('zone_hours')),
            int(re_res.group('zone_minutes')),
            plus=zonesign == '+'
            )

        result = datetime.datetime(
            year=int(re_res.group('year')),
            month=month,
            day=int(re_res.group('day')),
            hour=int(re_res.group('hour')),
            minute=int(re_res.group('minute')),
            second=second,
            tzinfo=tzinfo
            )

        if re_res.group('dayofweek') is not None:
            ret_attributes.add('dayofweek')

        ret = result

    return ret, ret_attributes


def datetime_to_str(value, attrs=None):

    if not isinstance(value, datetime.datetime):
        raise TypeError("`value' must be inst of datetime.datetime")

    if not hasattr(value, 'tzinfo') or value.tzinfo is None:
        raise ValueError("supplied datetime must have time zone info")

    if attrs is None:
        attrs = set(['dayofweek', 'second'])

    dayofweek = ''
    if 'dayofweek' in attrs:
        dayofweek = '{}, '.format(DAYSOFWEEK[value.date().weekday()])

    second = ''
    if 'second' in attrs:
        second = ':{:02d}'.format(value.second)

    month = MONTHES[value.month - 1]

    zone = wayround_org.utils.datetime_iso8601.format_tz(
        value.tzinfo,
        sep=False
        )

    ret = (
        '{dayofweek}'
        '{day:02d} {month} {year:04d} '
        '{hour:02d}:{minute:02d}{second} {zone}'
        ).format(
            dayofweek=dayofweek,
            day=value.day,
            month=month,
            year=value.year,
            hour=value.hour,
            minute=value.minute,
            second=second,
            zone=zone
            )

    return ret


def str_parse_test():
    """
    run tests if datetime string parser
    """

    tests = [
        'Fri, 29 Jan 2016 13:36:08 +0200'
        ]

    for value in tests:

        print("test subject: {}".format(value))

        re_res = DATETIME_EXPRESSION_C.match(value)

        if re_res:

            for i in [
                    'dayofweek',
                    'day', 'month', 'year',
                    'hour', 'minute', 'second',
                    'zone_sign', 'zone_val',
                    'zone_hours', 'zone_minutes']:
                print("    {:20}: {}".format(i, re_res.group(i)))

            dt, attrs = str_to_datetime(value)

            print(
                "    {:20}: {}".format(
                    'iso8601',
                    wayround_org.utils.datetime_iso8601.datetime_to_str(
                        dt
                        )
                    )
                )

            print(
                "    {:20}: {}".format(
                    'rendered',
                    datetime_to_str(
                        dt
                        )
                    )
                )
        else:
            print("    parse error")
    return
