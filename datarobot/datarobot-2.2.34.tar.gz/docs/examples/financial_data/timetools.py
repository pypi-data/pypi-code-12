import datetime
import itertools

import numpy as np
import pandas as pd


def value_filler(index, data):
    """Make a series representing the data that was known at each of the value
    in index. The index of data is guaranteed to be a subset of index

    Parameters
    ----------
    index : array-like
        The index for which we need to know data
    data : pandas.Series
        The data from which we can infer last-known values for the index
    """
    data_iter = data.iteritems()
    data_value = None
    next_index, next_value = next(data_iter)
    for index_value in index:
        if index_value >= next_index:
            data_value = next_value
            try:
                next_index, next_value = next(data_iter)
            except StopIteration:
                pass
        yield data_value


def expand_frame_merge(base, sparse):
    """Take two dataframes, the one on the left has more frequent data
    values than the one on the right. Merge in the one from the right,
    copying data to fill the missing values

    Parameters
    ----------
    base : pandas.DataFrame
        The data with more frequent values. The index must be a date string
    sparse : pandas.DataFrame
        The data with less frequent values. The index must be a date string

    Returns
    -------
    merged : pandas.DataFrame
        A frame with the data from both columns, merged with expansion of
        the less frequent values

    """
    index = common_index(base, sparse)
    all_series = {colname: pd.Series(value_filler(index, series), name=colname, index=index)
                  for colname, series in itertools.chain(
        base.iteritems(), sparse.iteritems())}
    return pd.DataFrame(all_series, index=index)


def common_index(obj1, obj2, datefmt='%Y-%m-%d'):
    """When merging two datasets with differing date indices, we need to know
    the common index that is shared between them.

    The rule is to have the timeframe cover both of their ranges, using the
    time step from obj1. Both of the objects are assumed to have a date index
    using the same date format.

    Parameters
    ----------
    obj1 : pandas.DataFrame or pandas.Series
        The data with the finer-grained data
    obj2 : pandas.DataFrame or pandas.Series
        The less fine-grained data. Could actually be the same time step
        (think of data reported on Wednesdays and data reported on Fridays.
        In such case, the Friday data should be obj1).
    datefmt : string (optional)
        The datefmt shared by the index of each object

    Returns
    -------
    idx : list
        The common index shared by both
    """
    def as_datetime(datestring):
        return datetime.datetime.strptime(datestring, datefmt)

    if len(obj1) <= 1:
        raise ValueError(
            'Need more than one value in reference index in order to build '
            'common index')
    tstep = (as_datetime(obj1.index[1]) -
             as_datetime(obj1.index[0]))

    # Find any days before obj1 on the obj1 timescale
    any_before = []
    if as_datetime(obj2.index[0]) < as_datetime(obj1.index[0]):
        earliest_day = as_datetime(obj2.index[0])
        start_day = as_datetime(obj1.index[0])
        start_day -= tstep
        while start_day >= earliest_day:
            any_before.insert(0, start_day.strftime(datefmt))
            start_day -= tstep

    # Find any days after obj1 on the obj1 timescale
    any_after = []
    if as_datetime(obj2.index[-1]) > as_datetime(obj1.index[-1]):
        latest_day = as_datetime(obj2.index[-1])
        start_day = as_datetime(obj1.index[-1])
        start_day += tstep
        while start_day <= latest_day:
            any_after.append(start_day.strftime(datefmt))
            start_day += tstep

    return any_before + list(obj1.index) + any_after


def slide(series, offset, datefmt='%Y-%m-%d'):
    """
    Take the data and slide it back in time by a specified number of days

    `series` is assumed to have a datestring index, which will be the basis
    of the slide. The same index will be used in the return, so values may
    have to be adjusted

    Parameters
    ----------
    series : pandas.Series
        The data to offset
    offset : int
        The number of days by which to slide back the data
    datefmt : str
        The format of the series' index

    Returns
    -------
    data : pandas.Series
        The adjusted data

    """
    hist_index = [date_offset(ix, offset, datefmt=datefmt) for ix in series.index]
    full_index = common_index(series, pd.Series(series, index=hist_index))
    n_extra_records = len(full_index) - len(hist_index)
    full_series = pd.Series(list(series.values) + [np.NaN] * n_extra_records,
                            index=full_index)
    return full_series[series.index]


def date_offset(datestr, days, datefmt='%Y-%m-%d'):
    """

    Parameters
    ----------
    datestr : str
        The date to adjust
    days : int
        The number of days in the past to drop
    datefmt : str
        The format of the datestring

    Returns
    -------
    past_datestr : str
        The date in the past
    """
    as_datetime = datetime.datetime.strptime(datestr, datefmt)
    past_datetime = as_datetime - datetime.timedelta(days=days)
    return past_datetime.strftime(datefmt)
