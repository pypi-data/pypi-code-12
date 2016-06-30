#!/usr/bin/env python
from lxml import etree
import logging
import sys
import argparse
from . import fxg2svg


LOGLEVELMAP = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,

}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("fxg", help="fxg file")
    parser.add_argument(
        "-l", 
        "--log-level", 
        choices=LOGLEVELMAP.keys(),
        default="info",
        help="set log level"
    )
    parser.add_argument("-o", "--output", help="output svg filename")
    args = parser.parse_args()

    fxg_bytes = open(args.fxg, 'r')

    logging.basicConfig(
        format=u'%(levelname)-6s| %(message)s',
        level=LOGLEVELMAP[args.log_level]
    )

    if args.output is not None:
        svg = args.output
    else:
        svg = "%s.svg" % ".".join(args.fxg.split('.')[:-1])
    fxg2svg(fxg_bytes).getroottree().write(svg)


if __name__ == "__main__":
    main(sys.argv[1::])
