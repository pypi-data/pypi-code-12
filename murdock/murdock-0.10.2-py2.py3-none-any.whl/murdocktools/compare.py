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
    Screening Comparison Report Creator
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Employs the Murdock API to create a report comparing multiple Murdock
    screenings. Use the command-line option ``--help`` for more information.

    :copyright: Copyright 2016 Malte Lichtner
    :license: Apache License, Version 2.0, see LICENSE for details.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import collections
import glob
import logging
import os
import sys

from murdock.results import ScreeningResult, DockingResult
import murdock.report
import murdock.report.latex
import murdock.report.sphinx
import murdock.logger
from murdock.misc import cleanup_filename


murdock.logger.Logger(
    console_level=logging.INFO, file_level=logging.INFO,
    logdir='.', filename='murdock-compare.log')

log = logging.getLogger('murdock-compare')

STATUS_KEYS = ('finished', 'failed', 'started')


class MultiScreeningReport(murdock.report.Report):

    def __init__(self, backends, sress, label, resdir=None):
        super(MultiScreeningReport, self).__init__(backends)
        self.sress = sress
        self.label = label
        self.resdir = resdir
        if self.resdir is None:
            self.resdir = label

    def create(self):
        if not self.sress:
            log.error('No screenings found.')
            return False
        self.clear()
        self.add_paragraph('Created: %s' % self.fmt_italic(self._timestamp()))
        self.add_headline(1, 'Status')
        self._add_progress_table()
        return True

    def _add_progress_table(self):
        thead = 'Total Progress'
        dhead = 'Docking Progress (%s)' % '-'.join(STATUS_KEYS)
        rows = []
        for sres in self.sress:
            row = murdock.report.TableRow()
            row['Screening']['label'] = sres.label
            dprgs = collections.OrderedDict()
            for dres in sres.dress:
                dprgs[dres.label] = []
                dprg = dres.progress
                for status_key in STATUS_KEYS:
                    try:
                        dprgs[dres.label].append(dprg[status_key])
                    except KeyError:
                        dprgs[dres.label].append(0)
            for i, shead in enumerate(STATUS_KEYS):
                row[thead][shead] = '%d' % sum(
                    _dp[i] for _dp in dprgs.values())
            for shead, dprg in dprgs.items():
                row[dhead][shead] = '-'.join('%d' % _dp for _dp in dprg)
            rows.append(row)
        rows.sort(key=lambda x: x['Screening']['label'])
        return self.add_table(rows, 'Progress')


def main():
    if _run():
        sys.exit(0)
    else:
        sys.exit(1)


def _parse_command_line():
    """Parse, validate and return command line arguments.
    """
    cmdline_parser = argparse.ArgumentParser(
        description='Murdock v%s Screening Comparison' %
        murdock.__version__)
    cmdline_parser.add_argument(
        'resdirs', type=str, nargs='+',
        help='one (or more) Murdock (docking/screening) results directorie(s)')
    cmdline_parser.add_argument(
        '-l', '--label', required=True, type=str, help='project label')
    cmdline_parser.add_argument(
        '-L', '--latex-executable', required=False, type=str,
        help='PDFLaTeX executable (usually named `pdflatex`) for automated '
        'building of the PDF report')
    cmdline_parser.add_argument(
        '-o', '--outdir', required=False, type=str, help='output directory')
    cmdline_parser.add_argument(
        '-S', '--sphinx-executable', required=False, type=str,
        help='Sphinx executable (usually named `sphinx-build`) for automated '
        'building of the HTML report')
    return cmdline_parser.parse_args()


def _run():
    cmdline = _parse_command_line()
    sress = []
    for sdir in cmdline.resdirs:
        if not os.path.isdir(sdir):
            continue
        slabel = os.path.basename(sdir.rstrip('/\\'))
        dfilepaths = glob.glob(
            os.path.join(sdir, 'dockings', '*', '*-results.json'))
        if not dfilepaths:
            log.warning('No dockings found in directory `%s`.', slabel)
            continue
        log.info('Add screening `%s`.', slabel)
        sres = ScreeningResult(label=slabel)
        for dfilepath in dfilepaths:
            dres = DockingResult(sres=sres)
            try:
                dres.load_json(dfilepath, done=False)
            except (IOError, ValueError) as exc:
                log.error(
                    'Can not parse docking result file `%s`: %s.', dfilepath,
                    str(exc))
                continue
            sres.add_dres(dres)
        sress.append(sres)
    title = 'Screening comparison: %s' % cmdline.label
    if cmdline.outdir is None:
        outdir = cleanup_filename(cmdline.label)
    else:
        outdir = cmdline.outdir
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    report_modules = [murdock.report.latex, murdock.report.sphinx]
    kwargs = {
        murdock.report.sphinx: {
            'outdir': os.path.join(outdir, 'sphinx'),
            'builder': 'html'},
        murdock.report.latex: {
            'outdir': os.path.join(outdir, 'latex')}}
    build_execs = {
        murdock.report.latex: cmdline.latex_executable,
        murdock.report.sphinx: cmdline.sphinx_executable}
    report_projects = [
        _backend.Project(
            mode='Screening comparison', title=title, label=cmdline.label,
            build_exec=build_execs[_backend], **kwargs[_backend]) for _backend
        in report_modules]
    for project in report_projects:
        project.create()
        if project.build_exec is not None:
            project.create_symlink(outdir)
    documents = [
        _project.get_document(cmdline.label) for _project in report_projects]
    report = MultiScreeningReport(documents, sress, cmdline.label)
    report.create()
    report.write()
    for project in report_projects:
        project.build()
    return True


if __name__ == '__main__':
    main()
