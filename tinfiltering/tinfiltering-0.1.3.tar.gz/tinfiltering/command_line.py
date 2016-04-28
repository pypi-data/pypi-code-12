# -*- coding: utf-8 -*-
"""
@author: Matheus Boni Vicari (matheus.boni.vicari@gmail.com)
"""

import filter
import sys


# Defining the run_cmd function to manage the command line execution of
# the tinfiltering package.
def run_cmd():

    args = sys.argv[1:]

    if len(args) == 2:

        main(args[0], args[1])

    else:
        print('To run the tinfiltering via command line you must use as\
 input the name of the file containing the point set to be filtered (*.npy)\
 and the name of the file to save the filtered points (*.npy)')


# Defining the filter function, which will be only used if the module is
# called from the console.
def main(in_filename, out_filename):

    """
    Run the filter module via console.

    Parameters
    ----------
    in_filename: str
            Name of the file containing the numpy array point data to be
            filtered.
    out_filename: str
            Name of the file to save the numpy array of filtered point data.

    """

    import numpy as np

    if type(in_filename) is not str:

        print('Wrong argument for input file name')
        return

    if type(out_filename) is not str:

        print('Wrong argument for output file name')
        return

    in_data = np.load(in_filename)

    out_data = filter.apply_filter(in_data[:, 0], in_data[:, 1])

    np.save(out_filename, out_data)


if __name__ == "__main__":

    run_cmd()
