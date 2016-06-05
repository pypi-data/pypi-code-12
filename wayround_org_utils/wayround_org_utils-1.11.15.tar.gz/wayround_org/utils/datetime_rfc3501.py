
"""
Based on RFC3501
"""


import re
import datetime

import wayround_org.utils.datetime_iso8601


DATE_EXPRESSION = (
    r'\s*'
    r'(?P<day>(\s|\d)?\d)'
    r'-'
    r'(?P<month>[a-zA-Z]{3})'
    r'-'
    r'(?P<year>\d+)'
    r'\s*'
    )

DATE_EXPRESSION_C = re.compile(DATE_EXPRESSION)

ZONE_EXPRESSION = (
    r'\s*'
    r'(?P<zone_sign>[+-]?)'
    r'(?P<zone_val>(?P<zone_hours>\d{2})(?P<zone_minutes>\d{2}))'
    r'\s*'
    )

TIME_EXPRESSION = (
    r'\s*'
    r'(?P<hour>\d+)'
    r'\:(?P<minute>\d+)'
    r'\:(?P<second>\d+)'
    r'\s*'
    )

DATETIME_EXPRESSION = (
    r'\s*'
    r'(?P<date>{date})'
    r'\s+'
    r'(?P<time>{time})'
    r'\s+'
    r'(?P<zone>{zone})'
    r'\s*'
    r''
    ).format(
        date=DATE_EXPRESSION,
        time=TIME_EXPRESSION,
        zone=ZONE_EXPRESSION
        )

DATETIME_EXPRESSION_C = re.compile(DATETIME_EXPRESSION)

MONTHES = [
    "Jan", "Feb", "Mar", "Apr",
    "May", "Jun", "Jul", "Aug",
    "Sep", "Oct", "Nov", "Dec"
    ]


def str_to_date(value):
    """
    Parse string and make datetime.date of it
    """

    if not isinstance(value, str):
        raise TypeError("`value' must be inst of str")

    ret = None

    ret_attributes = set()
    re_res = DATE_EXPRESSION_C.match(value)

    if re_res:

        month = MONTHES.index(re_res.group('month')) + 1

        day = re_res.group('day')
        if len(day) == 2 and day[0] == ' ':
            ret_attributes.add('day_fixed')

        result = datetime.date(
            year=int(re_res.group('year')),
            month=month,
            day=int(day)
            )

        ret = result

    return ret, ret_attributes


def date_to_str(value, attrs=None):

    if not isinstance(value, datetime.date):
        raise TypeError("`value' must be inst of datetime.date")

    if attrs is None:
        attrs = set()

    month = MONTHES[value.month - 1]

    if value.day < 10 and 'day_fixed' in attrs:
        day_str = ' {}'.format(value.day)
    else:
        day_str = str(value.day)

    ret = '{day}-{month}-{year:04d}'.format(
        day=day_str,
        month=month,
        year=value.year
        )

    return ret


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

        zonesign = '+'
        if re_res.group('zone_sign') == '-':
            zonesign = '-'

        tzinfo = wayround_org.utils.datetime_iso8601.gen_tz(
            int(re_res.group('zone_hours')),
            int(re_res.group('zone_minutes')),
            plus=zonesign == '+'
            )

        day = re_res.group('day')
        if len(day) == 2 and day[0] == ' ':
            ret_attributes.add('day_fixed')

        result = datetime.datetime(
            year=int(re_res.group('year')),
            month=month,
            day=int(day),
            hour=int(re_res.group('hour')),
            minute=int(re_res.group('minute')),
            second=int(re_res.group('second')),
            tzinfo=tzinfo
            )

        ret = result

    return ret, ret_attributes


def datetime_to_str(value, attrs=None):

    if not isinstance(value, datetime.datetime):
        raise TypeError("`value' must be inst of datetime.datetime")

    if not hasattr(value, 'tzinfo') or value.tzinfo is None:
        raise ValueError("supplied datetime must have time zone info")

    if attrs is None:
        attrs = set()

    month = MONTHES[value.month - 1]

    zone = wayround_org.utils.datetime_iso8601.format_tz(
        value.tzinfo,
        sep=False
        )

    if value.day < 10 and 'day_fixed' in attrs:
        day_str = ' {}'.format(value.day)
    else:
        day_str = str(value.day)

    ret = (
        '{day}-{month}-{year:04d} '
        '{hour:02d}:{minute:02d}:{second:02d} {zone}'
        ).format(
            day=day_str,
            month=month,
            year=value.year,
            hour=value.hour,
            minute=value.minute,
            second=value.second,
            zone=zone
            )

    return ret


def str_parse_test():
    """
    run tests if datetime string parser
    """

    tests = [
        '29-Jan-2016 13:36:08 +0200',
        '9-Jan-2016 13:36:08 +0200',
        ]

    for value in tests:

        print("test subject: {}".format(value))

        re_res = DATETIME_EXPRESSION_C.match(value)

        if re_res:

            for i in [
                    'day', 'month', 'year',
                    'hour', 'minute', 'second',
                    'zone_sign', 'zone_val',
                    'zone_hours', 'zone_minutes']:
                print("    {:20}: {}".format(i, re_res.group(i)))

            dt = str_to_datetime(value)[0]

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
