#!python
# -*- coding: utf-8 -*-

"""
convert Elegant lte file to json string file

Tong Zhang
2016-06-14 14:39:29 PM CST
"""

"""
import sys

if len(sys.argv) < 2:
    print("Usage: lte2json ltefile [jsonfile]")
    print(" ltefile : lte file to read")
    print(" jsonfile: json file to write,")
    print("           if jsonfile is omitted, use stdout\n")
    sys.exit(1)

ltefile  = sys.argv[1]
if len(sys.argv) == 2:
    jsonfile = None
else:
    jsonfile = sys.argv[2]

import beamline
lpins = beamline.LteParser(ltefile)
if jsonfile is None:
    print(lpins.file2json())
else:
    lpins.file2json(jsonfile)
"""

import argparse
import sys

parser = argparse.ArgumentParser(description="Convert Elegant lte file into json string file")

parser.add_argument('--lte', dest='ltefile', help='.lte file to read')
parser.add_argument('--json', dest='jsonfile', help='.json file to generate, if None or omitted, write to stdout')


args = parser.parser_args()

ltefile, jsonfile = args.ltefile, args.jsonfile

if args.ltefile is None:
    parser.print_help()
    sys.exit(1)

import beamline
lpins = beamline.LteParser(ltefile)
if jsonfile is None:
    print(lpins.file2json())
else:
    lpins.file2json(jsonfile)
