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
    Murdock Report Creator
    ~~~~~~~~~~~~~~~~~~~~~~

    Employs the Murdock API to create (or update) the report in an existing
    Murdock result directory. Use the command-line option ``--help`` for more
    information.

    .. warning::

        Murdock mode `training` is not implemented yet.

    :copyright: Copyright 2016 Malte Lichtner
    :license: Apache License, Version 2.0, see LICENSE for details.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import glob
import logging
import os
import sys

import murdock.logger
import murdock.report
import murdock.report.sphinx
import murdock.report.latex
from murdock.runner.docking import get_search_filepath
from murdock.misc import fmtpath


murdock.logger.Logger(
    console_level=logging.INFO, file_level=logging.INFO,
    logdir='.', filename='murdock-report.log')

log = logging.getLogger('murdock-report')


class ReportCreator(object):

    def __init__(self, resdir, cmdline):
        if resdir.endswith('/'):
            resdir = resdir[:-1]
        self.cmdline = cmdline
        self.resdir = resdir
        self.report_projects = None

    def run(self):
        if not os.path.isdir(self.resdir):
            log.error(
                'Path to result directory `%s` is not a directory.',
                self.resdir)
            return False
        label = os.path.basename(self.resdir)
        filepath = os.path.join(self.resdir, '%s-results.json' % label)
        resfile = self._load_resultfile(filepath)
        if not resfile:
            return False
        mode = resfile.keys()[0]
        log.info('Set mode to %s.', mode)
        if mode == 'docking':
            res = murdock.results.DockingResult()
        elif mode == 'screening':
            res = murdock.results.ScreeningResult()
        else:
            raise NotImplementedError('Mode `%s` not implemented yet.' % mode)
        res.from_json(resfile[mode])
        try:
            user = resfile[mode]['user']
        except KeyError:
            user = None
        report_modules = [murdock.report.sphinx, murdock.report.latex]
        build_execs = {
            murdock.report.sphinx: self.cmdline.sphinx_executable,
            murdock.report.latex: self.cmdline.latex_executable}
        kwargs = {
            murdock.report.sphinx: {
                'outdir': os.path.join(self.resdir, 'sphinx')},
            murdock.report.latex: {
                'outdir': os.path.join(self.resdir, 'latex')}}
        self.report_projects = [
            _module.Project(
                mode=mode.capitalize(), title=res.title, label=res.label,
                user=user, build_exec=build_execs[_module], **kwargs[_module])
            for _module in report_modules]
        for project in self.report_projects:
            project.create()
            if project.build_exec is not None:
                project.create_symlink(self.resdir)
        if mode == 'docking':
            if self.cmdline.sort:
                log.warning(
                    'Command-line argument `--sort` has no effect in '
                    '`docking` mode.')
            self._create_docking_report(res, self.resdir)
            for project in self.report_projects:
                project.build()
        elif mode == 'screening':
            dfilepaths = glob.glob(
                os.path.join(self.resdir, 'dockings', '*', '*-results.json'))
            if not dfilepaths:
                log.warning('No docking result files found for `%s`.', label)
                return False
            if self.cmdline.sort:
                dfilepaths.sort()
            for dfilepath in dfilepaths:
                dres = murdock.results.DockingResult()
                dres.load_json(dfilepath)
                res.add_dres(dres)
            self._create_screening_report(res)
        return True

    def _load_resultfile(self, filepath):
        log.info('Load result file `%s`.', fmtpath(filepath, self.resdir))
        try:
            res = murdock.misc.load_ordered_json(filepath)
        except ValueError as exc:
            log.error(
                'Can not parse result file `%s`: %s.', filepath, str(exc))
            return False
        except IOError as exc:
            log.error(
                'No existing result file `%s` found.', filepath)
            return False
        if len(res.keys()) != 1:
            log.error('File `%s` is no Murdock result file.', filepath)
            return False
        if res.keys()[0] == 'training':
            raise NotImplementedError(
                'Mode `training` is not implemented yet.')
        if res.keys()[0] not in ('docking', 'screening'):
            log.error('File `%s` is no Murdock result file.', filepath)
            return False
        return res

    def _create_docking_report(self, dres, resdir, screening=False):
        log.info('Update docking report `%s` (`%s`).', dres.title, dres.label)
        search_filepath = get_search_filepath(resdir, dres.label)
        backends = [
            _project.get_document(dres.label) for _project in
            self.report_projects]
        report = murdock.report.DockingReport(
            backends=backends, resdir=resdir, result=dres,
            pymolexec=self.cmdline.pymol_executable,
            pymolscript=self.cmdline.pymol_script,
            num_threads=self.cmdline.threads_per_docking,
            draw_resscore_charts=self.cmdline.residue_score_charts,
            draw_resdist_charts=self.cmdline.residue_distance_charts)
        if screening:
            report.add_headline(0, dres.title)
        report.create()
        report.write()
        for project in self.report_projects:
            project.build()
        return True

    def _create_screening_report(self, sres):
        log.info(
            'Update screening report `%s` (`%s`).', sres.title, sres.label)
        backends = [
            _project.get_document(sres.label) for _project in
            self.report_projects]
        report = murdock.report.ScreeningReport(
            backends=backends, resdir=self.resdir, result=sres,
            pymolexec=self.cmdline.pymol_executable,
            pymolscript=self.cmdline.pymol_script,
            num_threads=self.cmdline.threads_per_docking)
        report.create()
        report.write()
        for project in self.report_projects:
            project.build()
        for dres in sres.dress:
            resdir = os.path.join(self.resdir, 'dockings', dres.label)
            self._create_docking_report(dres, resdir, screening=True)
        return True


