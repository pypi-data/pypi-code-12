"""
The Main Repl for ChurchREPL
"""
import sys
from churchrepl import set_args, repl


def main(args):
    """
    The main repl runner
    :param args: args supplied to set_args
    :return: None
    """
    repl("> ", set_args(args))

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
