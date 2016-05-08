#!/usr/bin/env python
"""sorno_realdate.py prints the human readable date for timestamps

Example:

    $ sorno_realdate.py 1455223642 1455223642000 1455223642000000 1455223642000000000
    1455223642: 2016-02-11 12:47:22-0800 PST in s
    1455223642000: 2016-02-11 12:47:22-0800 PST in ms
    1455223642000000: 2016-02-11 12:47:22-0800 PST in us
    1455223642000000000: 2016-02-11 12:47:22-0800 PST in ns

    Copyright 2016 Heung Ming Tai

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import argparse
import sys

from sorno import datetimeutil


_datetime_format = "%Y-%m-%d %H:%M:%S%z %Z"


class RealDateApp(object):
    def __init__(self, args):
        self.args = args

    def run(self):
        for n in self.args.numbers:
            try:
                n = int(n)
                dt, unit = datetimeutil.number_to_local_datetime(n)
                print(
                    "%s: %s in %s" % (
                        n,
                        dt.strftime(_datetime_format),
                        unit,
                    )
                )
            except ValueError:
                try:
                    print(
                        "%s: %s" % (
                            n,
                            datetimeutil.guess_local_datetime(n).strftime(
                                _datetime_format
                            ),
                        )
                    )
                except:
                    print("%s: invalid datetime" % n)


def parse_args(cmd_args):
    description = __doc__.split("Copyright 2016")[0].strip()

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "numbers",
        metavar="number",
        nargs="+",
    )

    args = parser.parse_args(cmd_args)
    return args


def main():
    args = parse_args(sys.argv[1:])

    app = RealDateApp(args)
    sys.exit(app.run())


if __name__ == '__main__':
    main()
