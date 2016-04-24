#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse

from collections import namedtuple
from datetime import datetime, timedelta

import requests
import pytz

from icalendar import Calendar
from icalendar.prop import vDatetime

__all__ = ['print_ctf']

__CTFTIME_ICAL_URL='https://calendar.google.com/calendar/ical/ctftime%40gmail.com/public/basic.ics'

Cal = namedtuple('Cal', 'summary start end desc')


def __conv_vDDD_to_datetime(vddd, tz=pytz.utc):
    return vDatetime.from_ical(vddd.to_ical()).astimezone(tz)


def __get_cals(ical_url, now, interval=timedelta(weeks=2), tz=pytz.utc):
    ical_str = requests.get(ical_url).text
    ical = Calendar.from_ical(ical_str)

    target_cals = list()
    for c in ical.walk():
        if c.name == 'VEVENT':
            start = __conv_vDDD_to_datetime(c.get('DTSTART', None), tz)

            if now >= start:
                continue

            summary = c.get('SUMMARY', '')
            desc = c.get('DESCRIPTION', '')
            end = __conv_vDDD_to_datetime(c.get('DTEND', None), tz)

            target_cals.append(Cal(summary, start, end, desc))

    return sorted(filter(lambda x: x.start - now < interval, target_cals),
                  key=lambda x:x.start)


def print_ctf(interval=timedelta(weeks=2), tz=pytz.utc):
    date_format = '%Y/%m/%d(%a) %H:%M:%S'

    now = datetime.now(tz)

    for c in __get_cals(__CTFTIME_ICAL_URL, now, interval, tz):
        print c.summary
        print c.start.strftime(date_format), 'TO', \
              c.end.strftime(date_format)
        print c.desc


def __main():
    parser = argparse.ArgumentParser(
                description='Print recent CTF contests sourced by CTFTime.org')
    parser.add_argument('--weeks', dest='weeks', type=int, default=0,
                        help='DEFAULT 2 weeks')
    parser.add_argument('--days', dest='days', type=int, default=0)
    parser.add_argument('--timezone', dest='timezone', type=str,
                        default='UTC', help='DEFAULT UTC - ex. Asia/Tokyo (UTC+9)')
    p = parser.parse_args()

    interval = {
        'weeks': 2 if p.weeks == 0 and p.days == 0 else p.weeks,
        'days': p.days
    }

    print_ctf(timedelta(**interval), pytz.timezone(p.timezone))


if __name__ == '__main__':
    __main()

