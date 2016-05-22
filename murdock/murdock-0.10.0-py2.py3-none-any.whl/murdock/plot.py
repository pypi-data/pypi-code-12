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
Module :mod:`murdock.plot`
--------------------------

A collection of plotting classes based on :mod:`matplotlib` employed in the
:mod:`~murdock.report.report` module.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as pyplot
import matplotlib.colors
import numpy
import scipy.stats

from murdock.misc import ResidueFormatter


log = logging.getLogger('plot')

LIGHTRED = (1., .2, .2)
MARKERS = ('.', 'x', 'v', 'o', '^')
COLORS = (
    'blue', 'green', 'red', 'magenta', 'orange', 'darkblue', 'lightgreen',
    'cyan', 'magenta', 'lime', 'brown', 'wheat', 'teal', 'snow', 'rosybrown',
    'lightskyblue', 'darkblue', 'orange', 'dodgerblue', 'yellow', 'green',
    'cyan', 'magenta', 'lime', 'brown', 'wheat', 'teal', 'snow', 'rosybrown',
    'lightskyblue', 'darkblue', 'orange', 'dodgerblue', 'yellow', 'green',
    'cyan', 'magenta', 'lime', 'brown', 'wheat', 'teal', 'snow', 'rosybrown',
    'lightskyblue')
RESIDUE_COLORS = {
    'ARG': 'lightblue', 'HIS': 'lightblue', 'LYS': 'lightblue',
    'ASP': LIGHTRED, 'GLU': LIGHTRED,
    'SER': 'magenta', 'THR': 'magenta', 'ASN': 'magenta', 'GLN': 'magenta',
    'CYS': 'yellow', 'SEC': 'yellow', 'GLY': 'yellow', 'PRO': 'yellow',
    'ALA': 'green', 'ILE': 'green', 'LEU': 'green', 'MET': 'green',
    'PHE': 'green', 'TRP': 'green', 'TRY': 'green', 'VAL': 'green',
    'other': '0.85'}


class PlotError(Exception):
    pass


class Plot(object):

    def __init__(
            self, height, width, fontsize=None, legend_loc='best', xlabel=None,
            ylabel=None):
        self.height = height
        self.width = width
        self.fontsize = fontsize
        self.legend_loc = legend_loc
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.fig = None

    def close(self):
        if self.fig is not None:
            pyplot.close(self.fig)
        return True

    def save_plot(self, prefix, width=None, height=None, ext='.pdf'):
        if (
                (width is None and height is None) or
                (width is not None and height is not None)):
            raise PlotError('Either `width` OR `height` must be given')
        outdir = os.path.split(prefix)[0]
        if outdir and not os.path.exists(outdir):
            try:
                os.makedirs(outdir)
            except OSError:
                if not os.path.isdir(outdir):
                    raise PlotError(
                        'Failed to create directory `%s`.' % outdir)
        if width is not None:
            dpi = width / self.fig.get_size_inches()[0]
        else:
            dpi = height / self.fig.get_size_inches()[1]
        filepath = '%s%s' % (prefix, ext)
        try:
            self.fig.savefig(filepath, dpi=dpi)
        except (RuntimeError, TypeError) as exc:
            log.error(
                'Matplotlib failed to save picture `%s`: %s.', filepath, exc)
            return False
        return True

    def _inch_to_px(self, x):
        if self.fig is None:
            return x * 80
        return x * self.fig.get_dpi()

    def _px_to_inch(self, x):
        if self.fig is None:
            return x / 80.
        return float(x) / self.fig.get_dpi()

    def _setup(self):
        self.fig = pyplot.figure(figsize=(
            self._px_to_inch(self.width), self._px_to_inch(self.height)))
        if self.xlabel is not None:
            pyplot.xlabel(self.xlabel, fontsize=self.fontsize)
        if self.ylabel is not None:
            pyplot.ylabel(self.ylabel)
        return True


