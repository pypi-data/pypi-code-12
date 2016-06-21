import numpy as np
import pandas as pd


def as_vector(*xs):
    res = []
    for x in xs:
        if isinstance(x, pd.DataFrame):
            if x.index.size == 1:
                x = x.T
            elif x.columns.size == 1:
                x = x[x.columns[0]]
            else:
                raise ValueError("Vector-like pandas.DataFrame must contains ONLY 1 column or 1 row.", x.shape)

        if isinstance(x, pd.Series):
            x = x.as_matrix()

        if isinstance(x, np.ndarray):
            x = x.ravel()
            res.append(x)
        else:
            raise TypeError("Vector-like types are numpy.ndarray, pandas.Series, and pandas.DataFrame", type(x))

    return res
