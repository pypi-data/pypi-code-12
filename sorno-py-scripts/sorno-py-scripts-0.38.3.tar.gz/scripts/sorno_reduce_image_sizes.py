#!/usr/bin/env python
"""Saves images with reduced sizes.

Reduces the sizes of all images in a directory and its subdirectories by
saving them with lower quality jpg format. The directory structure is
preserved but the new directory is created with a timestamp suffix.


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
import time

from PIL import Image


_LOG = logging.getLogger(__name__)


class App(object):
    def __init__(
        self,
        src_dir,
        dest_dir,
        dry_run=False,
    ):
        self.src_dir = src_dir
        self.dest_dir = dest_dir
        self.real_src_dirpath = os.path.realpath(src_dir)
        self.dry_run = dry_run

    def run(self):
        _LOG.info("Create directory %s", self.dest_dir)
        if not self.dry_run:
            os.mkdir(self.dest_dir)

        for root, dirs, files in os.walk(self.src_dir):
            for d in dirs:
                dirpath = os.path.realpath(os.path.join(root, d))
                dest_path = self.make_dest_path(dirpath)
                _LOG.info(
                    "Create directory %s",
                    dest_path,
                )

                if not self.dry_run:
                    os.mkdir(dest_path)

            for f in files:
                filepath = os.path.realpath(os.path.join(root, f))
                ext = os.path.splitext(filepath)[1]
                if ext in (".jpg", ".png"):
                    dest_path = self.make_dest_path(filepath)
                    if not dest_path.endswith(".jpg"):
                        dest_path = os.path.splitext(dest_path)[0] + ".jpg"

                    _LOG.info(
                        "Shrink the size of %s and save to %s",
                        filepath,
                        dest_path,
                    )
                    src_image = Image.open(filepath)
                    if not self.dry_run:
                        src_image.save(
                            dest_path,
                            optimize=True,
                            quality=85,
                        )

                        src_size, src_atime, src_mtime = os.stat(filepath)[
                            6:9
                        ]
                        dest_size = os.path.getsize(dest_path)
                        _LOG.info(
                            "Saved. Size is reduced from %s bytes to %s bytes",
                            src_size,
                            dest_size,
                        )
                        _LOG.info(
                            "Change the atime and mtime for %s to %s and %s",
                            dest_path,
                            src_atime,
                            src_mtime,
                        )
                        os.utime(dest_path, (src_atime, src_mtime))


    def make_dest_path(self, src_path):
        if not src_path.startswith(self.real_src_dirpath):
            raise Exception(
                "{0} does not start with {1}".format(
                    src_path,
                    self.real_src_dirpath,
                )
            )

        return os.path.join(
            self.dest_dir,
            src_path[len(self.real_src_dirpath):].lstrip('/'),
        )

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
Reduce the sizes of all images in a directory and its subdirectories by saving them with lower
quality jpg format. The directory structure is preserved but the new directory
is created with a timestamp suffix.
    """
    parser = argparse.ArgumentParser(
        description=description,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
    )
    parser.add_argument(
        "src_dir",
    )
    args = parser.parse_args(cmd_args)
    return args


def main():
    args = parse_args(sys.argv[1:])

    setup_logger(_LOG)

    dest_dir = args.src_dir.rstrip('/') + time.strftime("_%Y_%m_%d_%H_%M_%S")

    app = App(
        args.src_dir,
        dest_dir,
        dry_run=args.dry_run,
    )
    app.run()


if __name__ == '__main__':
    main()