class LegendBar(Plot):

    def create(self, data, fontsize=11):
        self._setup()
        boxes = [
            pyplot.Rectangle((0, 0), 1, 1, fc=_c) for _c in data.itervalues()]
        pyplot.legend(
            boxes, data.keys(), ncol=len(data),
            bbox_to_anchor=(0., 1., 1., 0.), prop={'size': fontsize},
            fancybox=True, loc=self.legend_loc)
        pyplot.subplots_adjust(left=0., right=1., top=1., bottom=0.)
        pyplot.gca().set_axis_off()
        return True


class TrainingRatingPlot(Plot):

    def __init__(
            self, height, width, fontsize=None, xlabel='Iteration',
            ylabel='Mean rating'):
        super(TrainingRatingPlot, self).__init__(
            height, width, xlabel=xlabel, ylabel=ylabel)

    def create(self, data):
        if not data:
            return False
        xdat = range(1, len(data) + 1)
        self._setup()
        pyplot.plot(xdat, data, 'o-', ms=10)
        pyplot.xlim((.5, xdat[-1] + .5))
        pyplot.ylim((0, 1))
        pyplot.xticks(xdat)
        pyplot.tight_layout()
        return True


class TrainingScorePlot(Plot):

    def __init__(
            self, height, width, fontsize=None, legend_loc=2,
            xlabel='Iteration', ylabel='Mean term score'):
        super(TrainingScorePlot, self).__init__(
            height, width, legend_loc=legend_loc, xlabel=xlabel, ylabel=ylabel)
        self.styles = ('o-', 's--')

    def create(self, data):
        self._setup()
        xulim = None
        for (setlabel, setdata), style in zip(data.iteritems(), self.styles):
            for (tname, ydat), color in zip(setdata.iteritems(), COLORS):
                label = '%s (%s)' % (tname, setlabel)
                l = len(ydat)
                xdat = range(1, l + 1)
                pyplot.plot(
                    xdat, ydat, style, label=label, color=color, ms=10)
                if xulim is None or l > xulim:
                    xulim = l
        if xulim is None:
            return False
        pyplot.legend(prop={'size': 10}, loc=self.legend_loc)
        pyplot.grid(b=True, which='major', axis='x', linestyle='-', alpha=0.2)
        pyplot.xticks(range(1, xulim + 1))
        pyplot.xlim((.5, xulim + .5))
        pyplot.tight_layout()
        return True


class TrainingOutlierPlot(Plot):

    def __init__(
            self, height, width, fontsize=None, xlabel='Iteration',
            ylabel='Outlier fraction'):
        super(TrainingOutlierPlot, self).__init__(
            height, width, xlabel=xlabel, ylabel=ylabel)

    def create(self, data, num):
        if not data:
            return False
        xdat = range(1, len(data) + 1)
        ydat = [float(len(_ols)) / num for _ols in data]
        self._setup()
        pyplot.plot(xdat, ydat, 'o-', ms=10)
        for i, ols in enumerate(data):
            for i_ol, ol in enumerate(ols[::-1]):
                textvpos = 0.03 + 0.06 * i_ol
                y = float(len(ols)) / num + textvpos
                text = ol if len(ol) < 7 else '%s.' % ol[:5]
                pyplot.text(i + 1, y, text, fontsize=10, family='monospace')
        pyplot.xlim((.5, xdat[-1] + .5))
        pyplot.ylim((0, 1))
        pyplot.xticks(xdat)
        pyplot.tight_layout()
        return True


