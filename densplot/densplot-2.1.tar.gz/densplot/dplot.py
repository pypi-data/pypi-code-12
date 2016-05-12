import sys
import argparse
import numpy as np

import matplotlib.pyplot as plt

from lsdmap.rw import reader
from densplot import hist2d


def create_arg_parser():

    parser = argparse.ArgumentParser(description="create 2D density plot..")

    # required options
    parser.add_argument("-x",
        type=str,
        dest="input_file_x",
        required=True,
        nargs='*',
        help='Input file containing x coordinates')

    parser.add_argument("-y",
        type=str,
        dest="input_file_y",
        required=True,
        nargs='*',
        help = 'Input file containing y coordinates')

    # other options

    parser.add_argument("--nbinsx",
        type=int,
        default=5,
        dest="nbinsx",
        help='Number of bins along x')

    parser.add_argument("--nbinsy",
        type=int,
        default=5,
        dest="nbinsy",
        help='Number of bins along y')

    parser.add_argument("--temperature",
        default=300,
        help='Temperature for free energy plot')

    parser.add_argument("--fe",
        default=False,
        action='store_true',
        dest='free_energy_plot',
        help='Create free energy plot')

    parser.add_argument("--nbins",
        type=int,
        dest='nbins',
        help='Number of bins for 2D histogram')

    parser.add_argument("--plot",
        type=str,
        default='scatter',
        dest='plot_style',
        help='Plot style (scatter, contour)')

    parser.add_argument("-w",
        type=str,
        dest="wfile",
        nargs='*',
        help='File containing the weights of every point in a row (input, opt.): .w')

    parser.add_argument("--xlabel",
        type=str,
        dest="xlabel",
        default='x',
        help='xlabel for density plot')

    parser.add_argument("--ylabel",
        type=str,
        dest="ylabel",
        default='y',
        help='ylabel for density plot')


    parser.add_argument("--smooth",
        type=int,
        dest='idx_smoothing',
        default=2,
        help='Index used to smooth the data')

    return parser


def run():

    parser = create_arg_parser()
    args = parser.parse_args()

    #read input files

    x = []

    for input_file in args.input_file_x: 
        file = reader.open(input_file)
        vals = file.readlines()
        # using readlines() of lsdmap reader, each row of x is a list
        # corresponding to the coordinates of each config, thus
        # needs to concatenate.
        vals = np.concatenate(vals, axis=0)
        x.append(vals)

    x = np.hstack(np.array(x))

    y = []
    for input_file in args.input_file_y:
        file = reader.open(input_file)
        vals = file.readlines()
        # using readlines() of lsdmap reader, each row of y is a list
        # corresponding to the coordinates of each config, thus
        # needs to concatenate.
        vals = np.concatenate(vals, axis=0)
        y.append(vals)

    y = np.hstack(np.array(y)) 


    if not args.nbins:
        npoints = x.shape[0]
        nbins = int(np.sqrt(npoints))
    else:
        nbins = args.nbins

    if args.wfile is not None:
        weight = []
        for wfile in args.wfile:
            file = reader.open(wfile)
            vals = file.readlines()
            weight.append(vals)
        weight = np.hstack(np.array(weight))
    else:
        weight = None


    plot_style = args.plot_style
    free_energy_plot = args.free_energy_plot
    idx_smoothing = args.idx_smoothing 

    x, y, z = hist2d.make(x, y, nbins, nbins, weight=weight, plot_style=plot_style, free_energy_plot=free_energy_plot, idx_smoothing=idx_smoothing)

    if plot_style == 'scatter':
        cp = plt.scatter(x, y, s=10, c=z, marker='o', linewidth=0., vmax=3.5)
    elif plot_style == 'contour':
        cp = plt.contourf(x, y, z)
        plt.contour(x, y, z, cp.levels, colors='k', hold='on')

    plt.xlabel(args.xlabel, size=16)
    plt.ylabel(args.ylabel, size=16)

    cb = plt.colorbar(cp)
    pad = 10
    if free_energy_plot is True:
        cb.set_label(r'Free Energy (kcal/mol)',labelpad=pad)
    else:
        cb.set_label(r'Density', labelpad=pad)

    plt.show()

if __name__=='__main__':
   run()
