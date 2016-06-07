"""
Plotting functions, mostly a wrapper layer to seaborn for easier usage.
"""

import collections
import functools

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_fn(fn):
    @functools.wraps(fn)
    def wrap(*args, x_lim=None, y_lim=None, y_label=None, x_label=None, title=None, **kwargs):
        plt.clf()
        figure = fn(*args, **kwargs)
        if x_label is not None:
            plt.xlabel(x_label)
        if y_label is not None:
            plt.ylabel(y_label)
        if title is not None:
            plt.title(title)
        return figure
    return wrap

"""
def rotate_xlabels(degrees=30):
    fig, ax = plt.subplots()
    labels = ax.get_xticklabels()
    plt.setp(labels, rotation=degrees)
"""

@plot_fn
def bar(xs, orient="v", error=None, **kwargs):
    assert isinstance(xs, pd.Series)
    if orient == "v":
        x,y = xs.index, xs
    else:
        x,y = xs, xs.index

    data = pd.DataFrame.from_dict({"x": x, "y": y})
    ax = sns.barplot(x="x", y="y", data=data, orient=orient, order=xs.index)
    if error is not None:
        if isinstance(error, collections.Iterable):
            assert len(error) == len(xs)
            error = list(error)
            for i in range(len(error)):
                ax.errorbar(i, xs.iloc[i], yerr=error[i], fmt="o", color="black")
        else:
            ax.errorbar(np.arange(len(xs)), xs, yerr=error, fmt="o", color="black")
    return plt.gcf()

def coef(fit):
    """
    Plot of statsmodels linear model coefficients.
    """
    return bar(fit.params, error=fit.bse)
