# -*- coding: utf-8 -*-

from os.path import expanduser, join

import numpy as np
from matplotlib import pyplot as plt

def create_bar_chart(k, v, width=0.5, grid=True, config=None):
    """Create bar chart img
    Input:
        k -- labels for the xaxis,
        v -- heights of the bars,
        width -- width(s) of the bars (default: 0.5),
        grid -- turn the axes grids on or off,
        config -- ConfigObj dict.

    """

    N = len(k)
    x = np.arange(N) # The x coordinates of the left sides of the bars
    # Create a figure with a set of subplots already made
    fig = plt.subplots()
    # Make a bar plot
    plt.bar(left=x, height=v, width=width)
    # Set the x axis label of the current axis
    plt.xlabel("time")
    # Set the y axis label of the current axis
    plt.ylabel("money")
    # Set the x-limits of the current tick locations and labels
    plt.xticks(x+width/2, k)
    # Set a title of the current axes
    plt.title('Ruslan Korniichuk')
    # Turn the axes grids on or off
    plt.grid(grid)
    # Save the current figure
    if config != None:
        output_dir_abs_path = expanduser(config["output_dir_abs_path"])
        bar_chart_png_file_name = config["bar_chart_png_file_name"]
        png_abs_path = join(output_dir_abs_path, bar_chart_png_file_name)
    else:
        png_abs_path = "cash.png"
    plt.savefig(png_abs_path)