class Histogram(Plot):

    def _fix_min_xlim(self, bins):
        dx = 0.05 * (bins[-1] - bins[0])
        pyplot.xlim((bins[0] - dx, bins[-1] + dx))
        return True

    def _mark_bin(self, val, bins, patches, color=None, hatch='//'):
        try:
            w = patches[0].get_width()
        except TypeError:
            return False
        ax = pyplot.gca()
        ax.relim()
        ylim = pyplot.gca().get_ylim()[1]
        h = ylim
        y = 0
        x = val - 0.5 * w
        for i in xrange(len(bins) - 1):
            if bins[i] <= val <= bins[i+1]:
                x = patches[i].get_x()
                y = patches[i].get_height() + patches[i].get_y()
                h -= patches[i].get_height()
                break
        # Increase ylim by 0.25 if the highest bar is marked.
        if h == 0:
            h = 0.25
            ax.set_ylim((0, ylim + 0.25))
        mark = matplotlib.patches.Rectangle(
            (x, y), width=w, height=h, hatch=hatch, color=color, fill=False,
            linestyle='dashed')
        ax.add_patch(mark)
        return True

    def _set_yticks(self, nbins):
        try:
            maxval = int(max(max(_n) for _n in nbins))
        except TypeError:
            maxval = int(max(nbins))
        pyplot.gca().set_yticks(range(0, maxval + 1, maxval / 10 + 1))
        return True


