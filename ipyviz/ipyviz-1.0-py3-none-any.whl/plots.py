import matplotlib.pyplot as mpl
import numpy as np
import seaborn


def area_plot(values: list, label="", title="", xlabel="", ylabel="", xlim=[], ylim=[], color_palette="muted", lw=0.3,
              alpha=0.5, edgecolor='black', hold=False):
    """
    Produces a pretty MATLAB-Style "Area Plot"

    :param values: a list of numpy vectors of equal size to be plotted
    :type values: :class:`list`
    :param label: a readable name for the individual entries
    :type label: :class:`str`
    :param title: a title for the plot
    :type title: :class:`str`
    :param xlabel: a xlabel for the plot
    :type xlabel: :class:`str`
    :param ylabel: a ylabel for the plot
    :type ylabel: :class:`str`
    :param xlim: x limits of the plot. If nothing is passed the default is 110% of the maximum value
    :type xlim: :class:`list`
    :param ylim: y limits of the plot. If nothing is passed this is the length of the value entries
    :type ylim: :class:`list`
    :param color_palette: the :func:`seaborn.color_palette` to be used. Default is "muted"
    :type color_palette: :class:`str`
    :param lw: the line width. Default is 0.3
    :type lw: :class:`float`
    :param alpha: the alpha value of the areas. Default is 50%
    :type alpha: :class:`float`
    :param edgecolor: the edge color of the areas. Default is black.
    :type edgecolor: :class:`str`
    :param hold: Hold the print
    :type hold: :class:`bool`
    """
    ax = mpl.gca()

    muted = seaborn.color_palette(color_palette, len(values))

    for i, value in enumerate(values):
        previous = np.zeros(value.shape)
        for n in range(i):
            previous += values[n]

        ax.fill_between(range(len(previous)),
                        previous,
                        previous + value,
                        lw=lw,
                        alpha=alpha,
                        edgecolor=edgecolor,
                        facecolor=muted[i],
                        label="{} {}".format(label, i))

    total = np.zeros(values[0].shape)
    for value in values:
        total += value

    if ylim:
        mpl.ylim(ylim)
    else:
        # default ylim is 110% of the maximum
        mpl.ylim([np.minimum(np.sum([min(value) for value in values]) * 1.1, 0),
                  np.maximum(np.sum([max(value) for value in values]) * 1.1, 0)])

    if xlim:
        mpl.xlim(xlim)
    else:
        mpl.xlim([0, len(total)])

    # legend(loc='right')
    if ylabel:
        mpl.ylabel(ylabel)

    if xlabel:
        mpl.xlabel(xlabel)

    if title:
        mpl.title(title)

    if not hold:
        mpl.show()
