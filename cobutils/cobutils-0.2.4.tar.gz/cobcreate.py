#!/usr/bin/python

from optparse import OptionParser
import sys
import csv
from decimal import Decimal
import locale

locale.setlocale(locale.LC_ALL, '')

import cobutils


def edit_value(value):
    if isinstance(value, basestring):
        return value.strip().decode('latin_1').encode('utf8')
    if isinstance(value, Decimal):
        return locale.str(value)
    if isinstance(value, float):
        return locale.str(value)
    return value


def main():
    usage = """usage: %prog [OPTIONS] [CSVFILE]
Create a cobol sequential data from CSV FILE or standard input"""
    parser = OptionParser(usage=usage)
    parser.add_option("-r", "--reg", dest="regfilename",
                      help="read register from FILE", metavar="FILE")
    parser.add_option("-o", "--out", dest="outfilename",
                      help="output FILE", metavar="FILE")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")

    (options, args) = parser.parse_args()

    if not options.regfilename:
        parser.error("Record definition [-r|--reg] is required")

    if len(args) > 1:
        parser.error("Bad number of arguments")
    if len(args) == 1:
        filename = args[0]
        csvfile = csv.DictReader(open(filename))
    else:
        csvfile = csv.DictReader(sys.stdin)

    if options.outfilename:
        outfile = open(options.outfilename, 'w')
    else:
        outfile = sys.stdout

    struct = cobutils.load_definition_from_file(options.regfilename)

    for row in csvfile:
        raw = struct.get_bytes(row)
        outfile.write(raw)


if __name__ == '__main__':  # pragma no cover
    main()
