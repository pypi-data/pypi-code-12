from pyfem1d import Analysis
from multiprocessing import Process
import argparse
import os
import ntpath

import pyfem1d.umat_defaults
import pyfem1d.load_defaults

# abspath = os.path.dirname(os.path.abspath(__file__))


class FullPaths(argparse.Action):
    """Expand user- and relative-paths"""

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest,
                os.path.abspath(os.path.expanduser(values)))


def is_dir(dirname):
    """Checks if a path is an actual directory"""
    if not os.path.isdir(dirname):
        msg = "{0} is not a directory".format(dirname)
        raise argparse.ArgumentTypeError(msg)
    else:
        return dirname


parser = argparse.ArgumentParser()
parser.add_argument("input",
                    metavar="input_file",
                    nargs="?",
                    help="input file",
                    type=argparse.FileType("r"))
# parser.add_argument("-o",
#                     "--output-file",
#                     default="default_out.dat",
#                     type=argparse.FileType("w"))
#parser.add_argument("-l", "--log-file", default="default.log",
#type=argparse.FileType("w"))
# parser.add_argument("-d",
#                     "--displacement-file",
#                     default="default_disp.dat",
#                     type=argparse.FileType("w"))
# parser.add_argument("-u",
#                     "--stress-file",
#                     default="default_stre.dat",
#                     type=argparse.FileType("w"))
# parser.add_argument("-p",
#                     "--plot-file",
#                     default="default.ps",
#                     type=argparse.FileType("w"))
# parser.add_argument("-n",
#                     "--number-of-elements",
#                     default="10",
#                     type=int)

# parser.add_argument("-t", "--timestep", default="0.1", type=float)
# parser.add_argument("-m", "--maximum-time", default="25", type=float)
# parser.add_argument("-g", "--gui", action="store_true", help="Start the graphical user interface")
parser.add_argument("-v", "--verbose", action="store_true")

# parser.add_argument("-s", "--silent", action="store_true")
# parser.add_argument("-i", "--interactive", action="store_true")


def __main__():
    args = parser.parse_args()

    an = Analysis()

    # an.silent = args.silent
    an.verbose = args.verbose
    # an.interactive = args.interactive
    # an.gui = args.gui

    # input file
    if args.input:
        an.input_file = os.path.abspath(args.input.name)
        an.workingDirectory = os.path.dirname(os.path.abspath(args.input.name))
    else:
        an.workingDirectory = os.getcwd()

    #an.logFile = os.path.abspath(args.log_file.name)
    # an.output_file = os.path.abspath(args.output_file.name)
    # an.stress_file = os.path.abspath(args.stress_file.name)
    # an.displacement_file = os.path.abspath(args.displacement_file.name)
    # an.plotFile = os.path.abspath(args.plot_file.name)

    an.output_file = "default_out.dat"
    an.stress_file = "default_stre.dat"
    an.displacement_file = "default_disp.dat"

    an.add_umats(os.path.abspath(pyfem1d.umat_defaults.__file__))
    an.add_loads(os.path.abspath(pyfem1d.load_defaults.__file__))

    an.printHeader()

    # Execute the input file if given
    if an.input_file:
        an.cmdShell.execFile(an.input_file)
    else:
        an.startShell()


if __name__ == "__main__":
    __main__()
