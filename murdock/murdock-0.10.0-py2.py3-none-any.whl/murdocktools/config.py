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
    Murdock Configuration File Creator
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Creates basic Murdock configuration files. Use the command-line option
    ``--help`` for more information.

    :copyright: Copyright 2016 Malte Lichtner
    :license: Apache License, Version 2.0, see LICENSE for details.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import codecs
import collections
import glob
import json
import logging
import os
import sys
import textwrap
import traceback

import murdock.logger
import murdock.misc


murdock.logger.Logger(
    console_level=logging.ERROR, file_level=logging.INFO,
    logdir='.', filename='murdock-config.log')

log = logging.getLogger('murdock-config')


PRESET_PATH = os.path.join(murdock.__path__[0], 'data', 'config_presets')


USAGE_EXAMPLES = """

Usage examples:
===============

  Example 1 (docking):
    murdock-config -l my_docking -r 10 -R my_receptor.mol2 -L my_ligand.mol2

  Example 2 (screening: one receptor, multiple ligands):
    murdock-config -l my_screening -r 10 -R my_receptor.mol2
                   -L my_ligand1.mol2 my_ligand2.mol2 my_ligand3.mol2

  Example 3 (screening: multiple receptors, one ligand):
    murdock-config -l my_screening -r 10
                   -R my_receptor1.mol2 my_receptor2.mol2 my_receptor3.mol2
                   -L my_ligand.mol2

  Example 4 (screening: multiple receptor-ligand pairs)
    murdock-config -l my_screening -r 10
                   -R my_receptor1.mol2 my_receptor2.mol2 my_receptor3.mol2
                   -L my_ligand1.mol2 my_ligand2 my_ligand3.mol2

  Example 5 (using optional arguments)
    murdock-config -l my_project -t My Project -u My Name -m screening
                   -T my_template.json -r 10 -s 1 -o my_project.json
                   -R my_receptor1.mol2 my_receptor2.mol2
                   --receptor-refs my_receptor1xray.mol2 my_receptor2xray.mol2
                   -L my_ligand1.mol2 my_ligand2.mol2
                   --ligand-refs my_ligand1xray.mol2 my_ligand2xray.mol2
"""


TEMPLATE_FORMATS = """
  Format 1 (basic template):
    {
      "steps": [ ... ]
    }

  Format 2 (docking configuration file):
    {
      "docking": {
        ...,
        "steps" : [ ... ],
        ...
      }
    }

  Format 3 (screening configuration file):
    {
      "screening": {
        ...,
        "steps" : [ ... ],
        ...
      }
    }
"""


TEMPLATE_PRESETS = """

Template presets (argument -T)
==============================

%s

"""


def main():
    if _run():
        sys.exit(0)
    else:
        sys.exit(1)


def _create_label(rec_fp, lig_fp):
    reclabel = os.path.splitext(os.path.basename(rec_fp))[0]
    liglabel = os.path.splitext(os.path.basename(lig_fp))[0]
    return '%s_%s' % (reclabel, liglabel)


def _fmt_presets():
    presets = [
        os.path.basename(_fp).split('-preset.json')[0] for _fp in
        glob.glob(os.path.join(PRESET_PATH, '*-preset.json'))]
    presets.sort()
    info_filepaths = [
        os.path.join(PRESET_PATH, '%s-info.txt' % _p)
        for _p in presets]
    infos = []
    for filepath in info_filepaths:
        try:
            with codecs.open(filepath, 'r', encoding='utf-8') as f:
                s = f.read()
        except:
            s = '(no description found)'
        infos.append(s)
    lines = []
    for preset, info in zip(presets, infos):
        info_block = ' '.join([_l.strip() for _l in info.splitlines()])
        info_wrapped = textwrap.wrap(info_block, 74 - len(preset))
        lines.append('  %s : %s' % (preset, info_wrapped[0]))
        if len(info_wrapped) > 1:
            lines.extend([
                ' ' * len(preset) + '     %s' % _i for _i in
                info_wrapped[1:]])
        lines.append('\n')
    return '\n'.join(lines)


