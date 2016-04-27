""" Implementation of the command line interface.

"""
from __future__ import absolute_import, print_function

from argparse import ArgumentParser

import subprocess

from . import __version__
from .core import config
from .core import logger
import requests
from pyquery import PyQuery as pq
from lxml import etree


__all__ = "main",


def _cmdline(argv=None):
    """ Parse command line arguments.

    """
    parser = ArgumentParser()
    parser.add_argument("-c", "--config", action="append",
            help="config file [etc/config.yml]")
    parser.add_argument("-v", "--version", action="version",
            version="pipsort {:s}".format(__version__),
            help="print version and exit")
    parser.add_argument("-w", "--warn", default="WARNING",
            help="logger warning level [WARNING]")
    parser.add_argument("search_term", type=str,
                        help="Search term for PyPI")
    args = parser.parse_args(argv)
    if not args.config:
        args.config = ["etc/config.yml"]
    return args


def sort_function(a):
    version_a = filter( lambda x: x in '0123456789.', a )
    return version_a


def get_package_list(search_term):
    url = "https://pypi.python.org/pypi?%%3Aaction=search&term=%s"
    r = requests.get(url % search_term)
    htmls = r.content
    htmls = htmls.replace("&nbsp", '')
    d = pq(etree.fromstring(htmls))
    od = d(".odd")
    ev = d(".even")
    odd_list = [odd.getchildren()[0].getchildren()[0].text.split(";") for odd in od]
    even_list = [even.getchildren()[0].getchildren()[0].text.split(";") for even in ev]
    odd_list.extend(even_list)
    return odd_list


def main(argv=None):
    """ Execute the application CLI.

    Arguments are taken from sys.argv by default.

    """
    args = _cmdline(argv)
    config.load(args.config)
    results = get_package_list(args.search_term)
    results = sorted(results, key=lambda a: sort_function(a[1]), reverse=True)
    results_normalized = list()
    last_result = None
    for result in results:
        if result[0] == last_result:
            continue
        results_normalized.append(result)
        last_result = result[0]
    print('\n'.join(["%s    -     %s" % (_[0], _[1]) for _ in results_normalized]))
    return 0
 

# Make the module executable.

if __name__ == "__main__":
    try:
        status = main()
    except:
        logger.critical("shutting down due to fatal error")
        raise  # print stack trace
    else:
        raise SystemExit(status)
