#!/Library/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python
"""Fills up the disk space with a specific size of garbage data.


   Copyright 2014 Heung Ming Tai

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
import logging
import os
import sys


_LOG = logging.getLogger(__name__)


class SpaceFiller(object):
    def __init__(
        self,
        size,
        output_file,
        buffer_size,
    ):
        """
        @param size
            In GB.
        @param output_file
        @param buffer_size
        """

        self.size = size
        self.output_file = output_file
        self.buffer_size = buffer_size

    def run(self):
        # bytes to fillup
        num_remaining_bytes = int(1024 * 1024 * 1024 * self.size)
        with open(self.output_file, "wb") as f:
            while num_remaining_bytes > 0:
                # do it 10 MB by 10 MB
                _LOG.info(
                    "%d MB remaining.",
                    num_remaining_bytes / (1024 * 1024),
                )
                num_bytes_to_write = min(
                    num_remaining_bytes,
                    self.buffer_size * 1024 * 1024,
                )
                bytes_to_write = os.urandom(num_bytes_to_write)
                f.write(bytes_to_write)
                num_remaining_bytes -= num_bytes_to_write

        _LOG.info("Done")


#
# logger-related functions
#

def setup_logger(
    logger,
    debug=False,
    stdout=False,
    add_thread_id=False,
    logging_level=None,
    use_path=False,
):
    if logging_level is None:
        if debug:
            logging_level = logging.DEBUG
        else:
            logging_level = logging.INFO

    formatter = create_logging_formatter(
        add_thread_id=add_thread_id,
        use_path=use_path
    )
    hdlr = create_stream_handler(
        formatter=formatter,
        stdout=stdout,
    )
    logger.handlers = []  # clear the existing handlers
    logger.addHandler(hdlr)
    logger.setLevel(logging_level)


def create_logging_formatter(add_thread_id=False, use_path=False):
    format_str = "%(asctime)s"

    if add_thread_id:
        format_str += " thread:%(thread)s"

    format_str += " %(levelname)s "

    if use_path:
        format_str += "%(pathname)s"
    else:
        format_str += "%(name)s"

    format_str += ":%(lineno)s: %(message)s"

    detail_formatter = logging.Formatter(
        fmt=format_str,
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    return detail_formatter


def create_stream_handler(formatter=None, stdout=False):
    if formatter is None:
        formatter = create_logging_formatter()

    if stdout:
        stream = sys.stdout
    else:
        stream = sys.stderr

    hdlr = logging.StreamHandler(stream=stream)
    hdlr.setFormatter(formatter)
    return hdlr

#
# end of logger-related functions
#

def parse_args(cmd_args):
    description = """
Fill up the disk space with a specific size of garbage data.
    """
    parser = argparse.ArgumentParser(
        description=description,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
    )
    parser.add_argument(
        "--buffer-size",
        type=int,
        default=10,
        help="Buffer size in MB",
    )
    parser.add_argument(
        "--size",
        required=True,
        type=float,
        help="In GB",
    )
    parser.add_argument("--output", default="stub.dat")

    args = parser.parse_args(cmd_args)
    return args


def main():
    args = parse_args(sys.argv[1:])

    setup_logger(_LOG, debug=args.debug)

    app = SpaceFiller(
        args.size,
        args.output,
        args.buffer_size,
    )
    app.run()


if __name__ == '__main__':
    main()
