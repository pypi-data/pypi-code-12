# -*- coding: utf-8 -*-
import sys
from argparse import ArgumentParser
from . import context


if __name__ == '__main__':
    # python -m vebootstrap hogehoge.py
    parser = ArgumentParser(add_help=False, prog="python -m vebootstrap")
    parser.add_argument("pyfile")

    if len(sys.argv) >= 2 and sys.argv[1] in ("--help", "-h"):
        parser.print_help()
        sys.exit(0)

    known, unknown = parser.parse_known_args()
    c = context.Context(sys.executable, known.pyfile)
    c.start(unknown)

