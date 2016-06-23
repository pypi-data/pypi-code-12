"""
The Main Repl for ChurchREPL
"""
import sys
from churchrepl import set_args, repl_eval


def main():
    """
    The main repl runner
    :param args: args supplied to set_args
    :return: None
    """
    repl_eval("> ", set_args(sys.argv[1:]))

if __name__ == '__main__':
    sys.exit(main())
