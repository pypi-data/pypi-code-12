
"""
Here are placed some typical functions for use with data_cahce module tools
"""

import os.path
import logging
import datetime


def check_data_cache_timeout(filename, timeout_delta):
    """
    return:
        True - cache timed out,
        False - cache isn't timed out,
        None - some error
    """

    ret = True

    if not isinstance(filename, str):
        raise TypeError("`filename' must be str")

    if not isinstance(timeout_delta, datetime.timedelta):
        raise TypeError("`timeout_delta' must be datetime.timedelta")

    try:
        if os.path.isfile(filename):

            file_ctime = datetime.datetime.fromtimestamp(
                os.stat(filename).st_ctime,
                tz=datetime.timezone.utc
                )
            current_time = datetime.datetime.now(
                tz=datetime.timezone.utc
                )

            if (current_time - file_ctime) <= timeout_delta:
                ret = False
    except:
        logging.exception('error')
        ret = None

    return ret
