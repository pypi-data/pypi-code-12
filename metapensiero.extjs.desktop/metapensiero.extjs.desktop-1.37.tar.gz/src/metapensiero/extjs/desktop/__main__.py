# -*- coding: utf-8 -*-
# :Project:   metapensiero.extjs.desktop -- ExtJS downloader
# :Created:   mar 02 apr 2013 10:21:38 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2013, 2014, 2016 Lele Gaifax
#

from .scripts.extjs_dl import URL, download_and_extract


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser(description=download_and_extract.__doc__)
    parser.add_argument('--cache', metavar="DIR",
                        default="~/.cache/metapensiero.extjs.desktop",
                        help="Cache the ExtJS zip archive under directory DIR"
                        " (%(default)s by default) instead of downloading it each time")
    parser.add_argument('--no-cache', dest='cache', action='store_false',
                        help="Do not use the cache")
    parser.add_argument('--replace', action='store_true', default=False,
                        help="Remove previously extracted framework")
    parser.add_argument('--url', metavar="URL", default=URL,
                        help="Download ExtJS archive from the given URL"
                        " (%(default)s by default)")
    parser.add_argument('--all', action='store_true', default=False,
                        help="Extract everything instead of just the resources")
    parser.add_argument('--src', action='store_true', default=False,
                        help="Extract also the framework sources, required in"
                        " development mode")

    args = parser.parse_args()
    download_and_extract(args.url, replace=args.replace, cache=args.cache,
                         all=args.all, src=args.src)
