# -*- coding: utf-8 -*-

import dateparser
import re

from collections import namedtuple

DateRange = namedtuple('DateRange', 'start end dates')


def parse(value, max_days=15):
    """
    parse single or double dates ignoring times
    """

    separators = ['-', ' to ', ' at ']

    date_pieces = [piece.strip() for piece in re.split("|".join(separators),value)]

    # strip out time
    for k,v in enumerate(date_pieces):

        time = ([p.strip() for p in re.split("|".join(['-',',']), v) if 'am' in p.lower() or 'pm' in p.lower()] or [None])[0]
        if time:
            date_pieces[k] = v.replace(time, '').strip().strip(",").strip("-")

    date_pieces = [piece.strip() for piece in date_pieces if len(piece.strip()) > 4]

    dates = [dateparser.parse(date) for date in date_pieces]

    if len(dates) > 2 or len(dates) == 0:
        return None

    if len(dates) == 1 and dates[0]:
        return DateRange(dates[0],None,date_pieces)

    if len(dates) == 2:

        if dates[0] == None or dates[1] == None:
            return None

        if abs((dates[0] - dates[1]).days) > 5:

            dates = value.split('-')
            date_bits = dates[1].split(" ")
            if len(date_bits) < 2:
                return None

            date_bits = " ".join(date_bits[-2:])

            if date_bits not in dates[0]:
                dates[0] = "{} {}".format(dates[0], date_bits)

            dates = [dateparser.parse(date) for date in dates]

    if dates[0] == None or dates[1] == None:
        return None

    if abs((dates[0] - dates[1]).days) > max_days:
        return None

    if (dates[1] - dates[0]).days < 1:
        return None

    return DateRange(dates[0], dates[1], date_pieces)
