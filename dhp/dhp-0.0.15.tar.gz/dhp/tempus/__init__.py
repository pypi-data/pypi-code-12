'''dhp.tempus - date, time and interval related routines.'''

import datetime

MIAD = 24 * 60      # Minutes In A Day (MIAD)
SY_TABLE = {
    'hourly': MIAD/24,
    'daily': MIAD,
    'weekly': 7 * MIAD,
    'monthly': 28 * MIAD,
    'yearly': 365 * MIAD
}


class IntervalError(ValueError):
    '''time interval error has occurred'''
    pass


def delta_from_interval(interval):
    """convert an interval 'NwNdNhNmNs' to a timedelta.

    Args:
        interval (str): a string in the form [Mw][Nd][Od][Ph][Qm][Rs]

    Returns:
        datetime.timedelta: a timedelta object of the same interval length.

    """
    periods = ['weeks', 'days', 'hours', 'minutes', 'seconds']
    struct = {period: 0 for period in periods}
    remain = interval.lower()
    for period in periods:
        if period[0] in remain:
            struct[period], remain = remain.split(period[0])
            try:
                struct[period] = int(struct[period])
                if struct[period] < 0:
                    raise IntervalError('Negative Intervals not allowed.')
            except ValueError:
                msg = 'Invalid %s interval [%s]'
                raise IntervalError(msg % (period, struct[period]))

    if remain:
        raise IntervalError('Unknown Subinterval[%s]' % remain)

    return datetime.timedelta(**struct)


def interval_from_delta(tdelta):
    """convert a timedelta to an interval.

    Args:
        tdelta (datetime.timedelta): The timedelta object to convert to an
            interval.

    Returns:
        interval (str): The interval representation of the timedelta object.
    """
    weeks, days = divmod(tdelta.days, 7)
    minutes, seconds = divmod(tdelta.seconds, 60)
    hours, minutes = divmod(minutes, 60)
    rslt = ''
    if weeks:
        rslt += '%iw' % weeks
    if days:
        rslt += '%id' % days
    if hours:
        rslt += '%ih' % hours
    if minutes:
        rslt += '%im' % minutes
    if seconds:
        rslt += '%is' % seconds
    return rslt