class BoxPlot(Plot):
    """Box plot class for one major and opt. one or two minor data sets.
    """

    def __init__(
            self, height, width, fontsize=None, horizontal=False,
            lim=(None, None), legend_loc='best', xlabel=None, ylabel=None):
        super(BoxPlot, self).__init__(
            height, width, fontsize=fontsize, legend_loc=legend_loc,
            xlabel=xlabel, ylabel=ylabel)
        self.horizontal = horizontal
        self.lim = lim
        self.labels = None
        self.ticklabels = None
        self.colors = COLORS[:3]

    def create(self, data, fmt_ticklabels=None, rescale=False):
        """Create violin plot.

        The ``data`` has the form::

            data = {<setlabel>: {<xticklabel>: <boxdata>}}

        If order is important (which it usually is), ``data`` should be an
        `collections.OrderedDict()` instance and have `OrderedDict()` items.
        The <boxdata> are lists of numeric values (if a box is not a list but
        single value it will be transformed into a tuple). The dictionary
        ``data`` may contain up to three items: one primary and two secondary
        data sets.  The first set is plotted as large central bars above each
        x-ticklabel, the second set as slim bars left and the third set as slim
        bars right of each central bar.

        The dictionary ``fmt_ticklabels`` maps the <xticklabel> key to a
        formatted string (may include TeX code).

        """
        if rescale:
            scale1 = 0.1 + 0.3 * max(
                len(_setdat.keys()) for _setdat in data.itervalues())
            scale2 = 1 + 0.05 * max(
                len(_xtl) for _setdat in data.itervalues() for _xtl in
                _setdat.iterkeys())
            if self.horizontal:
                self.height *= scale1
                self.width *= scale2
            else:
                self.height *= scale2
                self.width *= scale1
        for dataset in data.itervalues():
            for xlabel, box in dataset.iteritems():
                try:
                    iter(box)
                except TypeError:
                    dataset[xlabel] = (box, )
        self.labels = data.keys()
        datsets = data.values()
        if fmt_ticklabels is None:
            self.ticklabels = datsets[0].keys()
        else:
            self.ticklabels = [
                fmt_ticklabels[_k] for _k in datsets[0].iterkeys()]
        allvals = [
            _val for _ds in datsets for _box in _ds.itervalues() for _val in
            _box]
        if not allvals:
            return False
        minval = min(allvals)
        maxval = max(allvals)
        valrange = maxval - minval
        if self.lim[0] is None:
            llim = minval - 0.05 * valrange
        else:
            llim = self.lim[0]
        if self.lim[1] is None:
            ulim = maxval + 0.05 * valrange
        else:
            ulim = self.lim[1]
        self._setup()
        for i in xrange(len(self.ticklabels)):
            if i % 2:
                fc = 'gray'
            else:
                fc = 'lightgray'
            if self.horizontal:
                x, w, h = (llim, i + .5), ulim - llim, 1
            else:
                x, w, h = (i + .5, llim), 1, ulim - llim
            pyplot.gca().add_patch(matplotlib.patches.Rectangle(
                x, w, h, facecolor=fc, alpha=.2,
                edgecolor='white'))
        vals1 = datsets[0].values()
        if len(data) == 1:
            if not self._create_single_plot(vals1):
                return False
        else:
            vals2a = [datsets[1][_xtl] for _xtl in datsets[0].iterkeys()]
        if len(data) == 2:
            if not self._create_double_plot(vals1, vals2a):
                return False
        elif len(data) == 3:
            vals2b = [datsets[2][_xtl] for _xtl in datsets[0].iterkeys()]
            if not self._create_triple_plot(vals1, vals2a, vals2b):
                return False
        elif len(data) > 3:
            raise PlotError(
                'ViolinPlot can plot up to 3 data sets (%d given).' %
                len(data))
        if self.horizontal:
            tickfunc = pyplot.yticks
            limfunc = pyplot.ylim
            rot = 0.
            set_lim_within_bounds('x', (llim, ulim), add_margins=False)
        else:
            tickfunc = pyplot.xticks
            limfunc = pyplot.xlim
            rot = 45.
            set_lim_within_bounds('y', (llim, ulim), add_margins=False)
        tickfunc(
            range(1, len(self.ticklabels) + 1), self.ticklabels,
            rotation=rot, fontsize=self.fontsize)
        limfunc((.5, len(self.ticklabels) + .5))
        pyplot.tight_layout()
        return True

    def _add(self, positions, data, width, color=None):
        vert = not self.horizontal
        for dset, pos in zip(data, positions):
            if len(dset) != 1:
                continue
            if self.horizontal:
                x, y = dset, [pos]
            else:
                x, y = [pos], dset
            pyplot.scatter(x, y, color=color, s=150, marker='s')
        plot = pyplot.boxplot(
            data, positions=positions, widths=width, vert=vert)
        for key in ('boxes', 'caps', 'fliers', 'medians', 'whiskers'):
            pyplot.setp(plot[key], color=color)
        return matplotlib.patches.Patch(color=color)

    def _create_single_plot(self, vals):
        boxwidth = 0.5
        positions = range(1, len(vals) + 1)
        plot = self._add(positions, vals, boxwidth, self.colors[0])
        handles = [plot]
        pyplot.legend(
            handles, self.labels, prop={'size': 15}, loc=self.legend_loc)
        return True

    def _create_double_plot(self, vals1, vals2):
        if len(vals1) != len(vals2):
            raise PlotError(
                'The lists `vals1` and `vals2` must have the same length.\n'
                'vals1=%s\nvals2=%s\nticklabels=%s' % (
                    str(vals1), str(vals2), str(self.ticklabels)))
        boxwidth1 = 0.2
        boxwidth2 = 0.1
        offset = 0.32
        handles = []
        positions = range(1, len(vals1) + 1)
        plot = self._add(positions, vals1, boxwidth1, self.colors[0])
        handles.append(plot)
        positions = [_i + 1. + offset for _i in xrange(len(vals2))]
        plot = self._add(positions, vals2, boxwidth2, self.colors[1])
        handles.append(plot)
        if self.labels is not None:
            pyplot.legend(
                handles, self.labels, prop={'size': 15}, loc=self.legend_loc)
        return True

    def _create_triple_plot(self, vals1, vals2a, vals2b):
        if len(vals1) != len(vals2a) or len(vals2a) != len(vals2b):
            raise PlotError(
                'The lists `vals1`, `vals2a` and `vals2b` must have the same '
                'length.\nvals1=%s\nvals2a=%s\nvals2b=%s\nticklabels=%s' % (
                    str(vals1), str(vals2a), str(vals2b),
                    str(self.ticklabels)))
        boxwidth1 = 0.2
        boxwidth2 = 0.1
        offset = 0.32
        handles = []
        positions = range(1, len(vals1) + 1)
        plot = self._add(positions, vals1, boxwidth1, self.colors[0])
        handles.append(plot)
        for vals, d, bc in zip((vals2a, vals2b), (1, -1), self.colors[1:]):
            positions = [_i + 1. + offset * d for _i in xrange(len(vals))]
            plot = self._add(positions, vals, boxwidth2, bc)
            handles.append(plot)
        if self.labels is not None:
            pyplot.legend(
                handles, self.labels, prop={'size': 15}, loc=self.legend_loc)
        return True


