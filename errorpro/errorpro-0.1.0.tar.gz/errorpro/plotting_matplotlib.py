import matplotlib.pyplot as plt
import numpy as np
from sympy.utilities.lambdify import lambdify

# TODO: adjust everything to new structure

def plot(data_sets, functions, xlabel=None, ylabel=None, xrange=None,
         yrange=None, xscale=None, yscale=None,  legend=True, size=None,
         save_to=None, show=True, return_fig=False):
    """ plots data and functions with matplotlib

    Args:
        data_sets: list of tuples like this
                   ((xvalue, xerror), (yvalue, yerror), options)
        functions: list of tuples like this
                   (x_quantity, y_expression, options)
                   -> must be adjusted to unit choice already
        ... (see core.py)

    Returns:
        figure object
    """
    plt.ioff()
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # plot data sets
    min = None
    max = None
    for data_set in data_sets:
        data_set = list(data_set)

        # find min and max for function plotting
        min_here = np.amin(data_set[0][0])
        if min is None or min_here < min:
            min = min_here
        max_here = np.amax(data_set[0][0])
        if max is None or max_here > max:
            max = max_here

        # default behaviour for data points
        if not 'marker' in data_set[2]:
            data_set[2]['marker'] = 'o'
        if not 'linestyle' in data_set[2]:
            data_set[2]['linestyle'] = 'None'

        # plot
        ax.errorbar(data_set[0][0],
                    data_set[1][0],
                    xerr = data_set[0][1],
                    yerr = data_set[1][1],
                    **data_set[2])
                    #marker="o",
                    #linestyle="None",
                    #label=data_set["title"])

    if not xrange is None:
        min = xrange[0]
        max = xrange[1]
    if min is None or max is None:
        # standard min/max if no xrange and no data set
        min = 0
        max = 10
    # plot functions
    for f in functions:
        f = list(f)
        # replace all other symbols by their value
        for var in f[1].free_symbols:
            if not var == f[0]:
                f[1] = f[1].subs(var, var.value)
        numpy_func = lambdify((f[0]), f[1], [{"cot":lambda x:1/np.tan(x)},"numpy"])
        x = np.linspace(min,max,500)
        y = numpy_func(x)
        ax.plot(x,y,**f[2])

    if legend:
        plt.legend(loc=legend if isinstance(legend, str) or isinstance(legend, int) else None)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if not xrange is None:
        ax.set_xlim(xrange)
    if not yrange is None:
        ax.set_ylim(yrange)
    if not xscale is None:
        ax.set_xscale(xscale)
    if not yscale is None:
        ax.set_yscale(yscale)
    if size is not None:
        fig.set_size_inches(*size)
    if not save_to is None:
        fig.savefig(save_to)
    if show:
        plt.show()
    if return_fig:
        return fig
    else:
        fig.clear()
