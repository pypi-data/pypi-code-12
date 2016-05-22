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
    Report Table Creator
    ~~~~~~~~~~~~~~~~~~~~

    Employs the Murdock API to create formatted tables. Use the command-line
    option ``--help`` for more information.

    :copyright: Copyright 2016 Malte Lichtner
    :license: Apache License, Version 2.0, see LICENSE for details.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import codecs
import logging
import os
import sys
import traceback

import murdock.logger
import murdock.misc


murdock.logger.Logger(
    console_level=logging.ERROR, file_level=logging.INFO,
    logdir='.', filename='murdock-tables.log')

log = logging.getLogger('murdock-config')


def main():
    if _run():
        sys.exit(0)
    else:
        sys.exit(1)


def _append_to_table(i_run, value, dres=None, steptitle=None, label=None):
    run_num = i_run + 1
    head_fmt = '{:^3s} {:^11s}\n'
    val_fmt = '{:>3d} {:>11.5f}\n'
    filepath = ''
    if dres is not None:
        filepath += dres['label']
    if label is not None:
        filepath += '-scores'
    if steptitle is not None:
        filepath += '-%s' % steptitle
    if not filepath:
        raise ArgumentError('Can not create a filepath from nothing.')
    filepath += '.txt'
    if not os.path.exists(filepath):
        with codecs.open(filepath, 'w', encoding='utf-8') as f:
            f.write(head_fmt.format('Run', 'Score'))
    with codecs.open(filepath, 'a', encoding='utf-8') as f:
        f.write(val_fmt.format(run_num, value))
    return True


def _create_tables(dres, steptitles=None):
    if steptitles is not None:
        found = []
    if 'runs' not in dres:
        return False
    for i_run, run in enumerate(dres['runs']):
        try:
            steps = run['steps']
        except KeyError:
            continue
        for i_step, step in enumerate(steps):
            steptitle = step['step title']
            if steptitles is not None and steptitle not in steptitles:
                continue
            try:
                sres = step['results']
            except KeyError:
                continue
            try:
                score = sres['score']
            except KeyError:
                continue
            total = score['total']
            _append_to_table(
                i_run, total, dres=dres, steptitle=steptitle, label='scores')
            if steptitles is not None and steptitle not in found:
                found.append(steptitle)
    if steptitles is not None:
        not_found = ', '.join(
            ['`%s`' % _t for _t in steptitles if _t not in found])
        if not_found:
            log.error('Missing steps (%s) in `%s`.', not_found, dres['label'])
            return False
    return True


def _load_results(filepath):
    try:
        t = murdock.misc.load_ordered_json(filepath)
    except IOError:
        log.fatal('Result file `%s` does not exist.', filepath)
        return False
    except ValueError:
        log.fatal(
            'File `%s` is not a valid JSON file. This should not happen if '
            'the given file is a docking result file written by Murdock. %s',
            traceback.format_exc().splitlines()[-1])
        return False
    try:
        return t['docking']
    except KeyError:
        if 'screening' in t:
            log.fatal(
                'File `%s` is a screening result file. The file given must be '
                'a docking result file (found in a docking result directory).',
                filepath)
        else:
            log.fatal(
                'File `%s` is not a docking result file (there should be a '
                'key `docking` at the top of the JSON structure.', filepath)
        return False


def _parse_command_line():
    """Parse, validate and return command line arguments.
    """
    cmdline_parser = argparse.ArgumentParser(
        description='Murdock v%s Table Creator' % murdock.__version__)
    cmdline_parser.add_argument(
        'result_files', nargs='+',
        help='docking result JSON file/s (`*-results.json`)')
    cmdline_parser.add_argument(
        '-s', '--step-titles', nargs='+',
        help='list of step titles to be included (default: <all>)')
    return cmdline_parser.parse_args()


def _run():
    cmdline = _parse_command_line()
    for filepath in cmdline.result_files:
        dres = _load_results(filepath)
        if not dres:
            continue
        if not _create_tables(dres, cmdline.step_titles):
            continue
    return True


if __name__ == '__main__':
    main()
