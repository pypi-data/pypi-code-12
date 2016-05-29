#!/usr/bin/env python3

"""
    run.py
    ======

    Script for executable module.

    Compute a hash value for the given DIMACS file.

    * Ignores comments 'c' and '%' lines
    * Order of clauses matters
    * Order of literals matters

    A more formal specification is provided at
    `cnfhash project homepage <http://lukas-prokop.at/proj/cnfhash/>`_.

    (C) Lukas Prokop, 2016, Public Domain
"""

import gzip
import os.path
import argparse
import datetime
import multiprocessing

from . import hashing


def read_chunks(fd, chunk_size=None):
    """Read chunks from a file descriptor"""
    if chunk_size is None:
        import resource
        chunk_size = resource.getpagesize()
    while True:
        data = fd.read(chunk_size)
        if not data:
            break
        yield data


def run(arg):
    args, dimacsfile = arg
    if dimacsfile.endswith('.gz'):
        opener = gzip.open
    else:
        opener = open

    with opener(dimacsfile, 'rb') as fd:
        ignore_lines = b'c'
        for prefix in (args.ignore or []):
            ignore_lines += prefix.encode('ascii')
        try:
            gen = read_chunks(fd)
            hashvalue = hashing.hash_dimacs(gen, ignore_lines=ignore_lines)
        except hashing.DimacsSyntaxError as e:
            raise hashing.DimacsSyntaxError("Error while processing {}".format(dimacsfile))

    filename = os.path.basename(dimacsfile)
    print('{:<45}  {}'.format(hashvalue, dimacsfile if args.fullpath else filename))


def main():
    parser = argparse.ArgumentParser(description='CNF hashing')
    parser.add_argument('dimacsfiles', metavar='dimacsfiles', nargs='+',
                        help='filepath of DIMACS file')
    parser.add_argument('--ignore', action='append',
                        help='a prefix for lines that shall be ignored (like "c")')
    parser.add_argument('-f', '--fullpath', action='store_true',
                        help='the hash value will be followed by the filepath, not filename')

    args = parser.parse_args()
    print('cnf-hash-py 1.0.0 {} {}'.format(datetime.datetime.utcnow().isoformat(), os.getcwd()))
    with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
        pool.map(run, zip([args] * len(args.dimacsfiles), args.dimacsfiles))

if __name__ == '__main__':
    main()