def main():
    if _run():
        sys.exit(0)
    else:
        sys.exit(1)


def _parse_command_line():
    """Parse, validate and return command line arguments.
    """
    cmdline_parser = argparse.ArgumentParser(
        description='Murdock v%s report creator' %
        murdock.__version__)
    cmdline_parser.add_argument(
        'resdirs', type=str, nargs='+',
        help='one (or more) Murdock (docking/screening) results directorie(s)')
    cmdline_parser.add_argument(
        '-L', '--latex-executable', required=False, type=str,
        default=None, help='PDFLaTeX executable (usually named '
        '`pdflatex`) for automated building of the PDF report')
    cmdline_parser.add_argument(
        '-P', '--pymol-executable', required=False, type=str, default=None,
        help='PyMOL executable for automated PNG picture creation')
    cmdline_parser.add_argument(
        '--pymol-script', required=False, type=str, default=None,
        help='PyMOL script to be run during PNG picture creation')
    cmdline_parser.add_argument(
        '--residue-distance-charts', action='store_true', help='draw '
        'residue distance charts for each docking (may result in many '
        'small files)')
    cmdline_parser.add_argument(
        '--residue-score-charts', action='store_true', help='draw '
        'residue score charts for each docking (may result in many small '
        'files)')
    cmdline_parser.add_argument(
        '--sort', action='store_true', help='whether to sort dockings (within '
        'a screening) alphabetically by label (default: False)')
    cmdline_parser.add_argument(
        '-S', '--sphinx-executable', required=False, type=str,
        default=None, help='Sphinx executable (usually named '
        '`sphinx-build`) for automated building of the HTML report')
    cmdline_parser.add_argument(
        '-t', '--threads-per-docking', required=False, type=int,
        help='number of CPU threads used for each docking process (sets '
        'the environment variables OMP_NUM_THREADS and MKL_NUM_THREADS; '
        'default: unlimited)')
    cmdline = cmdline_parser.parse_args()
    if cmdline.pymol_script is not None:
        cmdline.pymol_script = os.path.expanduser(cmdline.pymol_script)
    return cmdline


def _run():
    pwd = os.getcwd()
    cmdline = _parse_command_line()
    for resdir in cmdline.resdirs:
        resdir = os.path.abspath(resdir)
        if not os.path.isdir(resdir):
            continue
        os.chdir(os.path.join(resdir, '..'))
        ReportCreator(resdir, cmdline).run()
        log.info('All reports in `%s` created.' % resdir)
        os.chdir(pwd)


if __name__ == '__main__':
    main()
