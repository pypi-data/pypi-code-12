#!/usr/bin/env python

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division

from functools import partial

from future import standard_library
from jw.util.python3hell import SetDefaultEncoding

standard_library.install_aliases()
from builtins import *
import argparse

from . import __version__
import io
import logging
import logging.config
from jw.util import configuration
from .app import App
from gevent.monkey import patch_all
from .logging2 import *

VERSION = 'Mailfilter version {}'.format(__version__)

logging.addLevelName(DEBUG2, 'DEBUG2')
logging.addLevelName(DEBUG3, 'DEBUG3')

patch_all()

SetDefaultEncoding()

def Main():
    argp = argparse.ArgumentParser(description='IMAP Mail Account')
    argp.add_argument(
        '-c',
        '--config',
        action='store',
        type=partial(io.open, encoding='utf-8'),
        help='Specify configuration file to use'
    )
    argp.add_argument('-V', '--version', action='version', version=VERSION)
    args = argp.parse_args()
    config = configuration.FromStream(args.config)
    logging.config.dictConfig(config('logging'))
    App.init(config)
    App.run()
    App.terminate()

if __name__ == '__main__':
    Main()

