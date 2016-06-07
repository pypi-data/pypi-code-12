"""
Pandas helper functions.
"""

import pandas as pd

def align_series(x, y, dropna=True):
    """
    Align two :class:`pandas.Series` using an inner join of their indices.

    Arguments
    =========
    x, y : :class:`pandas.Series`
    dropna : bool, optional
        Whether to drop missing elements from both :class:`pandas.Series`
        objects before performing the join.

    Returns
    =======
    A 2-tuple of :class:`pandas.Series`, the aligned versions of x and y.

    """
    assert isinstance(x, pd.Series)
    assert isinstance(y, pd.Series)
    if dropna is True:
        x = x.dropna()
        y = y.dropna()

    ix = list(set(x.index) & set(y.index))
    return x.loc[ix], y.loc[ix]

def sort_absolute_value(v, column=None, ascending=True):
    """
    Sort a :class:`pandas.Series` or a :class:`pandas.DataFrame` by
    absolute value (in the latter case, by the absolute value of a given column).

    Arguments
    =========
    v : :class:`pandas.Series` or :class:`pandas.DataFrame`
    column : str, optional
        If a :class:`pandas.DataFrame` is provided, sort by this column.
        Ignored if v is a :class:`pandas.Series`.
    ascending : bool
        Whether to sort ascending (default True).
    """
    assert isinstance(v, pd.Series) or isinstance(v, pd.DataFrame)

    if column is not None:
        df = v
        ix = sort_absolute_value(df[column], ascending=ascending).index
        return df.loc[ix,:]
    else:
        return v.loc[v.abs().sort_values(ascending=ascending).index]
