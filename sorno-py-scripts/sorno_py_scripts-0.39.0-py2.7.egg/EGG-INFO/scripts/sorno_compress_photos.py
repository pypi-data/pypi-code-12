#!/Library/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python
"""
sorno_compress_photos.py

Compress a bunch of photos in a folder. The compressed photos will be saved in
a folder called "compressed" in the same folder as the source folder.
The destination folder structure is the same as the source.

This script needs the PIL module some jpeg decoder. For mac, you may try the
following:

brew install libjpeg
sudo pip install pillow

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
import subprocess

from PIL import Image

_LOG = logging.getLogger(__name__)
_PLAIN_LOGGER = None  # will be created in main()


class App(object):
    def __init__(
        self,
        src_folder,
        src_file_extensions,
        quality,
    ):
        self.src_folder = os.path.realpath(src_folder)
        self.src_file_extensions = set(src_file_extensions)
        self.quality = quality
        self.dest_folder = os.path.join(
            os.path.dirname(src_folder),
            "compressed",
        )

    def run(self):
        if not os.path.exists(self.dest_folder):
            os.mkdir(self.dest_folder)

        for root, dirs, files in os.walk(self.src_folder):
            for d in dirs:
                dirpath = os.path.join(root, d)
                dest_dirpath = self.dest_folder + dirpath[len(self.src_folder):]
                if not os.path.exists(dest_dirpath):
                    _LOG.info("mkdir %s", dest_dirpath)
                    os.mkdir(dest_dirpath)

            for f in files:
                filename, ext = os.path.splitext(f)
                ext = ext.lstrip(".")
                if ext in self.src_file_extensions:
                    filepath = os.path.join(root, f)
                    filepath_without_ext = os.path.join(root, filename)
                    _LOG.info("Process file: %s", filepath)
                    image = Image.open(filepath)
                    new_filepath = (
                        self.dest_folder + filepath_without_ext[
                            len(self.src_folder):
                        ] + ".jpg"
                    )
                    _LOG.info("Save to new file: %s", new_filepath)
                    image.save(new_filepath, quality=self.quality)

#
# logger-related functions
#

def setup_logger(
    logger,
    debug=False,
    stdout=False,
    log_to_file=None,
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

    if log_to_file is not None:
        init_command = 'mkdir -p %s' % os.path.dirname(log_to_file)

        subprocess.check_call(init_command, shell=True)

        hdlr = TimedRotatingFileHandler(
            log_to_file,
            when="midnight",
            interval=1,
        )
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)


def create_plain_logger(logger_name, stdout=True):
    plain_logger = logging.getLogger(logger_name)
    plain_logger.propagate = False
    plain_logger.setLevel(logging.INFO)

    if stdout:
        out = sys.stdout
    else:
        out = sys.stderr

    handler = logging.StreamHandler(stream=out)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(message)s",
            datefmt="%Y",  # does not matter
        )
    )

    plain_logger.addHandler(handler)
    return plain_logger


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
Compress a bunch of photos in a folder.
    """
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
    )
    parser.add_argument(
        "src_folder",
        help="Recursively traverse all photos in the folder to compress them",
    )
    parser.add_argument(
        "--file-extensions",
        default="jpg",
        help="""
            A comma separated list of file extensions. Only files with these
            extensions will be compressed. Default: %(default)s
        """
    )
    parser.add_argument(
        "--quality",
        default=90,
        help="""
            The quality retained in the compression. It's a number from 0 to
            100. The default is %(default)s
        """,
        type=int,
    )

    args = parser.parse_args(cmd_args)
    return args


def main():
    global _PLAIN_LOGGER

    args = parse_args(sys.argv[1:])

    setup_logger(_LOG, debug=args.debug)
    _PLAIN_LOGGER = create_plain_logger("PLAIN")

    app = App(
        args.src_folder,
        [fs.strip() for fs in args.file_extensions.split(",")],
        quality=args.quality,
    )
    app.run()


if __name__ == '__main__':
    main()
