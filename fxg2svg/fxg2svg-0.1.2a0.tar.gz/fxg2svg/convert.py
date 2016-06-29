#!/usr/bin/env python
from lxml import etree
import logging
import sys
from . import fxg2svg


logging.basicConfig(
    format=u'%(levelname)-6s| %(message)s',
    level=logging.DEBUG
)


def main():
    if len(sys.argv) >= 1:
        fxg = sys.argv[1]
        if len(sys.argv) >= 3:
            svg = sys.argv[2]
        else:
            svg = "%s.svg" % ".".join(fxg.split('.')[:-1])
        fxg2svg(open(fxg, 'r')).getroottree().write(svg)


if __name__ == "__main__":
    main()
