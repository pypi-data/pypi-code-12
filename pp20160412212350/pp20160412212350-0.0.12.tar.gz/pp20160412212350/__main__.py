# -*- coding: utf-8 -*-


import sys
import argparse

from . import helloworld
from . import lib


def main():
    # add parser
    parser = argparse.ArgumentParser(description='ADD YOUR DESCRIPTION HERE')
    parser.add_argument('-v', '--verbose',
                        help='increase output verbosity',
                        required=False, action="count", default=0)
    parser.add_argument('-d', '--debug',
                        help='turn on debug mode',
                        required=False, action="store_true")

    # add subparsers
    subparsers = parser.add_subparsers(title='subcommands')

    # add subcommand - copy
    parser_copy = subparsers.add_parser('copy', help='copy file')
    parser_copy.add_argument('-i', '--input', help='input file name',
                             required=True)
    parser_copy.add_argument('-o', '--output', help='output file name',
                             required=True)
    parser_copy.set_defaults(func=lib.cmdcopy.do_copy)

    # add subcommand - sum
    parser_sum = subparsers.add_parser('sum',
                                       help='calculate the sum of numbers')
    parser_sum.add_argument('number', metavar='N', type=int, nargs='+',
                            help='a list of numbers for sum operation')
    parser_sum.set_defaults(func=lib.cmdsum.do_sum)

    # add subcommand - ls
    parser_ls = subparsers.add_parser('ls',
                                      help='list files or folders')
    parser_ls.add_argument('file', metavar='F', type=str, nargs='+',
                           help='a list of files or folders for ls operation')
    parser_ls.set_defaults(func=lib.cmdls.do_ls)

    # add subcommand - helloworld
    parser_helloworld = subparsers.add_parser('helloworld',
                                              help='print hello world')
    parser_helloworld.set_defaults(func=helloworld.show)

    # parse
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
    else:
        if args.debug:
            print "Turning on debug mode ..."
            print sys.argv
            print args
        else:
            print "Turning off debug mode ..."

        if args.verbose >= 2:
            print "Turning on verbose mode II ..."
        elif args.verbose == 1:
            print "Turning on verbose mode I ..."
        else:
            print "Turning off verbose mode ..."

        args.func(args)

if __name__ == "__main__":
    main()
