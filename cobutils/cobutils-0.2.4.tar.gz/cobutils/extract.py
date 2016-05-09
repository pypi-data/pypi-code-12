#!/usr/bin/python

from optparse import OptionParser
import csv
from decimal import Decimal
import locale
import sys
locale.setlocale(locale.LC_ALL, '')

import cobutils


def record_iterator(definition, datain, line_sequential=False, sql=False):
    regsize = definition.size()
    # save reference for speed
    rcls = cobutils.Record
    if line_sequential:
        for line in datain:
            record = rcls(definition, line)
            yield record
    else:
        regdata = datain.read(regsize)
        while regdata:
            record = rcls(definition, regdata, sql=sql)
            yield record
            regdata = datain.read(regsize)


def records(definition, datain, line_sequential=False, sql=False):
    return [record for record in \
                record_iterator(definition, datain, line_sequential, sql=sql)]

def edit_value(value):
    if isinstance(value, type(b'')):
        return value.rstrip()
    if isinstance(value, type(u'')):
        return value.rstrip().encode('latin_1')
    if isinstance(value, Decimal):
        return locale.str(value)
    if isinstance(value, float):
        return locale.str(value)
    return value


def main(args):
    usage = """usage: %prog [OPTIONS] [FILE]
Extract cobol sequential data from FILE or standard input"""
    parser = OptionParser(usage=usage)
    parser.add_option("-r", "--reg", dest="regfilename",
                      help="read register from FILE", metavar="FILE")
    parser.add_option("-l", "--line",
                      help="Input file is line sequential",
                      action="store_true", dest="line_sequential",
                      default=False)
    parser.add_option("-o", "--out", dest="outfilename",
                      help="output FILE", metavar="FILE")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")
    parser.add_option("-s", "--sql",
                      action="store_true", dest="sql", default=False,
                      help="Sanitize filed names for SQL")
    #parser.add_option("-u", "--quotes",
    #                  action="store_true", dest="quoting", default=False,
    #                  help="quote all non-numeric fields")

    (options, args) = parser.parse_args(args)

    if not options.regfilename:
        parser.error("Record definition [-r|--reg] is required")

    if len(args) > 1:
        parser.error("Bad number of arguments")
    if len(args) == 1:
        filename = args[0]
        datafile = open(filename)
    else:
        datafile = sys.stdin

    if options.outfilename:
        outfile = open(options.outfilename, 'w')
    else:
        outfile = sys.stdout

    struct = cobutils.load_definition_from_file(options.regfilename)
    fieldnames = struct.fieldnames()
    csvfile = csv.DictWriter(outfile, fieldnames, delimiter=";")

    if options.sql:
        row = {}
        for name, sqlname in zip(fieldnames, struct.fieldnames(sql=True)):
            row[name] = sqlname
        csvfile.writerow(row)
    else:
        csvfile.writerow(dict((name, name) for name in fieldnames))
    for record in record_iterator(struct, datafile,
                       line_sequential=options.line_sequential):
        for k, v in record.iteritems():
            record[k] = edit_value(v)
        csvfile.writerow(record)
