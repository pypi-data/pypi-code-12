#!/Library/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python
"""
sorno_appcache_generator.py


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
from argparse import ArgumentParser
import time

import logging
import os

import sys
import subprocess


_LOG = logging.getLogger(__name__)
_PLAIN_LOGGER = None  # will be created in main()


_APPCACHE_TEMPLATE = """
CACHE MANIFEST
# version {date} 01

CACHE:
{files_list}

NETWORK:
*
""".strip()

class App(object):
    def __init__(
        self,
        web_app_root,
    ):
        self.web_app_root = web_app_root

    def run(self):
        _LOG.debug("Generate appcache with root dir: %s", self.web_app_root)

        date = time.strftime("%Y-%m-%d")

        filepaths = []

        web_app_root = os.path.realpath(self.web_app_root)
        _LOG.debug("Walk dir: %s", web_app_root)

        for root, dirs, files in os.walk(web_app_root):
            dir_under_web_app_root = os.path.realpath(
                root
            ).replace(
                web_app_root, ""
            ).lstrip(os.path.sep)

            _LOG.debug("dir_under_web_app_root is %s", dir_under_web_app_root)

            for f in files:
                if not self.skip_file(f):
                    filepath = os.path.join(dir_under_web_app_root, f)
                    filepaths.append(filepath)

        filepaths.sort()
        files_list = os.linesep.join(filepaths)

        print(_APPCACHE_TEMPLATE.format(**locals()))

    def skip_file(self, filename):
        return filename.startswith(".")
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
Generate an appcache file to be used for html5 application cache of a web
application. The goal is to make the whole web app cached, so the app can be
run offline.

Synopsis:
sorno_appcache_generator.py <web app directory>

It prints out the appcache content, so you should redirect the standard output
to a file for your web app. The appcache file is assumed to be put into the
same folder as the web app root directory.
    """
    parser = ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
    )

    parser.add_argument(
        "web_app_dir",
        help="The root directory of the web app",
    )

    args = parser.parse_args(cmd_args)
    return args


def main():
    global _PLAIN_LOGGER

    args = parse_args(sys.argv[1:])

    setup_logger(_LOG, debug=args.debug)
    _PLAIN_LOGGER = create_plain_logger("PLAIN")

    app = App(
        args.web_app_dir,
    )
    app.run()


if __name__ == '__main__':
    main()
