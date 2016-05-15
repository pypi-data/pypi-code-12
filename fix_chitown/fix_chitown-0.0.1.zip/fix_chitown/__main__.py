"""Test script for entry points."""

import sys


def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    print("This/these are the args {}").format(args)
    print("This will do better stuff later")

if __name__ == "__main__":
    main()
