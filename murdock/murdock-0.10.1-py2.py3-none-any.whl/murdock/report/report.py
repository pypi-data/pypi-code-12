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
Module :mod:`murdock.report.report`
-----------------------------------

This module creates human-readable reports using different backends. It
provides the base classes :class:`Report` and :class:`RuntimeReport` as well as
an implementation for each Murdock runner: :class:`DockingReport`,
:class:`ScreeningReport` and `TrainingReport`.

In addition, it specifies the report API by providing the base classes
:class:`Project` and :class:`Document`. A list of implemented report backends
is given :mod:`here <murdock.report>`.

"""

# TODO(malte.lichtner@gmail.com): Add configuration file to all reports.
# TODO(malte.lichtner@gmail.com): Add rotatable bonds to docking results table.
# TODO(malte.lichtner@gmail.com): Add sampling figures to docking report.
# TODO(malte.lichtner@gmail.com): Add residue matching figures to all reports.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import range
from future.utils import listitems, listvalues, viewitems, viewvalues

import codecs
import collections
import logging
import os
import re
import time
import traceback
import uuid

import numpy
import scipy.constants

import murdock.math
import murdock.misc
import murdock.results
import murdock.pymol

try:
    import matplotlib
    import murdock.plot
    MATPLOTLIB = True
except ImportError as exc:
    MATPLOTLIB = False
    MATPLOTLIB_ERROR = exc

log = logging.getLogger('report')

DEFAULT_PLOTSIZE = 400
DEFAULT_PICSIZE = 800

if MATPLOTLIB:
    LEGEND_AA_TYPES = collections.OrderedDict((
        ('positively charged AA', murdock.plot.RESIDUE_COLORS['ARG']),
        ('negatively charged AA', murdock.plot.RESIDUE_COLORS['ASP']),
        ('polar uncharged AA', murdock.plot.RESIDUE_COLORS['SER']),
        ('special case AA', murdock.plot.RESIDUE_COLORS['CYS']),
        ('hydrophobic AA', murdock.plot.RESIDUE_COLORS['ALA']),
        ('other residue', murdock.plot.RESIDUE_COLORS['other'])))
    LEGEND_DOCKED = collections.OrderedDict((
        ('worst score', 'b'), ('best score', 'r'), ('reference', 'g')))
else:
    log.warning(
        'Error during import of `matplotlib` or related package: %s',
        MATPLOTLIB_ERROR)
    log.warning('Result plots will not be created.')
    LEGEND_AA_TYPES = None
    LEGEND_DOCKED = None


class ReportError(Exception):
    pass


class Project(object):
    """Parent class for report projects to be used for different backends.
    """

    def __init__(
            self, mode, title, label, outdir, user=None, build_exec=None):
        #: path to out directory
        self.outdir = outdir
        #: running mode (`Docking` or `Screening`)
        self.mode = mode
        #: project title
        self.title = title
        #: project label for result filenames (no special characters)
        self.label = murdock.misc.cleanup_filename(label)
        #: program user and copyright holder (on paper) for the results
        self.user = user
        #: build executable
        self.build_exec = build_exec
        #: dictionary of documents
        self.documents = collections.OrderedDict()

    def create(self):
        if self.outdir is None:
            return False
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)
        self.add_document(self.label)
        return True

    def create_symlink(self, outdir):
        targetpath, linkname = self.get_build_link()
        linkpath = os.path.join(outdir, linkname)
        reltargetpath = os.path.relpath(targetpath, outdir)
        if os.path.lexists(linkpath):
            os.remove(linkpath)
        try:
            os.symlink(reltargetpath, linkpath)
        except OSError:
            log.error(
                'Symbolic link `%s`->`%s` can not be created.',
                murdock.misc.fmtpath(linkpath, outdir),
                murdock.misc.fmtpath(reltargetpath, outdir))
            return False
        return True

    def get_document(self, label):
        if label not in self.documents:
            self.add_document(label)
        return self.documents[label]

    def add_document(self, label, document=None):
        if label in self.documents:
            raise Exception(
                'Document labeled `%s` already exists in project `%s`.' %
                (label, self.label))
        if document is None:
            document = self._new_document(label=label)
        self.documents[label] = document
        if document.project is None:
            document.project = self
        self._write_indexfile()
        return True

    def _get_main_doc(self):
        try:
            return self.documents[self.label]
        except KeyError:
            return None

    def _get_toc_docs(self):
        return collections.OrderedDict([
            (_label, _doc) for _label, _doc in viewitems(self.documents) if
            _label != self.label and os.path.exists(_doc._get_filepath())])
        return True


class Document(object):

    def __init__(
            self, outdir, label, ext, project=None, headline_offset=0,
            plot_ext=None):
        #: output directory
        self.outdir = outdir
        #: document label
        self.label = label
        #: output file extension
        self.ext = ext
        #: headline level offset
        self.headline_offset = headline_offset
        #: plot file extension
        self.plot_ext = plot_ext
        #: class:`Project` instance this Document belongs to
        self.project = project
        #: content of output file
        self._output = ''
        #: current level of indentation
        self._indent = ''
        #: dictionary of substitution to be performed in :meth:`substitute()`
        self._subs = collections.OrderedDict()

    def add_bullet_list(self, struct):
        self.add_paragraph(self.fmt_bullet_list(struct))

    def add_newline(self):
        if not self._output.endswith('\n\n'):
            self._output += '\n'
        return True

    def add_paragraph(self, text):
        for line in text.splitlines():
            self._output += self._indent + line + '\n'
        return True

    def add_table(self, rows, headline, ttype=None):
        table = self.get_table(ttype)
        for row in rows:
            table.add_row(row)
        if not table.rows:
            return False
        self.add_headline(2, headline)
        self.add_paragraph(table.create())
        return True

    def clear(self):
        self._output = ''
        self._subs.clear()
        return True

    def create_subst(self, uuid_key, text):
        if uuid_key in self._subs and self._subst[uuid_key] != text:
            raise ReportError(
                'Placeholder `%s` already defined with text `%s`. Can not set '
                'for text `%s`.' % (uuid_key, self._subs[uuid_key], text))
        self._subs[uuid_key] = text
        return True

    def decrease_indent(self, amount=2):
        self._indent = ' ' * (len(self._indent) - amount)
        return True

    def substitute(self):
        """Substitute all uuid_keys (:attr:`subs`) in :attr:`output`.
        """
        self._output = substitute_all(self._output, self._subs)
        return True

    def increase_indent(self, amount=2):
        self._indent = ' ' * (len(self._indent) + amount)
        return True

    def read(self, filelabel):
        filepath = os.path.join(self.outdir, '%s%s' % (filelabel, self.ext))
        with codecs.open(filepath, 'r', encoding='utf-8') as f:
            self._output = f.read()

    def write(self):
        self.substitute()
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)
        filepath = self._get_filepath()
        with codecs.open(filepath, 'w', encoding='utf-8') as f:
            f.write(self._output)

    def _get_filepath(self):
        return os.path.join(self.outdir, '%s%s' % (self.label, self.ext))


class Report(object):

    def __init__(self, backends, figdir='figures'):
        #: list of backends to be used for output formatting
        self.backends = backends
        #: figure dictionary
        self.figdir = figdir

    def add_bullet_list(self, struct):
        for backend in self.backends:
            backend.add_bullet_list(struct)

    def add_figure(
            self, filepath, caption=None, legend=None, scale=None, ext=None):
        label = os.path.basename(filepath)
        uuid_key = _uuid_key()
        for backend in self.backends:
            outdir = os.path.dirname(os.path.relpath(filepath, backend.outdir))
            if ext is not None and label.endswith(ext):
                label = os.path.splitext(label)[0]
            elif backend.plot_ext is not None and label.endswith(
                    backend.plot_ext):
                label = os.path.splitext(label)[0]
            figtext = backend.add_figure(
                outdir, label, caption=caption, legend=legend, scale=scale,
                ext=ext)
            backend.create_subst(uuid_key, figtext)
        return uuid_key

    def add_headline(self, level, text):
        for backend in self.backends:
            backend.add_headline(level, text)
        return True

    def add_newline(self):
        for backend in self.backends:
            backend.add_newline()
        return True

    def add_paragraph(self, text):
        for backend in self.backends:
            backend.add_paragraph(text)

    def add_plot(self, plot, outdir, label, overwrite=True, scale=None):
        filepath = self._save_plot(plot, outdir, label, overwrite=overwrite)
        return self.add_figure(filepath, scale=scale)

    def add_table(self, rows, headline, ttype=None):
        for backend in self.backends:
            backend.add_table(rows, headline, ttype)
        return True

    def clear(self):
        for backend in self.backends:
            backend.clear()

    def fmt_link(self, text, **kwargs):
        uuid_key = _uuid_key()
        for backend in self.backends:
            backend.create_subst(
                uuid_key, backend.fmt_figure(text, **kwargs))
        return uuid_key

    def fmt_bold(self, text):
        uuid_key = _uuid_key()
        for backend in self.backends:
            backend.create_subst(uuid_key, backend.fmt_bold(text))
        return uuid_key

    def fmt_bullet_list(self, struct):
        uuid_key = _uuid_key()
        for backend in self.backends:
            backend.create_subst(uuid_key, backend.fmt_bullet_list(struct))
        return uuid_key

    def fmt_italic(self, text):
        uuid_key = _uuid_key()
        for backend in self.backends:
            backend.create_subst(uuid_key, backend.fmt_italic(text))
        return uuid_key

    def write(self):
        for backend in self.backends:
            backend.write()
        return True

    def _save_plot(self, plot, outdir, label, overwrite=True):
        filepath = os.path.join(outdir, self.figdir, label)
        for ext in set(
                [_backend.plot_ext for _backend in self.backends if
                _backend.plot_ext is not None]):
            if not overwrite and os.path.exists(filepath):
                continue
            plot.save_plot(filepath, width=plot.width, ext=ext)
        plot.close()
        return filepath

    def _timestamp(self, t=None):
        return time.strftime('%a, %d %b %Y, %H:%M:%S', time.localtime(t))


class RunnerReport(Report):

    def __init__(
            self, backends, resdir, result, headline=None, num_runs=None,
            num_threads=None, pymolexec=None, pymolscript=None):
        super(RunnerReport, self).__init__(backends)
        #: result directory (contains screening/docking results)
        self.resdir = resdir
        #: result container
        self.res = result
        #: top-level headline
        self.headline = headline
        #: number of runs per docking
        self.num_runs = num_runs
        #: number of CPU threads used for external executalbes such as `PyMOL`
        #: (None means unlimited)
        self.num_threads = num_threads
        #: PyMOL executable (for picture creation)
        self.pymolexec = pymolexec
        #: (optional) path to PyMOL script to be included in picture creation
        self.pymolscript = pymolscript
        #: output directory for PyMOL scripts
        self.pymoldir = os.path.join(resdir, 'pymol', 'pictures')
        if not os.path.exists(self.pymoldir):
            os.makedirs(self.pymoldir)
        if self.num_runs is None:
            self.num_runs = max(_run.serial for _run in self.res.iter_runs())

    def _add_header(self, full=True):
        if not full:
            stored = {_backend: _backend._output for _backend in self.backends}
        self.clear()
        if self.headline is not None:
            self.add_headline(0, self.headline)
        self.add_paragraph('Created: %s' % self.fmt_italic(self._timestamp()))
        self.add_headline(1, 'Status')
        if not MATPLOTLIB or not self._add_progressbar():
            self._add_progresstext()
        self.add_headline(1, 'Info')
        self._add_timetable()
        if self.res.notes:
            self.add_headline(2, 'Notes')
            self.add_bullet_list(self.res.notes)
        if not full:
            for backend in self.backends:
                new_lines = backend._output.splitlines()
                stored_lines = stored[backend].splitlines()[len(new_lines):]
                backend._output = '\n'.join(new_lines + stored_lines)
        return True

    def _add_docked_pictures(
            self, width=DEFAULT_PICSIZE, height=DEFAULT_PICSIZE,
            topscored_fract=None):
        rec, recdir = self.get_receptor_directory()
        if rec is None:
            return False
        rec_filepath = os.path.join(recdir, rec.filepath)
        if rec.filepath_resid:
            resid_filepath = os.path.join(recdir, rec.filepath_resid)
        else:
            resid_filepath = None
        if self.pymolexec is not None:
            row = TableRow()
        for step in self.res.steps:
            if topscored_fract is None:
                ntop = None
            elif isinstance(self, DockingReport):
                ntop = int(numpy.ceil(topscored_fract * len(step.samples)))
            elif isinstance(self, ScreeningReport):
                ntop = 1
            else:
                raise NotImplementedError
            if ntop == 0:
                continue
            lig_filepaths = []
            lig_colors = {}
            num_res = 0
            for run in step.iter_samples(status='finished'):
                if ntop is not None and run.scoring.rank > ntop:
                    continue
                lig_color = murdock.math.normalize(
                    run.scoring.total, step.scoring.min_total(),
                    step.scoring.max_total(), invert=True)
                for fp in viewvalues(run.filepaths):
                    if isinstance(self, DockingReport):
                        rel_fp = os.path.join('..', '..', fp)
                    elif isinstance(self, ScreeningReport):
                        rel_fp = os.path.join(
                            '..', '..', 'dockings', run.mainres.label, fp)
                    else:
                        raise NotImplementedError
                    lig_filepaths.append(rel_fp)
                    lig_colors[rel_fp] = lig_color
                num_res += 1
            if not lig_filepaths:
                continue
            if isinstance(self, DockingReport):
                ref_filepaths = [
                    os.path.join('..', '..', _lig.filepath_ref) for _lig in
                    self.res.ligands if _lig.filepath_ref]
            elif isinstance(self, ScreeningReport):
                ref_filepaths = set((
                    os.path.join(
                        '..', '..', 'dockings', _dres.label, _lig.filepath_ref)
                    for _dres in self.res.dress for _lig in _dres.ligands if
                    _lig.filepath_ref))
            else:
                raise NotImplementedError
            if ntop is not None:
                pictitle = '%s-pymol-topscored-step%02d' % (
                    self.res.label, step.serial)
                draw_res_sticks = True
            else:
                pictitle = '%s-pymol-docked-step%02d' % (
                    self.res.label, step.serial)
                draw_res_sticks = False
            if self.pymolscript is not None:
                pictitle += '.%s' % os.path.basename(self.pymolscript)
            pic_filepath = os.path.join(
                self.resdir, self.figdir, '%s.png' % pictitle)
            # Create receptor residue coloring.
            if ntop is None:
                topres = step.get_top_receptor_residues(
                    'scores', normalize=True)
            else:
                mr = murdock.results.MultiResidueResult('scores', rec)
                for sample in step.samples:
                    if sample.scoring.rank <= ntop:
                        srec = sample.mainres.get_mol(name=rec.name)
                        mr.add(sample.residues['scores'][srec])
                topres = mr.get_top_residues(normalize=True)
            res_colors = collections.OrderedDict(
                (murdock.misc.ResidueFormatter.from_key(_r).serial, 1 - _val)
                for _r, _val in viewitems(topres))
            # Create and write PyMOL script.
            pic = murdock.pymol.PyMOLPicture(
                scriptpath=os.path.join(self.pymoldir, '%s.pml' % pictitle))
            if not pic.write_script(
                    rec_filepath, lig_filepaths, width=width, height=height,
                    ref_filepaths=ref_filepaths,
                    residuals_filepath=resid_filepath, colors=lig_colors,
                    res_colors=res_colors, draw_res_sticks=draw_res_sticks,
                    include_script=self.pymolscript):
                continue
            # Run PyMOL.
            if self.pymolexec is not None and self._run_pymol(
                    pic, pic_filepath, overwrite=pic.changed):
                link = self.add_figure(pic_filepath, ext='.png')
                shead = 'Step %d (%s): %d results' % (
                    step.serial, step.title, num_res)
                row[None][shead] = link
        if self.pymolexec is None:
            return True
        if topscored_fract is None:
            headline = 'All results'
        else:
            headline = 'Top-scored results'
        if self.pymolscript is not None:
            headline += ' (%s)' % os.path.basename(self.pymolscript)
        if isinstance(self, DockingReport):
            legend = True
        elif isinstance(self, ScreeningReport):
            legend = False
        else:
            raise NotImplementedError
        if not self.add_table([row], headline):
            return False
        if MATPLOTLIB and legend:
            return self._add_legendbar(
                LEGEND_DOCKED, 'legend-docked', height=32, width=362)
        return True

    def _add_averages_table(self):
        rows = []
        for step in self.res.steps:
            row = TableRow()
            row['Step']['ID'] = '%d' % step.serial
            row['Step']['Title'] = step.title
            mean = step.scoring.mean_total()
            std = step.scoring.std_total()
            row['Score']['Total'] = '%.3f +/- %.3f' % (mean, std)
            for termname in step.scoring.termnames:
                mean = step.scoring.mean_term(termname)
                std = step.scoring.std_term(termname)
                row['Score'][termname] = '%.3f +/- %.3f' % (mean, std)
            for measure, quality in viewitems(step.qualities):
                for mtype in ('receptor', 'ligand'):
                    vals = [
                        _val for _mol, _vals in viewitems(quality) if
                        _mol.mtype == mtype for _val in _vals]
                    if not vals:
                        continue
                    mean = numpy.mean(vals)
                    std = numpy.std(vals)
                    shead = '%ss' % mtype.capitalize()
                    row[measure][shead] = '%.1f +/- %.1f' % (mean, std)
            rows.append(row)
        return self.add_table(rows, 'Averages', ttype='slim')

    def _add_rate_plots(
            self, width=DEFAULT_PLOTSIZE, height=DEFAULT_PLOTSIZE):
        """Add RMSD prediction rate tables."""
        criteria = (('RMSD', 6.0), ('RMSATD', 6.0))
        row = TableRow()
        for measure, ulim in criteria:
            head = '%s < %.2f A' % (measure, ulim)
            for step in self.res.steps:
                try:
                    sqs = step.qualities[measure]
                except KeyError:
                    continue
                rates = collections.OrderedDict()
                errors = collections.OrderedDict()
                rates['all'], errs = sqs.get_rates(ulim, err=True)
                if not rates['all']:
                    continue
                lerr = lambda _r, _s: max(0., _r - 0.5 * _s)
                uerr = lambda _r, _s: min(1., _r + 0.5 * _s)
                errors['all'] = (
                    [lerr(_r, _err) for _r, _err in zip(rates['all'], errs)],
                    [uerr(_r, _err) for _r, _err in zip(rates['all'], errs)])
                rates['top-scored'], errs = sqs.get_rates(
                    ulim, top_scored=True, err=True)
                errors['top-scored'] = (
                    [lerr(_r, _err) for _r, _err in
                    zip(rates['top-scored'], errs)],
                    [uerr(_r, _err) for _r, _err in
                    zip(rates['top-scored'], errs)])
                rates['best'], errs = sqs.get_rates(
                    ulim, top_ranked=True, err=True)
                errors['best'] = (
                    [lerr(_r, _err) for _r, _err in zip(rates['best'], errs)],
                    [uerr(_r, _err) for _r, _err in zip(rates['best'], errs)])
                plot = murdock.plot.PredictionRatePlot(height, width)
                if not plot.create(rates, errors):
                    plot.close()
                    continue
                figlabel = '%s-prates-%s%02d-step%02d' % (
                    self.res.label, measure.lower(), ulim, step.serial)
                link = self.add_plot(plot, self.resdir, figlabel)
                row[head][step.title] = link
        if not row:
            return False
        return self.add_table([row], 'Prediction Rates')

    def _add_quality_plots(
            self, height=DEFAULT_PLOTSIZE, width=DEFAULT_PLOTSIZE,
            overwrite=True):
        row = TableRow()
        for measure in ('RMSD', 'RMSATD'):
            qualities = [
                _s.qualities[measure] for _s in self.res.steps if measure in
                _s.qualities]
            if not qualities:
                continue
            data = collections.OrderedDict()
            data['all'] = collections.OrderedDict(
                (_sqs.step.title, [
                    _val for _q in _sqs.qualities for _val in viewvalues(_q)]
                ) for _sqs in qualities)
            data['top-scored'] = collections.OrderedDict(
                (_sqs.step.title, [
                    _val for _q in _sqs.qualities if _q.step.scoring.rank == 1
                    for _val in viewvalues(_q)]
                ) for _sqs in qualities)
            data['best'] = collections.OrderedDict(
                (_sqs.step.title, [
                    _val for _q in _sqs.qualities if _q.rank == 1 for _val in
                    viewvalues(_q)]
                ) for _sqs in qualities)
            plot = murdock.plot.ViolinPlot(height, width, lim=(1, 40))
            if not plot.create(data):
                plot.close()
                continue
            figlabel = '%s-%s' % (self.res.label, measure.lower())
            link = self.add_plot(
                plot, self.resdir, figlabel, overwrite=overwrite)
            row[None][measure] = link
        thead = '%s distributions (averages)' % '/'.join(row[None])
        return self.add_table([row], thead)

    def _add_scoring_plots(
            self, overwrite=True, height=DEFAULT_PLOTSIZE,
            width=DEFAULT_PLOTSIZE):
        row = TableRow()
        for step in self.res.steps:
            scores = collections.OrderedDict()
            scores['docked'] = collections.OrderedDict()
            scores['docked']['total'] = step.scoring.total
            for tname, tvals in viewitems(step.scoring.terms):
                scores['docked'][tname] = tvals
            if step.reference:
                scores['reference'] = collections.OrderedDict()
                scores['reference']['total'] = step.reference.scoring.total
                for tname, tdat in viewitems(step.reference.scoring.terms):
                    scores['reference'][tname] = tdat
            plot = murdock.plot.ViolinPlot(height, width)
            if not plot.create(scores):
                plot.close()
                continue
            figlabel = '%s-score-step%02d' % (self.res.label, step.serial)
            link = self.add_plot(
                plot, self.resdir, figlabel, overwrite=overwrite)
            shead = 'Step %d (%s)' % (step.serial, step.title)
            row[None][shead] = link
        return self.add_table([row], 'Docked score distributions')

    def _add_legendbar(self, data, figlabel, height, width):
        plot = murdock.plot.LegendBar(height, width)
        if not plot.create(data):
            plot.close()
            return False
        link = self.add_plot(plot, self.resdir, figlabel, overwrite=False)
        self.add_paragraph(link)
        return True

    def _add_rotbond_plots(
            self, height=DEFAULT_PLOTSIZE, width=DEFAULT_PLOTSIZE,
            overwrite=True, legend=True):
        norm = 180 / scipy.constants.pi
        row = TableRow()
        for step in self.res.steps:
            if not step.rotbonds:
                continue
            head = 'Step %d (%s)' % (step.serial, step.title)
            steprbs = collections.OrderedDict(
                (_mol, step.rotbonds.get_bond_dict(_mol, norm=norm)) for
                _mol in step.rotbonds)
            refrbs = None if not step.reference else collections.OrderedDict(
                (_mol, step.rotbonds.get_bond_dict(_mol, norm=norm)) for
                _mol in step.reference.rotbonds)
            for mol, moldat in viewitems(steprbs):
                data = collections.OrderedDict()
                data['docked'] = moldat
                if refrbs is not None:
                    data['reference'] = refrbs[mol]
                plot = murdock.plot.ViolinPlot(
                    height, width, horizontal=True)
                if not plot.create(data, rescale=True):
                    plot.close()
                    continue
                figlabel = '%s-rotbonds-step%02d-%s' % (
                    self.res.label, step.serial, mol.label)
                link = self.add_plot(plot, self.resdir, figlabel)
                row[head][mol.name] = link
        return self.add_table([row], 'Rotatable Bonds')

    def _add_timetable(self):
        timing = self.res.timing
        rows = collections.OrderedDict((
            ('process', TableRow()), ('wall', TableRow())))
        rows['process']['Total']['Type'] = 'Processes'
        rows['wall']['Total']['Type'] = 'Wall'
        td = self.res.timing.elapsed
        if not td:
            return False
        for ttype in rows:
            rows[ttype]['Total']['Elapsed'] = td.formatted(ttype)
        extra_tds = self.res.timing_extra()
        for ttype in rows:
            for exlabel, extd in viewitems(extra_tds):
                rows[ttype]['Total'][exlabel] = extd.formatted(ttype)
        for ttype, fmt_time in viewitems(self.res.timing_fmt_mean(std=True)):
            rows[ttype]['Averages']['Run'] = fmt_time
        for step in self.res.steps:
            for ttype, fmt_time in viewitems(step.timing_fmt_mean(std=True)):
                rows[ttype]['Averages'][step.title] = fmt_time
        if self.res.status != 'finished':
            estimate_td = self.res.timing_fmt_estimate(self.num_runs, std=True)
            for shead, tdict in viewitems(estimate_td):
                for ttype, fmt_time in viewitems(tdict):
                    rows[ttype]['Estimate'][shead] = fmt_time
        self.add_table(listvalues(rows), 'Running Time')
        return True

    def _add_residue_plots(
            self, measure, width=DEFAULT_PLOTSIZE, height=DEFAULT_PLOTSIZE,
            nres=10, ylim=None):
        rec, relpath = self.get_receptor_directory()
        if rec is None:
            return False
        row = TableRow()
        for step in self.res.steps:
            ress = step.residues[measure][rec]
            if not ress:
                continue
            ress = collections.OrderedDict(listitems(ress)[:nres])
            if isinstance(self, DockingReport):
                try:
                    refs = step.reference.residues[measure][rec]
                except AttributeError:
                    refs = None
                else:
                    refs = collections.OrderedDict(
                        (_name, refs[_name]) for _name in ress if _name in
                        refs)
            elif isinstance(self, ScreeningReport):
                refs = None
            else:
                raise NotImplementedError
            width = DEFAULT_PLOTSIZE * nres / 10.
            plot = murdock.plot.ResiduePlot(
                width, height, nres=nres, ylabel=measure)
            if not plot.create(ress, refdata=refs, ylim=ylim):
                plot.close()
                continue
            figlabel = '%s-res%s-%s-step%02d' % (
                self.res.label, measure, rec.label, step.ind)
            link = self.add_plot(plot, self.resdir, figlabel)
            shead = 'Step %d (%s)' % (step.serial, step.title)
            row[None][shead] = link
        self.add_table([row], 'Receptor residue %s' % measure)
        return True

    def _results_available(self):
        if not self.res:
            return False
        for run in self.res.iter_runs():
            try:
                if run.steps[0].filepaths:
                    return True
            except IndexError:
                continue
        return False

    def _run_pymol(self, pic, filepath, overwrite=True):
        timing = murdock.results.Timing(add_subprocs=True)
        if pic.run_script(
                self.pymolexec, filepath, overwrite=overwrite,
                num_threads=self.num_threads):
            if pic.changed:
                log.debug(
                    'PyMOL picture `%s` created.',
                    murdock.misc.fmtpath(filepath))
            success = True
        else:
            success = False
        timing.end.set_current()
        if 'PyMOL' not in self.res.timing.extra:
            self.res.timing.extra['PyMOL'] = timing.total
        else:
            self.res.timing.extra['PyMOL'] += timing.total
        return success


class DockingReport(RunnerReport):

    def __init__(
            self, backends, resdir, result, headline=None, pymolexec=None,
            pymolscript=None, num_threads=None, num_runs=None,
            draw_resscore_charts=False, draw_resdist_charts=False,
            search_filepath=None):
        super(DockingReport, self).__init__(
            backends, resdir, result, headline=headline, pymolexec=pymolexec,
            pymolscript=pymolscript, num_threads=num_threads,
            num_runs=num_runs)
        #: whether to plot residue score/distance charts for every run
        self.draw_res_charts = {
            'scores': draw_resscore_charts, 'distances': draw_resdist_charts}
        #: filepath of score-over-iteration data
        self.search_filepath = search_filepath

    def create(self, full=True):
        self._add_header(full=full)
        if not full:
            return True
        self._add_info()
        self._add_unbonded_score_table()
        if self.res.references:
            self.add_headline(1, 'Reference')
            self._add_reference_table()
        if not self._results_available():
            return True
        self.add_headline(1, 'Results')
        self._add_docked_pictures()
        self._add_docked_pictures(topscored_fract=0.1)
        self._add_result_table()
        self._add_averages_table()
        self._add_cluster_table()
        if MATPLOTLIB:
            self._add_scoring_plots()
            self._add_residue_plots(measure='scores', ylim=(None, 0.))
            self._add_residue_plots(measure='distances', ylim=(0., 20.))
            self._add_rotbond_plots()
            self._add_quality_plots()
            self._add_rate_plots()
            self._add_search_plots()
        return True

    def get_receptor_directory(self):
        try:
            return self.res.receptor, os.path.join('..', '..')
        except AttributeError:
            return None, None

    def _add_cluster_table(
            self, width=DEFAULT_PICSIZE, height=DEFAULT_PICSIZE):
        if not self.res.clustering:
            return False
        cmeasure = self.res.clustering.method['measure']
        rowdict = collections.OrderedDict()
        rownames = (
            'Sketch', 'Members', 'Mean score', 'RMSD', 'RMSATD', 'Run IDs',
            'Residue scores')
        for rowname in rownames:
            rowdict[rowname] = TableRow()
            rowdict[rowname]['Clustering']['Result'] = rowname
        rec, reldir = self.get_receptor_directory()
        rec_filepath = os.path.join(reldir, rec.filepath)
        if rec.filepath_resid is not None:
            resid_filepath = os.path.join(reldir, rec.filepath_resid)
        else:
            resid_filepath = None
        ref_filepaths = [
            os.path.join('..', '..', _lig.filepath_ref) for _lig in
            self.res.ligands if _lig.filepath_ref is not None]
        if not ref_filepaths:
            ref_filepaths = None
        for step in self.res.clustering:
            if not step.clusters:
                continue
            head = 'Step %d (%s <= %.1f A)' % (
                step.serial, cmeasure, step.parameters['max_distance'])
            for cl in step.clusters:
                shead = 'Cluster %d' % cl.serial
                rowdict['Members'][head][shead] = '%d' % len(cl.samples)
                rowdict['Mean score'][head][shead] = '%.2f +/- %.2f' % (
                    cl.scoring.mean_total(), cl.scoring.std_total())
                for qmeasure in ('RMSD', 'RMSATD'):
                    try:
                        quality = cl.qualities[qmeasure]
                    except KeyError:
                        continue
                    rowdict[qmeasure][head][shead] = '%.1f +/- %.1f' % (
                        quality.mean, quality.std)
                rowdict['Run IDs'][head][shead] = ', '.join(
                    ('%d' % _sample.run.serial for _sample in cl.samples))
                top_res_scores = cl.get_top_receptor_residues('scores')
                if top_res_scores:
                    rowdict['Residue scores'][head][shead] = ', '.join(
                        '%s (%.3f)' % (_r, _val) for _r, _val in
                        viewitems(top_res_scores))
                # Setup PyMOL picture.
                lig_filepaths = []
                lig_colors = {}
                for run in cl.samples:
                    lig_color = murdock.math.normalize(
                        run.scoring.total, cl.scoring.min_total(),
                        cl.scoring.max_total(), invert=True)
                    for fp in viewvalues(run.filepaths):
                        rel_fp = os.path.join('..', '..', fp)
                        lig_filepaths.append(rel_fp)
                        lig_colors[rel_fp] = lig_color
                if not lig_filepaths:
                    continue
                ref_filepaths = [
                    os.path.join('..', '..', _lig.filepath_ref) for _lig in
                    self.res.ligands if _lig.filepath_ref]
                topres = cl.get_top_receptor_residues('scores', normalize=True)
                res_colors = collections.OrderedDict(
                    (
                        murdock.misc.ResidueFormatter.from_key(_r).serial,
                        1 - _val)
                    for _r, _val in viewitems(topres))
                draw_res_sticks = True
                pictitle = '%s-cluster-step%02d-%d' % (
                    self.res.label, step.serial, cl.serial)
                if self.pymolscript is not None:
                    pictitle += '.%s' % os.path.basename(self.pymolscript)
                pic_filepath = os.path.join(
                    self.resdir, self.figdir, '%s.png' % pictitle)
                # Create and write PyMOL script.
                pic = murdock.pymol.PyMOLPicture(
                    scriptpath=os.path.join(
                        self.pymoldir, '%s.pml' % pictitle))
                if not pic.write_script(
                        rec_filepath, lig_filepaths, width=width,
                        height=height, ref_filepaths=ref_filepaths,
                        residuals_filepath=resid_filepath, colors=lig_colors,
                        res_colors=res_colors, draw_res_sticks=draw_res_sticks,
                        include_script=self.pymolscript):
                    continue
                if pic.changed:
                    # Remove old picture scripts and log files.
                    rm_cl_id = cl.serial
                    while True:
                        rm_cl_id += 1
                        basename = os.path.join(
                            self.pymoldir, '%s-cluster-step%02d-%d' % (
                                self.res.label, step.serial, rm_cl_id))
                        scriptpath = '%s.pml' % basename
                        logpath = '%s.log' % basename
                        if not os.path.exists(scriptpath):
                            break
                        for filepath in (scriptpath, logpath):
                            if os.path.exists(filepath):
                                try:
                                    os.remove(filepath)
                                except OSError:
                                    fmt_exc = traceback.format_exc()
                                    log.error(
                                        'File `%s` can not be removed: %s.',
                                        murdock.misc.fmtpath(filepath),
                                        fmt_exc.splitlines()[-1])
                # Add PyMOL pictures to table.
                if self.pymolexec is not None and self._run_pymol(
                        pic, pic_filepath, overwrite=pic.changed):
                    link = self.add_figure(pic_filepath, ext='.png')
                    rowdict['Sketch'][head][shead] = link
        rows = [_row for _row in viewvalues(rowdict) if len(_row) > 1]
        algorithm = self.res.clustering.method['algorithm']
        headline = 'Clustering (%s-based %s)' % (cmeasure, algorithm)
        if self.pymolscript is not None:
            headline += ' (%s)' % os.path.basename(self.pymolscript)
        return self.add_table(rows, headline)

    def _add_info(self):
        if not self.res.receptor:
            return False
        self._add_info_pictures()
        rows = []
        for mol in self.res.iter_mols():
            row = TableRow()
            row[None]['Name'] = mol.name
            if mol.description:
                row[None]['Description'] = mol.description
            else:
                row[None]['Description'] = ''
            if mol.resolution:
                row[None]['Resolution'] = '%.1f' % mol.resolution
            else:
                row[None]['Resolution'] = ''
            if mol.notes:
                row[None]['Notes'] = str(mol.notes)
            else:
                row[None]['Notes'] = ''
            if len(row) > 1:
                rows.append(row)
        return self.add_table(rows, 'Input Data')

    def _add_info_pictures(
            self, width=DEFAULT_PICSIZE, height=DEFAULT_PICSIZE):
        if self.pymolexec is not None:
            row = TableRow()
        rec, recdir = self.get_receptor_directory()
        ligs = self.res.ligands
        if rec.filepath_ref:
            rec_filepath = os.path.join(recdir, rec.filepath_ref)
        else:
            rec_filepath = os.path.join(recdir, rec.filepath)
        if rec.filepath_resid:
            resid_filepath = os.path.join(recdir, rec.filepath_resid)
        else:
            resid_filepath = None
        cols = []
        try:
            ref = self.res.references[0]
        except (KeyError, IndexError):
            # Set picture parameters for receptor.
            cols.append({
                'head': 'Receptor', 'shead': rec.name,
                'label': '%s-sketch-%s' % (self.res.label, rec.label),
                'rec_filepath': rec_filepath,
                'residuals_filepath': resid_filepath, 'ref_filepaths': [],
                'ref_color': None, 'res_colors': None,
                'draw_res_sticks': False})
        else:
            # Set picture parameters for reference complex.
            shead = ' + '.join([rec.name] + [
                _lig.name for _lig in ligs if _lig.filepath_ref])
            lig_filepaths = [
                os.path.join('..', '..', _lig.filepath_ref) for _lig in ligs if
                _lig.filepath_ref]
            topres = ref.get_top_receptor_residues('distances', normalize=True)
            res_colors = collections.OrderedDict(
                [(murdock.misc.ResidueFormatter.from_key(_r).serial, 1 - _val)
                for _r, _val in viewitems(topres)])
            col = {
                'head': 'Reference complex', 'shead': shead,
                'label': '%s-sketch-refs' % self.res.label,
                'rec_filepath': rec_filepath, 'ref_filepaths': lig_filepaths,
                'ref_color': 'green', 'residuals_filepath': resid_filepath,
                'res_colors': res_colors, 'draw_res_sticks': True}
            cols.append(col)
        # Set picture parameters for ligands.
        for lig in ligs:
            lig_filepath = os.path.join('..', '..', lig.filepath)
            cols.append({
                'head': 'Ligands', 'shead': lig.name,
                'label': '%s-sketch-%s' % (self.res.label, lig.label),
                'rec_filepath': None, 'residuals_filepath': None,
                'ref_filepaths': [lig_filepath],
                'ref_color': None,
                'res_colors': None, 'draw_res_sticks': False})
        # Create, write and (optionally) run picture script.
        for col in cols:
            rec_filepath = col['rec_filepath']
            ref_filepaths = col['ref_filepaths']
            res_filepath = col['residuals_filepath']
            pic_filepath = os.path.join(
                self.resdir, self.figdir, '%s.png' % col['label'])
            res_colors = col['res_colors']
            draw_res_sticks = col['draw_res_sticks']
            pic = murdock.pymol.PyMOLPicture(
                scriptpath=os.path.join(
                    self.pymoldir, '%s.pml' % col['label']))
            if not pic.write_script(
                    rec_filepath, lig_filepaths=None, width=width,
                    height=height, ref_filepaths=ref_filepaths,
                    ref_color=col['ref_color'],
                    residuals_filepath=res_filepath, res_colors=res_colors,
                    draw_res_sticks=draw_res_sticks):
                continue
            if self.pymolexec is not None and self._run_pymol(
                    pic, pic_filepath, overwrite=pic.changed):
                link = self.add_figure(pic_filepath, ext='.png')
                row[col['head']][col['shead']] = link
        if self.pymolexec is None:
            return True
        return self.add_table([row], 'Sketches')

    def _add_progressbar(self, height=20, width=800):
        bar = murdock.plot.ProgressBar(height, width)
        c = bar.create(self.res, self.num_runs)
        if not c:
            bar.close()
            return False
        figlabel = '%s-status' % self.res.label
        link = self.add_plot(bar, self.resdir, figlabel)
        self.add_paragraph(link)
        bar.close()
        return True

    def _add_progresstext(self):
        self.add_paragraph(self.res.status)
        return True

    def _add_reference_table(self):
        rows = []
        for step in self.res.references:
            row = TableRow()
            row['Step']['ID'] = '%d' % step.serial
            row['Step']['Title'] = step.title
            row['Score']['Total'] = '%.3f' % step.scoring.total
            for tname, tval in viewitems(step.scoring.terms):
                row['Score'][tname] = '%.3f' % tval
            if MATPLOTLIB:
                label = 'ref-step%02d' % step.serial
                charts = self._get_residue_charts(step, label, force=True)
                for key, subtable in viewitems(charts):
                    row['Residue %s' % key] = subtable
            rows.append(row)
        if not self.add_table(rows, 'Score', ttype='slim'):
            return False
        if MATPLOTLIB:
            self._add_legendbar(
                LEGEND_AA_TYPES, 'legend-residues', height=32, width=1018)
        return True

    def _add_unbonded_score_table(self):
        if not self.res.unbonded:
            return False
        rows = []
        for step in self.res.unbonded:
            row = TableRow()
            row['Step']['ID'] = '%d' % step.serial
            row['Step']['Title'] = step.title
            row['Score']['Total'] = '%.3f' % step.scoring.total
            for tname, tval in viewitems(step.scoring.terms):
                row['Score'][tname] = '%.3f' % tval
            rows.append(row)
        return self.add_table(rows, 'Unbonded score', ttype='slim')

    def _add_result_table(self):
        rows = []
        for run in self.res.runs:
            for step in run.iter_steps(status='finished'):
                row = TableRow()
                row['Stage']['Run'] = '%d' % run.serial
                row['Stage']['Step'] = '%d' % step.serial
                # Add ranks.
                rank = step.scoring.rank
                if rank == 1:
                    row['Rank']['Score'] = self.fmt_bold('%d' % rank)
                else:
                    row['Rank']['Score'] = '%d' % rank
                for measure, quality in viewitems(step.qualities):
                    rank = quality.rank
                    if rank == 1:
                        row['Rank'][measure] = self.fmt_bold('%d' % rank)
                    else:
                        row['Rank'][measure] = '%d' % rank
                # Add scores.
                if step.scoring.rank == 1:
                    total = self.fmt_bold('%.3f' % step.scoring.total)
                else:
                    total = '%.3f' % step.scoring.total
                row['Score']['Total'] = total
                for tname, tval in viewitems(step.scoring.terms):
                    row['Score'][tname] = '%.3f' % tval
                # Add quality measures (RMSD, RMSATD).
                for measure, quality in viewitems(step.qualities):
                    for mol, molval in viewitems(quality):
                        if molval is None:
                            continue
                        if quality.rank == 1:
                            row[measure][mol.name] = self.fmt_bold(
                                '%.1f' % molval)
                        else:
                            row[measure][mol.name] = '%.1f' % molval
                if self.res.references:
                    rec = self.res.receptor
                    ref_resid = step.reference.residues
                    resid = step.residues
                    head = 'Residue matches'
                    if 'distances' in resid and 'distances' in ref_resid:
                        # Add residue matches based on distances.
                        distmatches = resid['distances'][rec].match(
                            ref_resid['distances'][rec], top=True)
                        shead = 'distance'
                        row[head][shead] = '%d / %d' % distmatches
                    if 'scores' in resid and 'scores' in ref_resid:
                        # Add residue matches based on scores.
                        scorematches = resid['scores'][rec].match(
                            ref_resid['scores'][rec], top=True)
                        shead = 'score'
                        row[head][shead] = '%d / %d' % scorematches
                # Add residue score and distance charts.
                if MATPLOTLIB and True in viewvalues(self.draw_res_charts):
                    label = 'run%05d' % run.serial
                    charts = self._get_residue_charts(step, label)
                    for key, subtable in viewitems(charts):
                        row['Residue %s' % key] = subtable
                rows.append(row)
        if not self.add_table(rows, 'Overview', ttype='large'):
            return False
        if MATPLOTLIB and True in viewvalues(self.draw_res_charts):
            self._add_legendbar(
                LEGEND_DOCKED, 'legend-docked', height=32, width=362)
        return True

    def _add_search_plots(
            self, width=DEFAULT_PLOTSIZE, height=DEFAULT_PLOTSIZE):
        if not self.search_filepath:
            return False
        try:
            data = murdock.misc.load_ordered_json(self.search_filepath)
        except (IOError, ValueError, TypeError) as exc:
            log.warning(
                'Can not read data from file `%s`: %s',
                murdock.misc.fmtpath(self.search_filepath), str(exc))
            return False
        rows = collections.OrderedDict()
        for step in self.res.steps:
            for run in data['runs']:
                try:
                    iterations = run[step.title]['iterations']
                except KeyError:
                    continue
                try:
                    interval = iterations[1] - iterations[0]
                except IndexError:
                    continue
                break
            else:
                interval = 1
            scores = collections.OrderedDict()
            refs = collections.OrderedDict()
            scores['total'] = [
                _run[step.title]['total'] for _run in data['runs'] if
                step.title in _run]
            try:
                refs['total'] = step.reference.scoring.total
            except AttributeError:
                pass
            for tname in step.scoring.termnames:
                scores[tname] = [
                    _run[step.title]['terms']['weighted'][tname] for _run in
                    data['runs'] if step.title in _run]
                try:
                    refs[tname] = step.reference.scoring.terms[tname]
                except AttributeError:
                    pass
            rgb_red, rgb_blue = (1., 0., 0.), (0., 0., 1.)
            finaltots = [_vals[-1] for _vals in scores['total'] if _vals]
            if not finaltots:
                continue
            colors = murdock.misc.list_to_rgb(finaltots, rgb_red, rgb_blue)
            for tname, tvals in viewitems(scores):
                try:
                    row = rows[tname]
                except KeyError:
                    rows[tname] = row = TableRow()
                    row[None]['Term'] = tname
                refval = refs[tname] if tname in refs else None
                plot = murdock.plot.SearchPlot(
                    height, width, ylabel='`%s` score' % tname)
                if not plot.create(
                        interval, tvals, colors=colors, refval=refval):
                    plot.close()
                    continue
                figlabel = '%s-search-%s-step%02d' % (
                    self.res.label, murdock.misc.cleanup_filename(tname),
                    step.serial)
                link = self.add_plot(plot, self.resdir, figlabel)
                shead = 'Step %d (%s)' % (step.serial, step.title)
                row[None][shead] = link
        self.add_table(listvalues(rows), 'Convergence of Scores')
        return True

    def _get_residue_charts(self, step, label, force=False, width=1000):
        subtable = TableRow()
        if not step.residues:
            return subtable
        plot_classes = {
            'distances': murdock.plot.ResidueDistanceChart,
            'scores': murdock.plot.ResidueScoreChart}
        for measure, plot_class in viewitems(plot_classes):
            if not force and not self.draw_res_charts[measure]:
                continue
            try:
                contr = step.residues[measure]
            except KeyError:
                continue
            for mol, moldata in viewitems(contr):
                plot = plot_class(width)
                if not plot.create(moldata):
                    plot.close()
                    continue
                figlabel = '%s-%s-step%02d-%s-res%s' % (
                    self.res.label, label, step.serial, mol.label, measure)
                link = self.add_plot(
                    plot, self.resdir, figlabel, overwrite=False, scale=0.1)
                subtable[measure][mol.name] = link
        return subtable


class ScreeningReport(RunnerReport):

    def create(self, full=True):
        self._add_header(full=full)
        if not full or not self._results_available():
            return True
        self.add_headline(1, 'Results')
        self._add_docked_pictures()
        self._add_docked_pictures(topscored_fract=0.1)
        self._add_averages_table()
        if MATPLOTLIB:
            self._add_scoring_plots()
            self._add_residue_plots(measure='scores', ylim=(None, 0.))
            self._add_residue_plots(measure='distances', ylim=(0., 20.))
            self._add_quality_plots()
            self._add_quality_dockwise_plots()
            self._add_rotbond_plots(legend=False)
            self._add_rate_plots()
        return True

    def get_receptor_directory(self):
        if self.res.receptor:
            for dres in self.res.dress:
                if dres.receptor is not None:
                    return dres.receptor, os.path.join(
                        '..', '..', 'dockings', dres.label)
        return None, None

    def _add_progresstext(self):
        stats = {}
        for dres in self.res.dress:
            s = dres.status
            if s not in stats:
                stats[s] = []
            stats[s].append(dres.title)
        if stats:
            self.add_bullet_list(
                collections.OrderedDict(sorted(listitems(stats))))
        else:
            self.add_paragraph(self.res.status)
        return True

    def _add_quality_dockwise_plots(
            self, overwrite=True, height=DEFAULT_PLOTSIZE,
            width=DEFAULT_PLOTSIZE):
        row = TableRow()
        for measure in ('RMSD', 'RMSATD'):
            for step in self.res.steps:
                if measure not in step.qualities:
                    continue
                data = collections.OrderedDict((
                    ('all', collections.OrderedDict()),
                    ('top-scored', collections.OrderedDict()),
                    ('best', collections.OrderedDict())))
                for quality in step.qualities[measure].qualities:
                    dres = quality.step.mainres
                    if dres.title not in data['all']:
                        data['all'][dres.title] = []
                    data['all'][dres.title].extend(listvalues(quality))
                    if quality.step.scoring.rank == 1:
                        data['top-scored'][dres.title] = listvalues(quality)
                    if quality.rank == 1:
                        data['best'][dres.title] = listvalues(quality)
                dlabels = [_item[0] for _item in sorted(
                    data['best'].items(), key=lambda _x: min(_x[1]),
                    reverse=True)]
                data = collections.OrderedDict(
                    (_key, collections.OrderedDict(
                        (_dlabel, data[_key][_dlabel]) for _dlabel in dlabels))
                    for _key in data)
                plot = murdock.plot.ViolinPlot(
                    height, width, lim=(1, 40), xlabel=measure,
                    horizontal=True)
                if not plot.create(data, rescale=True):
                    plot.close()
                    continue
                figlabel = '%s-%s-step%02d' % (
                    self.res.label, measure.lower(), step.serial)
                link = self.add_plot(
                    plot, self.resdir, figlabel, overwrite=overwrite)
                shead = 'Step %d (%s)' % (step.serial, step.title)
                row[measure][shead] = link
        thead = '%s distributions (dockings)' % '/'.join(row)
        self.add_table([row], thead)
        return True

    def _add_progressbar(self, height=20, width=400):
        added = False
        for dres in self.res.dress:
            self.add_headline(2, '%s' % dres.title)
            bar = murdock.plot.ProgressBar(height, width)
            c = bar.create(dres, self.num_runs, label=dres.status)
            if not c:
                bar.close()
                continue
            figlabel = '%s-%s-status' % (self.res.label, dres.label)
            link = self.add_plot(bar, self.resdir, figlabel)
            self.add_paragraph(link)
            bar.close()
            added = True
        return added


class TrainingReport(RunnerReport):

    def create(self, full=True):
        self._add_header(full=full)
        if not full:
            return True
        if MATPLOTLIB:
            self.add_headline(1, 'Results')
            self._add_scoring_plots()
            self._add_rating_plots()
            self._add_outlier_plots()
        return True

    def _add_progressbar(self, height=20, width=800):
        bar = murdock.plot.ProgressBar(height, width)
        c = bar.create(self.res, self.num_runs, label=self.res.status)
        if not c:
            bar.close()
            return False
        figlabel = '%s-status' % self.res.label
        link = self.add_plot(bar, self.resdir, figlabel)
        self.add_paragraph(link)
        bar.close()
        return True

    def _add_outlier_plots(
            self, height=DEFAULT_PLOTSIZE, width=DEFAULT_PLOTSIZE):
        row = TableRow()
        for step in self.res.training_steps:
            plot = murdock.plot.TrainingOutlierPlot(height, width)
            if not plot.create(step.outliers, len(self.res.dress)):
                plot.close()
                continue
            figlabel = '%s-outliers-step%02d' % (self.res.label, step.serial)
            link = self.add_plot(plot, self.resdir, figlabel)
            shead = 'Step %d (%s)' % (step.serial, step.title)
            row[None][shead] = link
        self.add_table([row], 'Outliers')
        return True

    def _add_rating_plots(
            self, height=DEFAULT_PLOTSIZE, width=DEFAULT_PLOTSIZE):
        row = TableRow()
        for step in self.res.training_steps:
            plot = murdock.plot.TrainingRatingPlot(height, width)
            if not plot.create(step.rating_means):
                plot.close()
                continue
            figlabel = '%s-rating-step%02d' % (self.res.label, step.serial)
            link = self.add_plot(plot, self.resdir, figlabel)
            shead = 'Step %d (%s)' % (step.serial, step.title)
            row[None][shead] = link
        self.add_table([row], 'Rating')
        return True

    def _add_scoring_plots(
            self, overwrite=True, height=2*DEFAULT_PLOTSIZE,
            width=2*DEFAULT_PLOTSIZE):
        row = TableRow()
        for step in self.res.training_steps:
            scores = collections.OrderedDict()
            scores['decoys'] = step.term_means
            scores['ref'] = step.ref_term_means
            plot = murdock.plot.TrainingScorePlot(height, width)
            if not plot.create(scores):
                plot.close()
                continue
            figlabel = '%s-scoring-step%02d' % (self.res.label, step.serial)
            link = self.add_plot(
                plot, self.resdir, figlabel, overwrite=overwrite)
            shead = 'Step %d (%s)' % (step.serial, step.title)
            row[None][shead] = link
        self.add_table([row], 'Scoring')
        return True


class Table(object):
    """Class representing a formatted data table.

    Each row has the form collections.OrderedDict(
        {<headline_i>:{<sheadline_j>:<value_ij>}} for i, j).

    If <headline> is `None`, no subcolumn structure will be created and the
    sheadlines serve as regular headlines; in this case no headline except
    `None` must be used in any row.

    The order in which columns are added to the table can be manually set using
    the attribute `headorder` or is chosen automatically based on the order in
    the table rows (with higher priority on rows added first).

    """

    def __init__(self, ttype=None, subs=None):
        #: list of row dictionaries
        self.rows = []
        #: table type (None, `default`, `slim` or `large`)
        self.ttype = ttype
        #: list of headlines in order in which columns are added to the table
        self.heads = None
        #: dictionary with string substitutions to be performed
        self._subs = subs
        #: table data (nested dictionary; keys are headlines and subheadlines)
        self.data = None

    def add_row(self, row):
        row.remove_empty_fields()
        if not row:
            return False
        if None in row and len(row) > 1:
            raise ReportError(
                'Row can not be added because it contains more than one '
                'headline of which one is `None`: %s' % str(row))
        if self.rows and None in row and None not in self._get_heads():
            raise ReportError(
                'Row can not be added because it contains the headline `None` '
                'while rows without that headline have already been added: %s'
                % str(row))
        if self.rows and None not in row and None in self._get_heads():
            raise ReportError(
                'Row can not be added because it does not contain the header '
                'None` while rows with that headline have already been added: '
                '%s' % str(row))
        for stable in viewvalues(row):
            for shead, field in viewitems(stable):
                stable[shead] = str(field)
        rows = row.splitlines()
        self.rows.extend(rows)
        return True

    def create(self):
        raise NotImplementedError

    def _fill_table(self):
        for head, subtable in viewitems(self.data):
            for shead, column in viewitems(subtable):
                for row in self.rows:
                    try:
                        column.append(row[head][shead])
                    except KeyError:
                        column.append('')
        return True

    def _format_data(self):
        widths, subwidths = self._get_column_widths()
        formatted = collections.OrderedDict()
        for head, subtable in viewitems(self.data):
            if head is None:
                fhead = None
            else:
                headform = '{0:<%ds}' % widths[head]
                fhead = headform.format(head)
            formatted[fhead] = collections.OrderedDict()
            for shead, column in viewitems(subtable):
                strform = '{0:<%ds}' % subwidths[head][shead]
                numform = '{0:>%ds}' % subwidths[head][shead]
                fshead = strform.format(shead)
                formatted[fhead][fshead] = [
                    numform.format(_c) if self._isnumeric(_c) else
                    strform.format(_c) for _c in column]
        self.data = formatted
        return True

    def _get_column_widths(self):
        widths = collections.OrderedDict()
        swidths = collections.OrderedDict()
        for head, subtable in viewitems(self.data):
            swidths[head] = collections.OrderedDict()
            for shead, column in viewitems(subtable):
                swidths[head][shead] = max(len(_field) for _field in column)
                swidths[head][shead] = max(swidths[head][shead], len(shead))
            widths[head] = (
                sum(viewvalues(swidths[head])) + len(swidths[head]) - 1)
            if head is not None and len(head) > widths[head]:
                add_headspace = max(0, len(head) - widths[head])
                swidths[head][list(swidths[head])[-1]] += add_headspace
                widths[head] += add_headspace
        return widths, swidths

    def _get_heads(self):
        if self.heads is not None:
            return self.heads
        return list(collections.OrderedDict.fromkeys(
            _k for _row in self.rows for _k in _row))

    def _init_table_structure(self):
        heads = self._get_heads()
        self.data = collections.OrderedDict()
        for head in heads:
            self.data[head] = collections.OrderedDict()
            for row in self.rows:
                if head not in row:
                    continue
                for shead in row[head]:
                    if shead not in self.data[head]:
                        self.data[head][shead] = []
        if len(heads) == 1 and len(listvalues(self.data)[0]) == 1:
            self.data[heads[0]][' '] = []
        return True


class TableRow(collections.OrderedDict):

    def __missing__(self, key):
        self[key] = added = collections.OrderedDict()
        return added

    def remove_empty_fields(self):
        for head, stable in viewitems(self):
            for shead, field in viewitems(stable):
                if not field:
                    del self[head][shead]
            if not stable:
                del self[head]

    def splitlines(self):
        split = collections.OrderedDict((
            _head, collections.OrderedDict(
                (_shead, _field.splitlines()) for _shead, _field in
                viewitems(_stable))) for _head, _stable in viewitems(self))
        height = max(
            len(_field) for _stable in viewvalues(split) for _field in
            viewvalues(_stable))
        return [
            TableRow(
                (
                    _head, collections.OrderedDict(
                        (_shead, _lines[_i] if len(_lines) > _i else '') for
                        _shead, _lines in viewitems(_stable))
                ) for _head, _stable in viewitems(split)) for _i in
            range(height)]


def _uuid_key():
    return str(uuid.uuid4())


def substitute_fields(data, subdict):
    new_data = collections.OrderedDict()
    for head, subtable in viewitems(data):
        fmt_head = substitute_all(head, subdict)
        new_data[fmt_head] = collections.OrderedDict()
        for shead, column in viewitems(subtable):
            fmt_col = [
                substitute_all(_field, subdict) for _field in column]
            fmt_shead = substitute_all(shead, subdict)
            new_data[fmt_head][fmt_shead] = fmt_col
    return new_data


def substitute_all(text, sdict):
    pattern = re.compile(r'|'.join([re.escape(_k) for _k in sdict]))
    try:
        return pattern.sub(lambda _x: sdict[_x.group()], text)
    except (KeyError, TypeError):
        return text
