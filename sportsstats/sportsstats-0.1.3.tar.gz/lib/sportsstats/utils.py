#!/usr/bin/env python

"""utils

Utilities used in sportsstats
"""

import json


def unique_filepath(path):
    """Get a unique, absolute filepath from path by appending _%d, where %d is
    a unique digit starting at 1.

    Args:
        path (str): A not necessarily absolute filepath.

    Returns:
        str: A unique, absolute filepath.
    """
    import os
    attempt = 0
    file_path = os.path.splitext(os.path.abspath(path))
    file_name = file_path[0]
    file_ext = file_path[1]
    while True:
        suffix = '_' + str(attempt) if attempt > 0 else ''
        attempt_file_path = file_name + suffix + file_ext
        if not os.path.exists(attempt_file_path):
            return attempt_file_path
        attempt += 1


def beautify_json(content):
    """Parse JSON string and make it more human readable.

    Args:
        content (str): UTF-8 encoded JSON.
    Returns:
        str: Human readable JSON
    """
    json_data = json.loads(content)
    return json.dumps(json_data, sort_keys=True, indent=4)


def add_years(dt, years):
    """Add (or subtract) years, handling leap years.

    Args:
        dt (datetime): The datetime object.
        years (int): Positive or negative number of years to add.

    Returns:
        datetime: The same calendar date (month and day) in the
            destination year, if it exists, otherwise use the following day
            (thus changing February 29 to March 1).
    """
    try:
        dt = dt.replace(year=dt.year + years)
    except ValueError:
        # handle leap years
        #  dt = d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))
        dt = dt.replace(year=dt.year + years, day=dt.day + 1)
    return dt
