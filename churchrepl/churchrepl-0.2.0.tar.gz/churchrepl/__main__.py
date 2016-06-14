"""
The Main Repl for ChurchREPL
"""
import sys
from churchrepl import set_args, repl_eval


def main(args):
    """
    The main repl runner
    :param args: args supplied to set_args
    :return: None
    """
    repl_eval("> ", set_args(args))

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
