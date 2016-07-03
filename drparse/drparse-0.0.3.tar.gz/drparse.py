# -*- coding: utf-8 -*-

import dateparser
import re
import logging

from collections import namedtuple

DateRange = namedtuple('DateRange', 'start end dates')

log = logging.getLogger(__name__)

def get_time_match(value):
    return re.search(r'(\d{1,2})\s?(:\d{1,2})?(am|pm|AM|PM)+', value)

def parse(value, max_days=15):
    """
    parse single or double dates ignoring times unless its single datetime
    """

    separators = [' - ', ' to ', ' & ']

    # Clean input
    for word in ['\n', '\r']:
        value = value.replace(word, ' ')

    value = re.sub("\s\s+", " ", value).strip()

    date_pieces = [piece.strip() for piece in re.split("|".join(separators),value)]

    # strip out time and anything afterwards
    for k,v in enumerate(date_pieces):
        time = get_time_match(v)
        if time:
            date_pieces[k] = v[0:time.span()[0]-1].strip().strip(",").strip("-")

    date_pieces = [piece.strip() for piece in date_pieces if len(piece.strip()) > 4 and bool(re.search(r'\d', piece))]

    dates = [date for date in [dateparser.parse(date) for date in date_pieces] if date]

    if len(dates) > 2 or len(dates) == 0:
        return None

    if len(dates) == 1 and dates[0]:
        # Use datetime parser if possible
        datetime = dateparser.parse(value)
        if datetime and datetime.strftime("%Y-%m-%d") == dates[0].strftime("%Y-%m-%d"):
            dates[0] = datetime

        return DateRange(dates[0],None,date_pieces)

    if len(dates) == 2:

        if dates[0] == None or dates[1] == None:
            return None

        if abs((dates[0] - dates[1]).days) > max_days:

            date_bits = date_pieces[1].split(" ")
            if len(date_bits) < 2:
                return None

            date_bits = " ".join(date_bits[-2:])

            if date_bits not in date_pieces[0] and get_time_match(date_bits) is None:
                date_pieces[0] = "{} {}".format(date_pieces[0], date_bits)

            dates = [dateparser.parse(date) for date in date_pieces]

    if dates[0] == None or dates[1] == None:
        return None

    if abs((dates[0] - dates[1]).days) > max_days:
        return None

    if (dates[1] - dates[0]).days < 1:
        return None

    return DateRange(dates[0], dates[1], date_pieces)