class ViolinPlot(BoxPlot):
    """Violin plot class for one major and opt. one or two minor data sets.
    """

    def __init__(
            self, height, width, bw_method=0.05, fontsize=None,
            horizontal=False, lim=(None, None), loc='best', xlabel=None,
            ylabel=None):
        super(ViolinPlot, self).__init__(
            height, width, fontsize=fontsize, horizontal=horizontal,
            lim=lim, loc=loc, xlabel=xlabel, ylabel=ylabel)
        self.bw_method = bw_method

    def _add(self, positions, data, width, color=None):
        n = 100.
        num_trials = 10
        for d, p in zip(data, positions):
            if not d:
                continue
            bw = self.bw_method
            for i in xrange(num_trials):
                try:
                    k = scipy.stats.gaussian_kde(d, bw_method=bw)
                    llim = k.dataset.min()
                    ulim = k.dataset.max()
                    if llim == ulim:
                        raise ValueError
                    x = numpy.arange(llim, ulim, (ulim - llim) / n)
                    v = k.evaluate(x)
                    v = v / v.max() * width
                except (
                        FloatingPointError, ValueError,
                        numpy.linalg.LinAlgError):
                    if len(d) > 1 and i + 1 < num_trials:
                        try:
                            bw += float(self.bw_method)
                        except ValueError:
                            pass
                        else:
                            continue
                    # If gaussian KDE fails, add scatter plot instead.
                    for val in d:
                        if self.horizontal:
                            x, y = val, [p]
                        else:
                            x, y = [p], val
                        pyplot.scatter(x, y, color=color, s=150, marker='s')
                    break
            else:
                if self.horizontal:
                    fillfunc = pyplot.fill_between
                else:
                    fillfunc = pyplot.fill_betweenx
                fillfunc(
                    x, p, v + p, facecolor=color, alpha=1.0, edgecolor=color)
                fillfunc(
                    x, p, -v + p, facecolor=color, alpha=1.0, edgecolor=color)
        return matplotlib.patches.Patch(color=color)


class ProgressBar(Plot):

    def __init__(self, height, width):
        fontsize = 0.65 * height
        super(ProgressBar, self).__init__(height, width, fontsize=fontsize)
        self.elementwidth = self.width
        self.linewidth = 0.15 * height
        self.hpos = None
        self.runwidth = None

    def create(self, dres, num_runs, label=None):
        self._setup()
        pyplot.gca().set_axis_off()
        self.hpos = 0
        self.runwidth = self.width / num_runs
        if label is None:
            label_list = []
            num_rem = num_runs - len(dres.runs)
            if num_rem:
                label_list.append('remaining: %d' % num_rem)
            label_list.extend([
                '%s: %d' % (_pk, _pv) for _pk, _pv in dres.progress.iteritems()
                if _pk != 'started'])
            if 'started' in dres.progress:
                label_list.append('running: %s' % dres.status)
            label = ', '.join(label_list)
        self._add_docking(dres, label=label)
        pyplot.subplots_adjust(left=0., right=1., top=1., bottom=0.)
        return True

    def _add_docking(self, dres, dstart=0, label=None):
        dstart = self.hpos
        for run in dres.runs:
            self._add_run(run)
        # Add remaining runs.
        if self.hpos - dstart < self.elementwidth:
            self._add_remaining_runs(dres, dstart)
        # Add frame.
        pyplot.barh(
            bottom=0., width=self.elementwidth, height=1., left=dstart,
            linewidth=self.linewidth, edgecolor='black', fill=False)
        # Add label.
        if label:
            fontsize = min(self.fontsize, 80. * self.elementwidth / len(label))
            pyplot.text(
                dstart + .5 * self.elementwidth, .45, label, color='black',
                fontsize=fontsize, ha='center', va='center',
                family='monospace')
        return True

    def _add_remaining_runs(self, dres, dstart=0):
        if dres.done or dres.interrupted:
            hatch = '//'
            edgecolor = 'orange'
        elif dres.status == 'not started':
            hatch = None
            edgecolor = 'black'
        else:
            hatch = '//'
            edgecolor = 'lightgreen'
        h = self.elementwidth - (self.hpos - dstart)
        pyplot.barh(
            bottom=0., width=h, height=1., left=self.hpos, color='0.95',
            linewidth=0., hatch=hatch, edgecolor=edgecolor)
        self.hpos += h
        return True

    def _add_run(self, run):
        hatch = None
        edgecolor = 'black'
        if run.mainres.status == 'not started':
            color = '0.95'
            hatch = None
            edgecolor = 'black'
        elif run.status == 'failed':
            color = LIGHTRED
        elif run.interrupted:
            color = 'orange'
        elif run.status == 'finished':
            color = 'lightgreen'
        else:
            color = '0.95'
            edgecolor = 'green'
            hatch = '///'
        pyplot.barh(
            bottom=0., width=self.runwidth, height=1., left=self.hpos,
            color=color, edgecolor=edgecolor, hatch=hatch,
            linewidth=0.)
        self.hpos += self.runwidth
        return True


