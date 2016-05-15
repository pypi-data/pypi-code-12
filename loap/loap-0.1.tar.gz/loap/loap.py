import sys
import argparse
import logging


class LogOptionsArgumentParser (argparse.ArgumentParser):
    def __init__(self, *a, **kw):
        super(LogOptionsArgumentParser, self).__init__(*a, **kw)
        add_log_options(self)

    def parse_args(self, *a, **kw):
        opts = super(LogOptionsArgumentParser, self).parse_args(*a, **kw)
        init_logging(opts)
        return opts


def add_log_options(argparser):
    logopts = argparser.add_mutually_exclusive_group()
    logopts.set_defaults(loglevel=logging.INFO)

    logopts.add_argument(
        '--quiet', '-q',
        dest='loglevel',
        action='store_const',
        const=logging.WARN,
        help='Log only warnings and errors')

    logopts.add_argument(
        '--debug',
        dest='loglevel',
        action='store_const',
        const=logging.DEBUG,
        help='Log all messages, including debug messages')


def init_logging(opts):
    logging.basicConfig(
        stream=sys.stdout,
        format='%(asctime)s %(levelname) 5s %(name)s | %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S%z',
        loglevel=opts.loglevel)
