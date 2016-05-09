import argparse

from iterator import BedEntryIterator
from lhc.io.bed.tools import depth
from lhc.io.txt.tools import compress


def iter_bed(fname):
    it = BedEntryIterator(fname)
    for entry in it:
        yield entry
    it.close()


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    subparsers = parser.add_subparsers()
    # Compress parser
    compress_parser = subparsers.add_parser('compress')
    compress.define_parser(compress_parser)
    compress_parser.set_defaults(block_delimiter='\n')
    # Depth parser
    depth_parser = subparsers.add_parser('depth')
    depth.define_parser(depth_parser)
    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())