class PredictionRatePlot(Plot):

    def __init__(
            self, height, width, legend_loc=2,
            xlabel='Number of docking runs', ylabel='Prediction rate'):
        super(PredictionRatePlot, self).__init__(
            height, width, legend_loc=legend_loc, xlabel=xlabel, ylabel=ylabel)

    def create(self, data, errors=None):
        xulim = 3
        styles = ('-', '--', ':')
        lws = (2, 2, 2)
        self._setup()
        for (label, d), c, s, lw in zip(data.iteritems(), COLORS, styles, lws):
            xulim = max(xulim, len(d) + 1)
            x = range(1, len(d) + 1)
            pyplot.plot(x, d, label=label, ls=s, c=c, lw=lw)
            try:
                lerrs, uerrs = errors[label]
            except (IndexError, KeyError, TypeError):
                pass
            else:
                pyplot.fill_between(
                    x, lerrs, uerrs, facecolor=c, alpha=.2, interpolate=False)
        dxtick = max(1, int(xulim / 5.))
        pyplot.xticks(range(0, xulim, dxtick))
        pyplot.xlim(1, xulim - 1)
        pyplot.ylim((-0.02, 1.02))
        pyplot.legend(prop={'size': 12}, loc=self.legend_loc)
        return True


class ResiduePlot(Plot):

    def __init__(self, height, width, legend_loc=2, nres=10, ylabel=None):
        super(ResiduePlot, self).__init__(
            height, width, legend_loc=legend_loc, ylabel=ylabel)
        self.nres = nres

    def create(self, data, refdata=None, ylim=None):
        vals = data.values()
        minval = min(_val for _bar in vals for _val in _bar)
        maxval = max(_val for _bar in vals for _val in _bar)
        self._setup()
        xlabels = [
            ResidueFormatter.from_key(_key).short for _key in
            data.keys()[:self.nres]]
        pyplot.xticks(range(self.nres), xlabels, rotation=45)
        if refdata is not None:
            refranks = {
                _rn: _rank for _rn, _rank in
                zip(refdata.iterkeys(),
                    scipy.stats.rankdata(refdata.values()))}
            refplotdata = [
                (_i + 1, refdata[_rn], refranks[_rn]) for _i, _rn in
                enumerate(data.keys()[:self.nres]) if _rn in refdata]
            if refplotdata:
                refxdata = [_d[0] for _d in refplotdata]
                refydata = [_d[1] for _d in refplotdata]
                minval = min(minval, min(refydata))
                maxval = max(maxval, max(refydata))
                pyplot.scatter(
                    refxdata, refydata, color='g', marker='o', s=170,
                    label='reference', zorder=4)
                for x, y, rank in refplotdata:
                    pyplot.text(
                        x, y, '%d' % rank, zorder=5, color='white',
                        weight='bold', ha='center', va='center', fontsize=10)
                pyplot.legend(prop={'size': 12}, loc=self.legend_loc)
        pyplot.boxplot(vals)
        if ylim is not None:
            set_lim_within_bounds('y', (minval, maxval), add_margins=False)
            set_lim_within_bounds('y', ylim, add_margins=True)
        else:
            set_lim_within_bounds('y', (minval, maxval), add_margins=True)
        pyplot.tight_layout()
        return True