def _log_template_error(template_path):
    log.fatal(
        'File `%s` can not be used as template. Valid formats are:',
        template_path)
    for line in TEMPLATE_FORMATS.splitlines():
        log.fatal(line)
    log.fatal(
        'Please refer to the Murdock documentation for more information on '
        'the required template format or use one of the Murdock default '
        'templates (check `murdock-config --help`).')


def _parse_command_line():
    """Parse, validate and return command line arguments.
    """
    epilog = TEMPLATE_PRESETS % _fmt_presets() + '\n\n' + USAGE_EXAMPLES
    cmdline_parser = argparse.ArgumentParser(
        description='Murdock v%s Configuration File Creator' %
        murdock.__version__, epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    cmdline_parser.add_argument(
        '-l', '--label', required=True, help='docking/screening label')
    cmdline_parser.add_argument(
        '-L', '--ligands', nargs='+', required=True,
        help='one or multiple ligand file/s')
    cmdline_parser.add_argument(
        '--ligand-refs', nargs='+', required=False,
        help='ligand reference files (one per ligand)')
    cmdline_parser.add_argument('-m', '--mode',
        help='Murdock working mode: `docking` or `screening` (default: auto)')
    cmdline_parser.add_argument(
        '-o', '--output',
        help='JSON configuration file output path (default: stdout)')
    cmdline_parser.add_argument(
        '-r', '--runs', type=int, required=True,
        help='number of independent runs per docking')
    cmdline_parser.add_argument(
        '-R', '--receptors', nargs='+', required=True,
        help='one or multiple receptor file/s')
    cmdline_parser.add_argument(
        '--receptor-refs', nargs='+', required=False,
        help='receptor reference files (one per ligand)')
    cmdline_parser.add_argument(
        '-s', '--steps', type=int,
        help='use (only) the first N docking steps from the template '
        '(default: use all)')
    cmdline_parser.add_argument(
        '-t', '--title', nargs='+',
        help='docking/screening title (default: use label)')
    cmdline_parser.add_argument(
        '-T', '--template',
        help='search and scoring parameters given as either a) a Murdock '
        'configuration preset (see below) or b) an existing docking/screening '
        'configuration file (default: use `default` preset)',
        default='default')
    cmdline_parser.add_argument(
        '-u', '--user', nargs='+', help='user name (default: auto)')
    return cmdline_parser.parse_args()


def _process_cmdline(cmdline):
    if not os.path.isfile(cmdline.template):
        cmdline.template_path = os.path.join(
            PRESET_PATH, '%s-preset.json' % cmdline.template)
        if not os.path.exists(cmdline.template_path):
            log.fatal(
                'Neither a file nor a Murdock template named `%s` was found.',
                cmdline.template)
            return False
    else:
        cmdline.template_path = cmdline.template
    if cmdline.runs <= 0:
        log.fatal(
            'The command-line argument `-r/--runs` must be greater '
            'than zero.')
        return False
    if cmdline.steps is not None and cmdline.steps <= 0:
        log.fatal(
            'The command-line argument `-s/--steps` must be greater '
            'than zero.')
        return False
    if cmdline.mode not in (None, 'docking', 'screening'):
        log.fatal(
            'The command-line argument `-m/--mode` must be either `docking` '
            'or `screening` (without quotation marks). If the argument is not '
            'set, the mode is chosen based on the number of ligands and '
            'receptors.')
        return False
    if cmdline.mode is None:
        if len(cmdline.ligands) > 1 or len(cmdline.receptors) > 1:
            cmdline.mode = 'screening'
        else:
            cmdline.mode = 'docking'
    if (not cmdline.ligands or not cmdline.receptors) or not (
            len(cmdline.ligands) == len(cmdline.receptors) or
            len(cmdline.ligands) == 1 or
            len(cmdline.receptors) == 1):
        log.fatal(
            'The command-line arguments `-L/--ligands` and '
            '`-R/--receptors` can be used in one of four ways: a) one '
            'ligand and one receptor, b) one ligand and multiple receptors, '
            'c) multiple ligands and one receptor or d) an equal number of '
            'ligands and receptors. Given are %d ligands and %d receptors.',
            len(cmdline.ligands),
            len(cmdline.receptors))
        return False
    if cmdline.mode == 'docking':
        if len(cmdline.ligands) > 1 or len(cmdline.receptors) > 1:
            log.fatal(
                'If the command-line argument `-m/--mode` is set to '
                '`docking`, only one receptor and one ligand must be given.')
            return False
    if (
            cmdline.ligand_refs and
            len(cmdline.ligand_refs) != len(cmdline.ligands)):
        log.fatal(
            'The number of ligand reference files `--ligand-refs` (given %d) '
            'does not correspond to the number of ligand files `-L/--ligands` '
            '(given %d).', len(cmdline.ligand_refs), len(cmdline.ligands))
        return False
    if (
            cmdline.receptor_refs and
            len(cmdline.receptor_refs) != len(cmdline.receptors)):
        log.fatal(
            'The number of receptor reference files `--receptor-refs` (given '
            '%d) does not correspond to the number of receptor files '
            '`-R/--receptors` (given %d).', len(cmdline.receptor_refs),
            len(cmdline.receptors))
        return False
    murdock.misc.cleanup_filename(cmdline.label)
    if cmdline.title:
        cmdline.title = ' '.join(cmdline.title)
    else:
        cmdline.title = cmdline.label
    if cmdline.user:
        cmdline.user = ' '.join(cmdline.user)
    if cmdline.output:
        if not cmdline.output.endswith('.json'):
            cmdline.output = '%s.json' % cmdline.output
        if os.path.exists(cmdline.output):
            log.fatal('File `%s` already exists.', cmdline.output)
            return False
    filepaths = cmdline.ligands + cmdline.receptors
    if cmdline.ligand_refs:
        filepaths += cmdline.ligand_refs
    if cmdline.receptor_refs:
        filepaths += cmdline.receptor_refs
    for fp in filepaths:
        if not os.path.exists(fp):
            log.warning('File `%s` does not exist.', fp)
    log.info('Create Murdock v%s configuration file:' % murdock.__version__)
    for name, val in cmdline.__dict__.iteritems():
        if val is None:
            continue
        if isinstance(val, list):
            log.info('  %s:', name)
            for v in val:
                log.info('    %s', v)
        else:
            log.info('  %s: %s', name, val)
    return True


def _load_template(filepath):
    try:
        t = murdock.misc.load_ordered_json(filepath)
    except IOError:
        log.fatal('Template file `%s` does not exist.', filepath)
        return False
    except ValueError:
        log.fatal(
            'Template file `%s` is not a valid JSON file. Check JSON format '
            'specification (http://www.json.org). %s', filepath,
            traceback.format_exc().splitlines()[-1])
        return False
    return t


def _run():
    cmdline = _parse_command_line()
    if not _process_cmdline(cmdline):
        return False
    if not _write_configfile(cmdline):
        return False
    return True


def _write_configfile(cmdline):
    outdict = collections.OrderedDict()
    if cmdline.mode == 'docking':
        c = outdict['docking'] = collections.OrderedDict()
    else:
        c = outdict['screening'] = collections.OrderedDict()
    c['title'] = cmdline.title
    if cmdline.title != cmdline.label:
        c['label'] = cmdline.label
    if cmdline.user:
        c['user'] = cmdline.user
    c['number_of_runs'] = cmdline.runs
    if cmdline.mode == 'docking':
        rec = collections.OrderedDict()
        rec['filepath'] = cmdline.receptors[0]
        if cmdline.receptor_refs:
            rec['ref_filepath'] = cmdline.receptor_refs[0]
        lig = collections.OrderedDict()
        lig['filepath'] = cmdline.ligands[0]
        if cmdline.ligand_refs:
            lig['ref_filepath'] = cmdline.ligand_refs[0]
        inp = c['input_data'] = collections.OrderedDict()
        inp['receptor'] = rec
        inp['ligands'] = [lig]
        c['input_data'] = inp
    elif cmdline.mode == 'screening':
        inplist = c['input_data'] = []
        if len(cmdline.receptors) == len(cmdline.ligands):
            for i, (recfp, ligfp) in enumerate(zip(
                    cmdline.receptors, cmdline.ligands)):
                inp = collections.OrderedDict()
                inp['title'] = _create_label(recfp, ligfp)
                rec = collections.OrderedDict()
                rec['filepath'] = recfp
                if cmdline.receptor_refs:
                    rec['ref_filepath'] = cmdline.receptor_refs[i]
                inp['receptor'] = rec
                lig = collections.OrderedDict()
                lig['filepath'] = ligfp
                if cmdline.ligand_refs:
                    lig['ref_filepath'] = cmdline.ligand_refs[i]
                inp['ligands'] = [lig]
                inplist.append(inp)
        elif len(cmdline.receptors) == 1:
            inp = collections.OrderedDict()
            inp['title'] = 'default'
            rec = collections.OrderedDict()
            rec['filepath'] = cmdline.receptors[0]
            if cmdline.receptor_refs:
                rec['ref_filepath'] = cmdline.receptor_refs[0]
            inp['receptor'] = rec
            inplist.append(inp)
            for i, ligfp in enumerate(cmdline.ligands):
                inp = collections.OrderedDict()
                inp['title'] = _create_label(cmdline.receptors[0], ligfp)
                lig = collections.OrderedDict()
                lig['filepath'] = ligfp
                if cmdline.ligand_refs:
                    lig['ref_filepath'] = cmdline.ligand_refs[i]
                inp['ligands'] = [lig]
                inplist.append(inp)
        elif len(cmdline.ligands) == 1:
            inp = collections.OrderedDict()
            inp['title'] = 'default'
            lig = collections.OrderedDict()
            lig['filepath'] = cmdline.ligands[0]
            if cmdline.ligand_refs:
                lig['ref_filepath'] = cmdline.ligand_refs[0]
            inp['ligands'] = [lig]
            inplist.append(inp)
            for i, recfp in enumerate(cmdline.receptors):
                inp = collections.OrderedDict()
                inp['title'] = _create_label(recfp, cmdline.ligands[0])
                rec = collections.OrderedDict()
                rec['filepath'] = recfp
                if cmdline.receptor_refs:
                    rec['ref_filepath'] = cmdline.receptor_refs[i]
                inp['receptor'] = rec
                inplist.append(inp)
        c['input_data'] = inplist
    try:
        template = _load_template(cmdline.template_path)
        if not template:
            _log_template_error(cmdline.template_path)
            return False
        preprocessing = None
        if 'docking' in template and 'steps' in template['docking']:
            steps = template['docking']['steps']
            if 'preprocessing' in template['docking']:
                preprocessing = template['preprocessing']
        elif 'screening' in template and 'steps' in template['screening']:
            steps = template['screening']['steps']
            if 'preprocessing' in template['screening']:
                preprocessing = template['preprocessing']
        elif 'steps' in template:
            steps = template['steps']
            if 'preprocessing' in template:
                preprocessing = template['preprocessing']
        else:
            log.fatal(
                'The required `steps` section was not found in the template '
                'file `%s`.', cmdline.template_path)
            _log_template_error(cmdline.template_path)
            return False
        if cmdline.steps:
            if cmdline.steps > len(steps):
                if cmdline.template == cmdline.template_path:
                    loc = 'template file `%s`' % cmdline.template
                else:
                    loc = 'configuration preset `%s`' % cmdline.template
                log.error(
                    'The command-line parameter `-s/--steps` is set to '
                    '%d but the %s contains only %d docking steps (%s).',
                    cmdline.steps, loc, len(steps),
                    ', '.join(['`%s`' % _s['title'] for _s in steps]))
                return False
            steps = steps[:cmdline.steps]
    except:
        _log_template_error(cmdline.template_path)
        return False
    if preprocessing is not None:
        c['preprocessing'] = preprocessing
    c['steps'] = steps
    outstr = json.dumps(outdict, indent=2).encode('utf-8') + '\n'
    if cmdline.output:
        with codecs.open(cmdline.output, 'w', encoding='utf-8') as f:
            f.write(outstr)
        log.info('Configuration file written to `%s`.' % cmdline.output)
    else:
        sys.stdout.write(outstr)
        log.info('Configuration file written to standard output.')
    return True


if __name__ == '__main__':
    main()
