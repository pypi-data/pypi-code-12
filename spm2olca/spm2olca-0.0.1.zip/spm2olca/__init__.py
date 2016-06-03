import argparse
import spm2olca.pack as pack
import spm2olca.parser as parser
import logging as log
import sys
import os


def get_arg_parser() -> argparse.ArgumentParser:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('csv_file', metavar='CSV File', type=str,
                            help='The SimaPro CSV file')
    arg_parser.add_argument('-out', type=str, default=None,
                            help='name of the output file')
    arg_parser.add_argument('-skip_unmapped', action='store_true',
                            help='skip LCIA factors of non-reference flows')
    arg_parser.add_argument('-log', type=str, default='error',
                            choices=['error', 'warn', 'all'],
                            help='optional logging level (default is error)')
    return arg_parser


def main():
    arg_parser = get_arg_parser()
    args = arg_parser.parse_args()
    configure_logger(args)

    file_path = args.csv_file
    p = parser.Parser()
    p.parse(file_path)

    zip_file = file_path + '.zip'
    if args.out is not None:
        zip_file = args.out

    if os.path.isfile(zip_file):
        log.warning('%s already exists and will be overwritten' % zip_file)
        os.remove(zip_file)

    pack.Pack(p.methods, skip_unmapped_flows=args.skip_unmapped).to(zip_file)


def configure_logger(args):
    log_level = log.ERROR
    if args.log == 'warn':
        log_level = log.WARNING
    if args.log == 'all':
        log_level = log.DEBUG
    log.basicConfig(level=log_level, format='  %(levelname)s %(message)s',
                    stream=sys.stdout)