class ResidueChart(Plot):

    def __init__(self, height, width, nres=10):
        super(ResidueChart, self).__init__(height, width)
        self.nres = nres
        self.minlabelspace = 0.008
        self.minboxspace = 0.05**2

    def _create_bars(self, vals, reskeys, xlim, invert=False):
        xlabels = [
            ResidueFormatter.from_key(_key).short for _key in reskeys]
        pos = 0
        for i, val in enumerate(vals):
            if invert:
                val = -val
            try:
                resname = ResidueFormatter.from_key(reskeys[i]).name
                color = RESIDUE_COLORS[resname.upper()]
            except KeyError:
                color = ('0.8', '0.9')[i % 2]
            if val > self.minboxspace * xlim:
                pyplot.barh(
                    bottom=0.0, width=val, height=1.0, left=pos,
                    color=color, edgecolor='black', linewidth=1.5)
            if val > self.minlabelspace * xlim * len(xlabels[i]):
                pyplot.text(
                    pos + 0.1 * val, 0.1, '%s\n%.2f' % (xlabels[i], val),
                    color='black')
            pos += val
        return True


class ResidueDistanceChart(ResidueChart):

    def __init__(self, width, nres=10):
        height = int(width / 15.)
        super(ResidueDistanceChart, self).__init__(height, width, nres=nres)

    def create(self, data):
        if not data:
            return False
        self.fig = pyplot.figure(figsize=(15, 1))
        vals = []
        reskeys = []
        for reskey, val in data.items():
            if not vals or val / (sum(vals) + val) > self.minboxspace:
                vals.append(val)
                reskeys.append(reskey)
            if len(vals) == self.nres:
                break
        xlim = sum(vals)
        self._setup()
        pyplot.gca().set_axis_off()
        if not self._create_bars(vals, reskeys, xlim):
            return False
        pyplot.axis('tight')
        pyplot.tight_layout(h_pad=-1.0)
        pyplot.subplots_adjust(left=-0.0, right=1.0, top=1.0, bottom=-0.0)
        return True


class ResidueScoreChart(ResidueChart):

    def __init__(self, width, nres=10):
        height = int(2 * width / 15.)
        super(ResidueScoreChart, self).__init__(height, width, nres=nres)

    def create(self, data):
        if not data:
            return False
        axis = None
        negvals = []
        negreskeys = []
        for reskey, val in data.items():
            if val < 0 and (
                    not negvals or
                    val / (sum(negvals) + val) > self.minboxspace):
                negvals.append(val)
                negreskeys.append(reskey)
            if len(negvals) == self.nres:
                break
        xlim = -sum(negvals)
        posvals = []
        posreskeys = []
        for reskey, val in data.items()[::-1]:
            if val > 0 and sum(posvals) + val <= xlim:
                posvals.append(val)
                posreskeys.append(reskey)
            if len(posvals) == self.nres:
                break
        self._setup()
        if negvals:
            # Plot negative scoring dataibutions.
            axis = pyplot.subplot(211)
            axis.set_axis_off()
            self._create_bars(negvals, negreskeys, xlim, invert=True)
        if posvals:
            # Plot positive scoring dataibutions.
            axis = pyplot.subplot(212, sharex=axis)
            axis.set_axis_off()
            if not self._create_bars(posvals, posreskeys, xlim):
                return False
        pyplot.axis('tight')
        pyplot.tight_layout(h_pad=-1.0)
        pyplot.subplots_adjust(left=-0.0, right=1.0, top=1.0, bottom=-0.0)
        return True


