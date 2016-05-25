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
    Screening Splitter
    ~~~~~~~~~~~~~~~~~~

    Creates individual configuration files for each docking within an existing
    screening result directory, e.g. for manual parallelization. Use the
    command-line option ``--help`` for more information.

    :copyright: Copyright 2016 Malte Lichtner
    :license: Apache License, Version 2.0, see LICENSE for details.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import codecs
import json
import logging
import os
import sys
import traceback

import murdock.logger
import murdock.misc


murdock.logger.Logger(
    console_level=logging.INFO, file_level=logging.INFO,
    logdir='.', filename='murdock-split.log')

log = logging.getLogger('murdock-split')


def main():
    if _run():
        sys.exit(0)
    else:
        sys.exit(1)


def _parse_command_line():
    """Parse, validate and return command line arguments.
    """
    cmdline_parser = argparse.ArgumentParser(
        description='Murdock v%s Screening Splitter' % murdock.__version__)
    cmdline_parser.add_argument('resdir', help='screening result directory')
    return cmdline_parser.parse_args()


def _run():
    cmdline = _parse_command_line()
    slabel = os.path.basename(cmdline.resdir.rstrip('/\\'))
    sfilepath = os.path.join(cmdline.resdir, '%s-config.json' % slabel)
    log.info('Parse file `%s`.', sfilepath)
    try:
        scfg = murdock.misc.load_ordered_json(sfilepath)
    except ValueError as exc:
        log.fatal(
            'Can not parse screening result file `%s`: %s.', sfilepath,
            str(exc))
        return False
    except IOError as exc:
        log.fatal(
            'No existing screening result file `%s` found.', sfilepath)
        return False
    stitle = scfg['screening']['title']
    dcfg = scfg.copy()
    dcfg['docking'] = dcfg['screening']
    del dcfg['screening']
    try:
        del dcfg['notes']
    except KeyError:
        pass
    for dinp in scfg['screening']['input_data']:
        dcfg['docking']['input_data'] = dinp
        dcfg['docking']['title'] = dinp['title']
        del dcfg['docking']['input_data']['title']
        dlabel = dinp['label']
        dcfg['docking']['label'] = dlabel
        del dcfg['docking']['input_data']['label']
        try:
            del dinp['tags']
        except KeyError:
            pass
        try:
            dcfg['docking']['notes'] = dinp['notes']
            del dinp['notes']
        except KeyError:
            pass
        ddir = os.path.join(slabel, 'dockings', dlabel)
        if not os.path.exists(ddir):
            os.makedirs(ddir)
        dfilepath = os.path.join(ddir, '%s-config.json' % dlabel)
        if os.path.exists(dfilepath):
            log.warning('File `%s` already exists. Skip.', dfilepath)
            continue
        log.info('Write file `%s`.', dfilepath)
        with codecs.open(dfilepath, 'w') as f:
            f.write(json.dumps(dcfg, indent=2))
    return True


if __name__ == '__main__':
    main()
