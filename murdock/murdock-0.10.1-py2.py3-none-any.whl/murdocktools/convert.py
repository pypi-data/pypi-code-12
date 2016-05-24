#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   This file is part of the Murdock project.
#
#   Copyright 2016 Malte Lichtner
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
    Molecular Structure File Converter
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Employs the Murdock API to convert between molecular structure files. Use
    the command-line option ``--help`` for more information.

    :copyright: Copyright 2016 Malte Lichtner
    :license: Apache License, Version 2.0, see LICENSE for details.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import os
import sys

import murdock.logger
import murdock.moldata


murdock.logger.Logger(
    console_level=logging.INFO, file_level=logging.INFO,
    logdir='.', filename='murdock-convert.log')

log = logging.getLogger('murdock-convert')


def main():
    if _run():
        sys.exit(0)
    else:
        sys.exit(1)


def _parse_command_line():
    cmdline_parser = argparse.ArgumentParser(
        description='Murdock v%s Molecular Structure File Converter' %
        murdock.__version__)
    cmdline_parser.add_argument('inpath', type=str, help='input file path')
    cmdline_parser.add_argument('outpath', type=str, help='output file path')
    return cmdline_parser.parse_args()


def _run():
    cmdline = _parse_command_line()
    outext = os.path.splitext(cmdline.outpath)[1]
    mol = murdock.moldata.get_molstruct(cmdline.inpath)
    if not mol:
        return False
    f = murdock.moldata.convert_to_file(mol, outext)
    if not f:
        return False
    if not f.write(cmdline.outpath):
        return False
    log.info('File `%s` written.', cmdline.outpath)
    return True


if __name__ == '__main__':
    main()