class SamplingHistogram(Histogram):

    def __init__(self, height, width, xlabel='Value', ylabel='Frequency'):
        super(SamplingHistogram, self).__init__(
            height, width, xlabel=xlabel, ylabel=ylabel)

    def create(self, sampling, labels, ref=None):
        coord = 0
        data = []
        refdata = []
        while True:
            try:
                vals = [_state[coord] for _state in sampling]
            except IndexError:
                break
            if not vals:
                break
            if ref is not None:
                refdata.append(ref[0][coord])
            data.append(vals)
            coord += 1
        if coord == 0:
            return False
        self._setup()
        nbins, bins, patches = pyplot.hist(
            data, label=labels, bins=10, color=COLORS[:coord])
        self._fix_min_xlim(bins)
        self._set_yticks(nbins)
        if ref is not None:
            if len(refdata) == 1:
                self._mark_bin(refdata[0], bins, patches, color=COLORS[0])
            else:
                for i, (coordval, coordpatches) in enumerate(
                        zip(refdata, patches)):
                    self._mark_bin(
                        coordval, bins, coordpatches, color=COLORS[i])
        if len(labels) > 1:
            pyplot.legend(prop={'size': 12}, loc=self.legend_loc)
        return True


class SearchPlot(Plot):

    def __init__(self, height, width, ylabel, xlabel='Iteration'):
        super(SearchPlot, self).__init__(
            height, width, xlabel=xlabel, ylabel=ylabel)

    def create(self, interval, data, colors, refval=None):
        vals = [_x for _d in data for _x in _d]
        if not vals:
            return False
        self._setup()
        ax = pyplot.gca()
        final_vals = [_d[-1] for _d in data if _d]
        if colors is not None:
            ax.set_color_cycle(colors)
        max_it = None
        for dats in data:
            its = [_x * interval for _x, _ in enumerate(dats)]
            if max_it is None or its[-1] > max_it:
                max_it = its[-1]
            pyplot.plot(its, dats, '-')
        if refval:
            pyplot.axhline(refval, linestyle='--', color='g')
        yulim = max(numpy.percentile(vals, 90.), refval, max(final_vals))
        yllim = min(min(vals), refval)
        set_lim_within_bounds('y', (yllim, yulim), add_margins=True)
        ax.ticklabel_format(axis='x', style='sci', scilimits=(0, 2))
        ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
        pyplot.xlim(0, max_it)
        pyplot.tight_layout()
        return True


def set_lim_within_bounds(axis, max_range, add_margins=False):
    """Reduce the axis range if it is not within `max_range`.

    The parameter ``axis`` is either `x` or `y`.

    If the lower or upper axis limit `pyplot.xlim()` / `ylim()` lies within the
    bounds given bx `max_range` it is not changed. If a limit is changed, an
    additional margin is added on top of the values given by ``max_range`` if
    ``add_margins`` is ``True``.

    """
    if axis == 'x':
        limfunc = pyplot.xlim
    elif axis == 'y':
        limfunc = pyplot.ylim
    else:
        raise PlotError('Parameter ``axis`` must be either `x` or `y`.')
    lim = list(limfunc())
    if max_range[0] is not None:
        lim[0] = max(max_range[0], lim[0])
    if max_range[1] is not None:
        lim[1] = min(max_range[1], lim[1])
    if add_margins:
        margin = 0.05 * (lim[1] - lim[0])
        if max_range[0] is not None:
            lim[0] -= margin
        if max_range[1] is not None:
            lim[1] += margin
        if lim[0] == lim[1]:
            lim = (lim[0] - 1., lim[1] + 1.)
    if lim[0] == lim[1]:
        lim[0] -= .5
        lim[1] += .5
    limfunc(lim)
    return True
