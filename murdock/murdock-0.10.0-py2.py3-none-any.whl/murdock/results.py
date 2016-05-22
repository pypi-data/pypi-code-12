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
Module :mod:`murdock.results`
-----------------------------

Provides classes representing different Murdock results. The representations
are used in the :mod:`~murdock.runner` modules to store results and in the
:mod:`~murdock.report` module for postprocessing and to create presentation of
the results. This module provides one main class for each Murdock runner, i.e.
:class:`DockingResult`, :class:`ScreeningResult` and :class:`TrainingResult`.
In addition, it contains a large number of base and helper classes.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import codecs
import collections
import json
import logging
import os
import pickle
import time
import traceback

import numpy
import scipy.stats

import murdock.math
import murdock.misc

numpy.seterr(all='raise')
log = logging.getLogger('results')

INTERRUPTED_KEYS = ('CRASHED', 'KILLED', 'aborted')
DONE_KEYS = ('finished', 'failed')
RESIDUE_MEASURES = ('scores', 'distances')
QUALITY_MEASURES = ('RMSD', 'RMSATD')


class ResultError(Exception):
    pass


class MainResult(object):

    def __init__(
            self, label=None, notes=None, status='not started', title=None):
        self.label = label
        self.notes = notes
        self.status = status
        self._steps = None
        self.timing = Timing()
        self.title = title
        self.ranks = {}

    def __nonzero__(self):
        return self.label is not None

    @property
    def done(self):
        return self.status in DONE_KEYS

    @property
    def interrupted(self):
        return self.status in INTERRUPTED_KEYS

    @property
    def progress(self):
        progresses = {}
        for run in self.iter_runs():
            if run.status not in progresses:
                progresses[run.status] = 0
            progresses[run.status] += 1
        return collections.OrderedDict(sorted(progresses.items()))

    @property
    def running(self):
        if self.done or self.interrupted or self.status == 'not started':
            return False
        return True

    @property
    def steps(self):
        if self._steps is None:
            self._steps = []
            for run in self.iter_runs():
                for step in run.iter_steps():
                    if not step.status == 'finished':
                        break
                    if not self.add_step(step):
                        break
        return self._steps

    def add_step(self, step):
        if len(self._steps) < step.ind:
            raise ResultError(
                'Some step with index %d must be added before any step with '
                'index %d.' % (len(self._steps), step.ind))
        try:
            ms = self._steps[step.ind]
        except IndexError:
            self._steps.append(
                MultiStep(self, ind=step.ind, title=step.title))
        ms = self._steps[step.ind]
        if step in ms.samples:
            raise ResultError(
                'Results for run %d, step %d already added.' %
                (step.run.serial, step.serial))
        return ms.add(step)

    def from_json(self, data):
        try:
            self.label = data['label']
        except KeyError:
            pass
        try:
            self.title = data['title']
        except KeyError:
            pass
        try:
            self.timing.from_json(data['time'])
        except KeyError:
            pass
        try:
            self.notes = data['notes']
        except KeyError:
            pass
        return True

    def iter_runs(self, status=None):
        raise NotImplementedError

    def load_json(self, filepath, key, full=True, done=True):
        try:
            data = murdock.misc.load_ordered_json(filepath)[key]
        except KeyError:
            raise ValueError('Missing top-level key `%s`' % key)
        return self.from_json(data, full=full, done=done)

    def set_status(self, status):
        self.status = status
        return True

    def timing_fmt_mean(self, std=True):
        times = [_run.timing.total for _run in self.iter_runs('finished')]
        if not times:
            return {}
        mean_dt = _timing_mean(times)
        std_dt = _timing_std(times) if std else None
        return _timing_fmt_meanstd(mean_dt, std_dt)

    def timing_fmt_estimate(self, num_runs, std=True):
        if isinstance(self, ScreeningResult):
            num_runs *= len(self.dress)
        num_finished = sum(1 for _run in self.iter_runs('finished'))
        num_remaining = num_runs - num_finished
        times = [_run.timing.total for _run in self.iter_runs('finished')]
        if not times:
            return {}
        mean_dt = _timing_mean(times)
        tot_dt = mean_dt * num_runs
        rem_dt = mean_dt * num_remaining
        if std:
            std_dt = _timing_std(times) / num_finished * num_runs
        else:
            std_dt = None
        estimate = collections.OrderedDict()
        estimate['Total'] = _timing_fmt_meanstd(tot_dt, std_dt)
        estimate['Remaining'] = _timing_fmt_meanstd(rem_dt, std_dt)
        return estimate

    def to_json(self):
        data = collections.OrderedDict()
        if self.label:
            data['label'] = self.label
        if self.title:
            data['title'] = self.title
        data['timing'] = self.timing.to_json()
        if self.notes is not None:
            data['notes'] = self.notes
        return data

    def _clear_private_attributes(self):
        self.ranks = {}
        self._steps = None
        return True


class ScreeningResult(MainResult):

    def __init__(
            self, label=None, notes=None, status='not started', title=None):
        super(ScreeningResult, self).__init__(
            label=label, notes=notes, status=status, title=title)
        self.dress = []
        self._receptor = None
        self._ligands = []

    @property
    def ligands(self):
        if self._ligands is not None:
            return self._ligands
        ligands = [_dres.ligands for _dres in self.dress if _dres.ligands]
        unique_labels = set(
            [tuple(_lig.label for _lig in _ligs) for _ligs in ligands])
        if len(unique_labels) == 1:
            self._ligands = ligands[0]
        return self._ligands

    @property
    def receptor(self):
        if self._receptor is not None:
            return self._receptor
        receptors = [_dres.receptor for _dres in self.dress if _dres.receptor]
        unique_labels = set([_rec.label for _rec in receptors])
        if len(unique_labels) == 1:
            self._receptor = receptors[0]
        return self._receptor

    @property
    def references(self):
        if self._references is None:
            self._references = []
            for dres in self.dress:
                for step in dres.references:
                    try:
                        ms = self._references[step.ind]
                    except IndexError:
                        self._references.append(
                            MultiStep(self, ind=step.ind, title=step.title))
                    ms = self._references[step.ind]
                    if step in ms.samples:
                        raise ResultError(
                            'Reference for docking `%s`, step %d already '
                            'added.' % (dres.label, step.serial))
                    ms.add(step)
        return self._references

    def add_dres(self, dres):
        self._clear_private_attributes()
        self.dress.append(dres)
        return True

    def clear_dress(self):
        self.dress = []
        self._clear_private_attributes()
        return True

    def get_dres(self, label=None, title=None):
        for dres in self.dress:
            if label is not None and label == dres.label:
                return dres
            if title is not None and title == dres.title:
                return dres
        return None

    def get_mol(self, data=None, label=None, name=None):
        for dres in self.dress:
            try:
                return dres.get_mol(data=data, label=label, name=name)
            except ResultError:
                continue
        raise ResultError('Molecule `%s`/`%s` not found.' % (label, name))

    def iter_runs(self, status=None):
        for dres in self.dress:
            for run in dres.iter_runs(status):
                yield run

    def from_json(self, data, dockdata=None, full=True, done=True):
        self.__init__()
        super(ScreeningResult, self).from_json(data)
        if dockdata is None:
            return True
        for ddata in dockdata:
            d = DockingResult(sres=self)
            d.from_json(ddata, full=full, done=done)
            self.add_dres(d)
        return True

    def load_json(self, filepath, key='screening', full=True, done=True):
        return super(ScreeningResult, self).load_json(
            filepath, key, full=full, done=done)

    def set_status(self, status):
        super(ScreeningResult, self).set_status(status)
        if self.interrupted:
            for dres in self.dress:
                if dres.running:
                    dres.set_status(status)
        return True

    def timing_elapsed(self):
        elapsed = self.timing.elapsed
        elapsed.process += sum(
            _dres.timing.elapsed['process'] for _dres in self.dress)
        return elapsed

    def timing_extra(self):
        extras = {}
        for dres in self.dress:
            for exlabel, extd in dres.timing.extra.iteritems():
                if exlabel not in extras:
                    extras[exlabel] = TimingDict()
                    extras[exlabel]['process'] = 0.
                    extras[exlabel]['wall'] = 0.
                extras[exlabel] += extd
        return extras

    def _clear_private_attributes(self):
        super(ScreeningResult, self)._clear_private_attributes()
        self._ligands = []
        self._receptor = None
        self._references = None
        return True

    def _get_rates(
            self, step_ind, measure, ulim, top_ranked=False, top_scored=False,
            wsize=None):
        rates = []
        for dres in self.dress:
            rates = dres._get_rates(
                step_ind, measure, ulim, top_ranked=top_ranked,
                top_scored=top_ranked, wsize=wsize)
            rates.extend(rates)
        return rates


class TrainingResult(ScreeningResult):

    def __init__(
            self, label=None, notes=None, status='not started', title=None):
        super(TrainingResult, self).__init__(
            label=label, notes=notes, status=status, title=title)
        self.iterations = []

    @property
    def runs(self):
        return self.iterations[1:]

    @property
    def training_steps(self):
        return [
            MultiTrainingStep(self, ind=step.ind, title=step.title) for step
            in self.steps]

    def from_json(self, data, dockdata=None, full=True, done=True):
        self.__init__()
        super(TrainingResult, self).from_json(
            data, dockdata=dockdata, full=full, done=done)
        if 'iterations' in data:
            for ind, itdata in enumerate(data['iterations']):
                iteration = TrainingIteration(self, ind)
                if not iteration.from_json(itdata, done=done):
                    break
                self.iterations.append(iteration)
        return True

    def load_json(self, filepath, key='training', full=True, done=True):
        return super(TrainingResult, self).load_json(
            filepath, key, full=full, done=done)

    def new_iteration(self):
        ind = len(self.iterations)
        iteration = TrainingIteration(self, ind)
        iteration.set_status('started')
        self.iterations.append(iteration)
        return True

    def to_json(self):
        data = super(TrainingResult, self).to_json()
        data['status'] = self.status
        data['iterations'] = [_it.to_json() for _it in self.iterations]
        return data

    def update_status(self, num_runs=None):
        try:
            run = self.runs[-1]
        except IndexError:
            return False
        if num_runs is not None and len(self.runs) == num_runs and run.done:
            self.status = 'finished'
            return True
        if run.interrupted:
            self.status = run.status
            return True
        if run.ind == 0:
            self.status = 'initialization'
        else:
            self.status = 'iteration %d' % run.ind
        num_dress = len(self.dress)
        if not num_dress:
            return True
        num_done = sum(1 for _dres in self.dress if _dres.done)
        if num_dress == num_done:
            self.status += ' (optimizing)'
        else:
            self.status += ' (%d / %d)' % (num_done, num_dress)
        return True


class DockingResult(MainResult):

    def __init__(
            self, label=None, notes=None, status='not started', title=None,
            sres=None):
        super(DockingResult, self).__init__(
            label=label, notes=notes, status=status, title=title)
        self.clustering = None
        self.ligands = []
        self.receptor = None
        self.references = []
        self.runs = []
        self.sres = sres
        self.tags = []
        self.unbonded = []

    def add_reference(self, ref):
        self.references.append(ref)
        return True

    def add_run(self, run):
        self.runs.append(run)
        return True

    def add_unbonded(self, ub):
        self.unbonded.append(ub)
        return True

    def get_mol(self, data=None, label=None, name=None):
        if data is not None:
            if label is None and 'label' in data:
                label = data['label']
            if name is None and 'name' in data:
                name = data['name']
        if label is None and name is None:
            raise TypeError('Either `label` or `name` must be given.')
        if self.receptor is not None and (
                label == self.receptor.label or name == self.receptor.name):
            return self.receptor
        for lig in self.ligands:
            if name == lig.name:
                return lig
            if label == lig.label:
                return lig
        if name is not None:
            label = name
        raise ResultError('Molecule `%s`/`%s` not found.' % (label, name))

    def iter_mols(self):
        yield self.receptor
        for lig in self.ligands:
            yield lig

    def iter_runs(self, status=None):
        for run in self.runs:
            if status is None or run.status == status:
                yield run

    def from_json(self, data, full=True, done=True):
        self._clear_private_attributes()
        if self.sres is not None:
            self.sres._clear_private_attributes()
        self.__init__(sres=self.sres)
        super(DockingResult, self).from_json(data)
        try:
            self.status = data['status']
        except KeyError:
            pass
        try:
            moldata = data['moldata']
            self.new_molecules(moldata)
        except KeyError:
            pass
        if 'tags' in data:
            self.tags = data['tags']
        if not full:
            return True
        if 'reference' in data:
            for refdata in data['reference']:
                b = BasicStep(self)
                b.from_json(refdata)
                self.add_reference(b)
        if 'unbonded' in data:
            for ubdata in data['unbonded']:
                b = BasicStep(self)
                b.from_json(ubdata)
                self.add_unbonded(b)
        if 'runs' in data:
            for rundata in data['runs']:
                d = DockingRunResult(self)
                if not d.from_json(rundata, full=full, done=done):
                    break
                self.add_run(d)
        if 'clustering' in data:
            self.clustering = ClusteringResult(self)
            self.clustering.from_json(data['clustering'])
        return True

    def load_json(self, filepath, key='docking', full=True, done=True):
        return super(DockingResult, self).load_json(
            filepath, key, full=full, done=done)

    def new_clustering(self, method=None):
        self.clustering = ClusteringResult(self)
        if method:
            self.clustering.method = method
        return self.clustering

    def new_molecules(self, data):
        recinfo = data['receptor']
        liginfos = data['ligands']
        try:
            m = self.sres.get_mol(data=recinfo)
        except (AttributeError, KeyError, ResultError):
            m = MoleculeInfo('receptor')
            m.from_json(recinfo)
        self.receptor = m
        self.ligands = []
        for liginfo in liginfos:
            try:
                m = self.sres.get_mol(data=liginfo)
            except (AttributeError, KeyError, ResultError):
                m = MoleculeInfo('ligand')
                m.from_json(liginfo)
            self.ligands.append(m)
        return self.receptor, self.ligands

    def new_reference(
            self, ind, title, scoring, rotbonds=None, residues=None,
            sampling=None):
        ref = BasicStep(self, ind=ind, title=title)
        ref.new_scoring_result(scoring)
        if rotbonds:
            ref.new_rotbond_analysis(rotbonds)
        if residues:
            for measure, resdata in residues.iteritems():
                ref.new_residue_analysis(measure, resdata)
        if sampling:
            ref.add_sampling(sampling)
        self.add_reference(ref)
        return ref

    def new_run(self):
        ind = len(self.runs)
        run = DockingRunResult(self, ind=ind)
        self.add_run(run)
        self.update_status()
        return run

    def new_unbonded(self, ind, title, scoring, rotbonds):
        ub = BasicStep(self, ind=ind, title=title)
        ub.new_scoring_result(scoring)
        ub.new_rotbond_analysis(rotbonds)
        self.add_unbonded(ub)
        return ub

    def set_status(self, status):
        super(DockingResult, self).set_status(status)
        if self.interrupted:
            try:
                if self.runs[-1].steps[-1].running:
                    self.runs[-1].steps[-1].set_status(status)
            except IndexError:
                pass
        return True

    def timing_elapsed(self):
        return self.timing.elapsed

    def timing_extra(self):
        return self.timing.extra

    def to_json(self):
        data = super(DockingResult, self).to_json()
        data['status'] = self.status
        if self.receptor is not None or self.ligands:
            moldata = data['moldata'] = collections.OrderedDict()
        if self.receptor:
            moldata['receptor'] = self.receptor.to_json()
        if self.ligands:
            ligs = moldata['ligands'] = []
        for lig in self.ligands:
            ligs.append(lig.to_json())
        if self.tags:
            data['tags'] = self.tags
        if self.references:
            refs = data['reference'] = []
        for ref in self.references:
            refs.append(ref.to_json())
        if self.unbonded:
            ubs = data['unbonded'] = []
        for ub in self.unbonded:
            ubs.append(ub.to_json())
        if not self.runs:
            return data
        runs = data['runs'] = []
        for run in self.runs:
            runs.append(run.to_json())
        if self.clustering:
            data['clustering'] = self.clustering.to_json()
        return data

    def update_status(self, num_runs=None):
        try:
            run = self.runs[-1]
        except IndexError:
            return False
        if num_runs is not None and len(self.runs) == num_runs and run.done:
            if 'finished' in (_run.status for _run in self.runs):
                self.status = 'finished'
            else:
                self.status = 'failed'
            return True
        self.status = 'run %d' % run.serial
        if not run.steps:
            self.status += ', initializing'
        else:
            self.status += ', step %d' % run.steps[-1].serial
        return True

    def _get_rates(
            self, step_ind, measure, ulim, top_ranked=False, top_scored=False,
            wsize=None):
        wrates = []
        i0 = 0
        try:
            step = self.steps[step_ind]
        except IndexError:
            return wrates
        quals = [
            _s.qualities[measure] for _s in step.samples if measure in
            _s.qualities]
        if not quals:
            return wrates
        size = len(quals)
        while True:
            if wsize is None:
                wquals = quals
            else:
                if size < i0 + 1 or wsize > size or (wsize == size and i0 > 0):
                    break
                wquals = [
                    quals[_i+i0] if _i + i0 < size else quals[_i+i0-size]
                    for _i in xrange(wsize)]
            if top_ranked:
                wquals = [min(wquals, key=lambda _x: _x.rank)]
            elif top_scored:
                wquals = [min(wquals, key=lambda _x: _x.step.scoring.rank)]
            n = sum(1 for _q in wquals for _val in _q.itervalues())
            hits = sum(
                1 for _q in wquals for _val in _q.itervalues() if _val <= ulim)
            wrates.append(float(hits) / n)
            if wsize is None:
                break
            i0 += 1
        return wrates


class DockingRunResult(object):

    def __init__(self, mainres, ind=None):
        self.mainres = mainres
        self.ind = ind
        self.status = 'not started'
        self.steps = []
        self.timing = Timing()

    @property
    def done(self):
        return self.status in DONE_KEYS

    @property
    def interrupted(self):
        return self.status in INTERRUPTED_KEYS

    @property
    def serial(self):
        try:
            return self.ind + 1
        except TypeError:
            return None

    @property
    def running(self):
        if self.done or self.interrupted or self.status == 'not started':
            return False
        return True

    def add(self, step):
        self.steps.append(step)
        return True

    def iter_steps(self, status=None):
        for step in self.steps:
            if status is None or step.status == status:
                yield step

    def from_json(self, data, full=True, done=True):
        self.__init__(self.mainres)
        self.ind = data['run id'] - 1
        self.status = data['status']
        try:
            self.timing.from_json(data['time'])
        except KeyError:
            pass
        if 'steps' not in data:
            return False if done else True
        for stepdata in data['steps']:
            d = DockingStepResult(self.mainres, run=self)
            d.from_json(stepdata, full=full)
            if done and not d.done:
                if self.steps:
                    break
                else:
                    return False
            self.add(d)
        return True

    def new_step(self, title):
        ind = len(self.steps)
        step = DockingStepResult(self.mainres, self, ind=ind, title=title)
        self.add(step)
        self.mainres.update_status()
        return step

    def set_status(self, status):
        self.status = status
        return True

    def to_json(self):
        data = collections.OrderedDict()
        if self.ind is not None:
            data['run id'] = self.serial
        if self.status:
            data['status'] = self.status
        data['time'] = self.timing.to_json()
        if not self.steps:
            return data
        data['steps'] = []
        for step in self.steps:
            data['steps'].append(step.to_json())
        return data


class TrainingIteration(DockingRunResult):

    @property
    def serial(self):
        return self.ind

    def from_json(self, data, done=True):
        self.__init__(self.mainres)
        self.ind = data['run id']
        self.status = data['status']
        try:
            self.timing.from_json(data['time'])
        except KeyError:
            pass
        if 'steps' not in data:
            return False if done else True
        for stepdata in data['steps']:
            d = TrainingStep(self.mainres, iteration=self)
            d.from_json(stepdata)
            if done and not d.done:
                if self.steps:
                    break
                else:
                    return False
            self.add(d)
        return True

    def new_step(self, title):
        ind = len(self.steps)
        step = TrainingStep(self.mainres, self, ind, title)
        self.add(step)
        return True

    def update_status(self, num_dress):
        if True in (_dres.interrupted for _dres in self.mainres.dress):
            return True
        num_done = sum(1 for _dres in self.mainres.dress if _dres.done)
        if num_dress == num_done:
            self.status = 'optimizing'
        else:
            self.status = 'running (%d / %d)' % (num_done, num_dress)
        return True


class Step(object):

    def __init__(self, mainres, ind=None, title=None):
        self.mainres = mainres
        self.ind = ind
        self.status = None
        self.title = title

    def __nonzero__(self):
        return self.ind is not None

    @property
    def clustering(self):
        try:
            return self.mainres.clustering[self.ind]
        except IndexError:
            return None

    @property
    def done(self):
        return self.status in DONE_KEYS

    @property
    def interrupted(self):
        return self.status in INTERRUPTED_KEYS

    @property
    def reference(self):
        try:
            return self.mainres.references[self.ind]
        except IndexError:
            return None

    @property
    def running(self):
        if self.done or self.interrupted or self.status == 'not started':
            return False
        return True

    @property
    def serial(self):
        try:
            return self.ind + 1
        except TypeError:
            return None

    @property
    def unbonded(self):
        try:
            return self.mainres.unbonded[self.ind]
        except IndexError:
            return None

    def from_json(self, data):
        try:
            self.ind = data['step id'] - 1
        except KeyError:
            pass
        try:
            self.title = data['step title']
        except KeyError:
            pass
        try:
            self.status = data['status']
        except KeyError:
            pass
        return True

    def get_top_receptor_residues(self, measure, normalize=False):
        try:
            r = self.residues[measure][self.mainres.receptor]
        except KeyError:
            return None
        return r.get_top_residues(normalize)

    def to_json(self):
        data = collections.OrderedDict()
        if self.ind is not None:
            data['step id'] = self.serial
        if self.title:
            data['step title'] = self.title
        if self.status:
            data['status'] = self.status
        return data


class BasicStep(Step):

    def __init__(self, mainres, ind=None, title=None):
        super(BasicStep, self).__init__(mainres, ind=ind, title=title)
        self.residues = {}
        self.rotbonds = BasicRotatableBondAnalysis(self.mainres)
        self.sampling = None
        self.scoring = None
        self.timing = Timing()

    def from_json(self, data, full=True):
        super(BasicStep, self).__init__(self.mainres)
        super(BasicStep, self).from_json(data)
        try:
            self.timing.from_json(data['time'])
        except KeyError:
            pass
        if not full:
            return False
        try:
            sdata = data['scoring']
        except KeyError:
            self.scoring = BasicScoringResult(self)
        else:
            self.scoring = BasicScoringResult(self)
            self.scoring.from_json(sdata)
        for measure in RESIDUE_MEASURES:
            try:
                rdata = data['residues'][measure]
            except KeyError:
                continue
            self.residues[measure] = BasicResidueAnalysis(self, measure)
            self.residues[measure].from_json(rdata)
        try:
            self.sampling = data['sampling']
        except KeyError:
            pass
        try:
            rbdata = data['rotatable bonds']
        except KeyError:
            self.rotbonds = BasicRotatableBondAnalysis(self)
        else:
            self.rotbonds = BasicRotatableBondAnalysis(self)
            self.rotbonds.from_json(rbdata)
        return True

    def new_residue_analysis(self, measure, data):
        self.residues[measure] = BasicResidueAnalysis(self, measure)
        for src_mol, moldata in data.iteritems():
            mol = self.mainres.get_mol(label=src_mol.label, name=src_mol.name)
            b = BasicResidueResult(measure, mol)
            b.from_json(moldata)
            self.residues[measure].add_mol(mol, b)
        return self.residues[measure]

    def new_rotbond_analysis(self, data):
        self.rotbonds = BasicRotatableBondAnalysis(self)
        for src_mol, moldata in data.iteritems():
            mol = self.mainres.get_mol(label=src_mol.label, name=src_mol.name)
            self.rotbonds.add_mol(mol, moldata)
        return self.rotbonds

    def new_sampling_analysis(self, data):
        self.sampling = data
        return self.sampling

    def new_scoring_result(self, scoring):
        self.scoring = BasicScoringResult(self)
        self.scoring.total = scoring.total()
        for term in scoring.terms:
            self.scoring.terms[term.name] = term.weighted()
            self.scoring.unweighted[term.name] = term.unweighted()
        return self.scoring

    def to_json(self):
        data = super(BasicStep, self).to_json()
        data['time'] = self.timing.to_json()
        if self.scoring:
            data['scoring'] = self.scoring.to_json()
        if self.residues:
            data['residues'] = collections.OrderedDict()
        for measure, res in self.residues.iteritems():
            data['residues'][measure] = res.to_json()
        if self.rotbonds:
            data['rotatable bonds'] = self.rotbonds.to_json()
        return data


class MultiStep(Step):

    def __init__(self, mainres, ind=None, title=None):
        super(MultiStep, self).__init__(mainres, ind=ind, title=title)
        self.samples = []
        self._qualities = None
        self._residues = None
        self._rotbonds = None
        self._scoring = None

    @property
    def qualities(self):
        if self._qualities is None:
            self._qualities = {}
            for sample in self.samples:
                for measure in QUALITY_MEASURES:
                    try:
                        res = sample.qualities[measure]
                    except KeyError:
                        continue
                    try:
                        m = self._qualities[measure]
                    except KeyError:
                        m = self._qualities[measure] = MultiQuality(
                            self, measure)
                    m.add(res)
        return self._qualities

    @property
    def residues(self):
        if self._residues is None:
            self._residues = {}
            for sample in self.samples:
                for measure in RESIDUE_MEASURES:
                    try:
                        res = sample.residues[measure]
                    except KeyError:
                        continue
                    try:
                        mr = self._residues[measure]
                    except KeyError:
                        mr = self._residues[measure] = (
                            MultiResidueAnalysis(self, measure))
                    mr.add(res)
        return self._residues

    @property
    def rotbonds(self):
        if self._rotbonds is None:
            self._rotbonds = BasicRotatableBondAnalysis(self)
            for sample in self.samples:
                self._rotbonds.add(sample.rotbonds)
        return self._rotbonds

    @property
    def scoring(self):
        if self._scoring is None:
            self._scoring = MultiScoringResult(self)
            for sample in self.samples:
                self._scoring.add(sample.scoring)
        return self._scoring

    def get_unique_references(self):
        return set(
            _s.mainres.references[self.ind] for _s in self.samples if
            len(_s.mainres.references) > self.ind)

    def add(self, sample):
        self._clear_private_attributes()
        self.samples.append(sample)
        return True

    def iter_samples(self, status=None):
        for sample in self.samples:
            if status is None or sample.status == status:
                yield sample

    def timing_fmt_mean(self, std=True):
        times = [_sample.timing.total for _sample in self.samples]
        if not times:
            return {}
        mean_dt = _timing_mean(times)
        std_dt = _timing_std(times) if std else None
        return _timing_fmt_meanstd(mean_dt, std_dt)

    def _clear_private_attributes(self):
        self._qualities = None
        self._residues = None
        self._rotbonds = None
        self._scoring = None
        return True


class ClusteringStep(BasicStep):

    def __init__(self, mainres, ind=None, title=None):
        super(ClusteringStep, self).__init__(mainres, ind=ind, title=title)
        self.clusters = []
        self.parameters = {}

    def add(self, cluster):
        if cluster.ind != len(self.clusters):
            raise ResultError('Can not step with index %d at position %d.' % (
                cluster.ind, len(self.clusters)))
        self.clusters.append(cluster)
        return True

    def from_json(self, data):
        super(ClusteringStep, self).from_json(data)
        try:
            self.parameters = data['parameters']
        except KeyError:
            pass
        if 'clusters' not in data:
            return True
        for c_ind, cdat in enumerate(data['clusters']):
            cluster = MultiStep(self.mainres, c_ind)
            for sample in (
                    self.mainres.runs[_serial-1].steps[self.ind] for _serial in
                    cdat['run ids']):
                cluster.add(sample)
            self.clusters.append(cluster)
        return True

    def new_cluster(self, title, samples):
        ind = len(self.clusters)
        cluster = MultiStep(self.mainres, ind=ind)
        for sample in samples:
            cluster.add(sample)
        self.add(cluster)
        return cluster


class DockingStepResult(BasicStep):

    def __init__(
            self, mainres, run, ind=None, title=None):
        super(DockingStepResult, self).__init__(mainres, ind=ind, title=title)
        self.filepaths = collections.OrderedDict()
        self.qualities = {}
        self.run = run
        self.status = 'not started'

    @property
    def done(self):
        return self.status in DONE_KEYS

    @property
    def interrupted(self):
        return self.status in INTERRUPTED_KEYS

    @property
    def running(self):
        if self.done or self.interrupted or self.status == 'not started':
            return False
        return True

    def from_json(self, data, full=True):
        super(DockingStepResult, self).from_json(data, full=full)
        if not full:
            return True
        if 'filepaths' in data:
            for label, fp in data['filepaths'].iteritems():
                self.filepaths[self.mainres.get_mol(label=label)] = fp
        for measure in QUALITY_MEASURES:
            try:
                qdata = data[measure]
            except KeyError:
                continue
            b = BasicQuality(self, measure)
            b.from_json(qdata)
            self.qualities[measure] = b
        return True

    def new_quality(self, measure, data):
        self.qualities[measure] = BasicQuality(self, measure)
        for src_mol, moldata in data.iteritems():
            mol = self.mainres.get_mol(label=src_mol.label, name=src_mol.name)
            self.qualities[measure][mol] = moldata
        return self.qualities[measure]

    def to_json(self):
        data = super(DockingStepResult, self).to_json()
        if not self.filepaths:
            return data
        data['filepaths'] = collections.OrderedDict(
            (_mol.label, _fp) for _mol, _fp in self.filepaths.iteritems())
        if self.scoring:
            data['scoring'] = self.scoring.to_json()
        if self.residues:
            data['residues'] = collections.OrderedDict()
        for measure, res in self.residues.iteritems():
            data['residues'][measure] = res.to_json()
        if self.rotbonds:
            data['rotatable bonds'] = self.rotbonds.to_json()
        for measure, quality in self.qualities.iteritems():
            data[measure] = quality.to_json()
        return data

    def set_status(self, status):
        self.status = status
        if self.interrupted and not self.run.interrupted:
            self.run.set_status(status)
        return True


class TrainingStep(Step):

    def __init__(
            self, mainres, iteration, ind=None, title=None, weights=None,
            outliers=None, ratings=None, status='not started'):
        super(TrainingStep, self).__init__(mainres, ind=ind, title=title)
        self.iteration = iteration
        self.weights = weights
        self.outliers = outliers
        self.ratings = ratings
        self.status = status
        self.timing = Timing()

    def from_json(self, data):
        self.__init__(self.mainres, self.iteration)
        super(TrainingStep, self).from_json(data)
        try:
            self.timing.from_json(data['time'])
        except KeyError:
            pass
        try:
            self.weights = data['weights']
        except KeyError:
            pass
        try:
            self.outliers = data['outliers']
        except KeyError:
            pass
        try:
            self.ratings = data['ratings']
        except KeyError:
            pass
        return True

    def new_outliers(self, outliers):
        self.outliers = [_dres.label for _dres in outliers]
        return True

    def new_ratings(self, ratings):
        self.ratings = collections.OrderedDict(
            (_dres.label, _r) for _dres, _r in ratings.iteritems())
        return True

    def new_weights(self, termnames, weights):
        self.weights = collections.OrderedDict(
            (_tn, _tw) for _tn, _tw in zip(termnames, weights))
        return True

    def set_status(self, status):
        self.status = status
        return True

    def to_json(self):
        data = super(TrainingStep, self).to_json()
        data['time'] = self.timing.to_json()
        if self.weights:
            data['weights'] = self.weights
        if self.outliers:
            data['outliers'] = self.outliers
        if self.ratings:
            data['ratings'] = self.ratings
        return data


class MultiTrainingStep(Step):

    @property
    def outliers(self):
        outliers = []
        for it in self.mainres.iterations[1:]:
            try:
                ol = it.steps[self.ind].outliers
            except IndexError:
                break
            if ol is None:
                ol = []
            outliers.append(ol)
        return outliers

    @property
    def ratings(self):
        ratings = []
        for it in self.mainres.iterations[1:]:
            try:
                r = it.steps[self.ind].ratings
            except IndexError:
                break
            if r is None:
                break
            ratings.append(r.values())
        return ratings

    @property
    def rating_means(self):
        return [numpy.mean(_r) for _r in self.ratings]

    @property
    def terms(self):
        terms = collections.OrderedDict()
        for it in self.mainres.iterations:
            try:
                weights = it.steps[self.ind].weights
            except IndexError:
                continue
            if weights is None:
                continue
            for tname, weight in weights.iteritems():
                try:
                    term = terms[tname]
                except KeyError:
                    term = terms[tname] = []
                for dres in self.mainres.dress:
                    try:
                        s = dres.runs[it.ind].steps[self.ind].scoring
                    except (AttributeError, IndexError) as exc:
                        continue
                    if not s.unweighted:
                        continue
                    val = weight * s.unweighted[tname]
                    try:
                        term[it.ind].append(val)
                    except IndexError:
                        term.append([])
                        term[it.ind].append(val)
        return terms

    @property
    def term_means(self):
        return collections.OrderedDict(
            (_tn, [numpy.mean(_vals) for _vals in _its if _vals]) for _tn,
            _its in self.terms.iteritems())

    @property
    def ref_terms(self):
        terms = collections.OrderedDict()
        for it in self.mainres.iterations:
            try:
                weights = it.steps[self.ind].weights
            except IndexError:
                continue
            if weights is None:
                break
            for tname, weight in weights.iteritems():
                try:
                    term = terms[tname]
                except KeyError:
                    term = terms[tname] = []
                for dres in self.mainres.dress:
                    try:
                        s = dres.references[self.ind].scoring
                    except (AttributeError, IndexError):
                        continue
                    if not s.unweighted:
                        continue
                    val = weight * s.unweighted[tname]
                    try:
                        term[it.ind].append(val)
                    except IndexError:
                        term.append([])
                        term[it.ind].append(val)
        return terms

    @property
    def ref_term_means(self):
        return collections.OrderedDict(
            (_tn, [numpy.mean(_vals) for _vals in _its if _vals]) for _tn,
            _its in self.ref_terms.iteritems())


class ClusteringResult(list):

    def __init__(self, mainres):
        super(ClusteringResult, self).__init__()
        self.mainres = mainres
        self.method = {}

    def add(self, step):
        if step.ind != len(self):
            raise ResultError('Can not step with index %d at position %d.' % (
                step.ind, len(self)))
        self.append(step)
        return True

    def from_json(self, data):
        del self[:]
        try:
            self.method = data['method']
        except KeyError:
            pass
        if 'steps' not in data:
            return True
        for stepdata in data['steps']:
            c = ClusteringStep(self.mainres)
            c.from_json(stepdata)
            self.add(c)
        return True

    def new_step(self, ind, title):
        step = ClusteringStep(self.mainres, ind=ind, title=title)
        try:
            self[ind] = step
        except IndexError:
            self.add(step)
        return step

    def to_json(self):
        data = collections.OrderedDict()
        if self.method:
            data['method'] = self.method
        data['steps'] = []
        for step in self:
            data['steps'].append(step.to_json())
        return data


class MoleculeInfo(object):

    def __init__(self, mtype=None):
        self.description = None
        self.filepath = None
        self.filepath_ref = None
        self.filepath_resid = None
        self.label = None
        self.mtype = mtype
        self.name = None
        self.notes = None
        self.resolution = None
        self.tags = []

    def from_json(self, data):
        self.filepath = data['filepath']
        try:
            self.filepath_ref = data['ref_filepath']
        except KeyError:
            pass
        try:
            self.filepath_resid = data['residuals_filepath']
        except KeyError:
            pass
        try:
            self.description = data['description']
        except KeyError:
            pass
        self.label = data['label']
        try:
            self.name = data['name']
        except KeyError:
            self.name = self.label
        try:
            self.notes = data['notes']
        except KeyError:
            pass
        try:
            self.resolution = data['resolution']
        except KeyError:
            pass
        try:
            self.tags = data['tags']
        except KeyError:
            pass
        return True

    def to_json(self):
        data = collections.OrderedDict()
        if self.name:
            data['name'] = self.name
        if self.label:
            data['label'] = self.label
        if self.filepath:
            data['filepath'] = self.filepath
        if self.filepath_ref:
            data['ref_filepath'] = self.filepath_ref
        if self.filepath_resid:
            data['residuals_filepath'] = self.filepath_resid
        if self.description:
            data['description'] = self.description
        if self.resolution:
            self.resolution = data['resolution']
        if self.notes:
            data['notes'] = self.notes
        if self.tags:
            data['tags'] = self.tags
        return data


class Timing(object):

    def __init__(self, add_subprocs=False):
        self.add_subprocs = add_subprocs
        self.start = TimingDict(add_subprocs=add_subprocs)
        self.end = TimingDict(add_subprocs=add_subprocs)
        self.extra = {}
        self.start.set_current()

    @property
    def elapsed(self):
        if not self.start:
            return None
        if self.end:
            return self.total
        td = TimingDict(add_subprocs=self.add_subprocs)
        td.set_current()
        return td - self.start

    @property
    def total(self):
        if not self.start or not self.end:
            return None
        return self.end - self.start

    def from_json(self, data):
        try:
            pdata = data['process']
            wdata = data['wall']
        except KeyError:
            return False
        try:
            self.end['process'] = self.start['process'] + float(pdata['total'])
            self.end['wall'] = self.start['wall'] + float(wdata['total'])
        except (KeyError, TypeError):
            pass
        for key, val in pdata.iteritems():
            if key in ('start', 'total'):
                continue
            try:
                self.extra[key] = TimingDict(
                    process=float(pdata[key]), wall=float(wdata[key]),
                    add_subprocs=self.add_subprocs)
            except (KeyError, TypeError):
                pass
        return True

    def to_json(self):
        data = {
            'process': collections.OrderedDict(),
            'wall': collections.OrderedDict()}
        total = self.total
        for key in data.iterkeys():
            if total is not None:
                data[key]['total'] = total[key]
            else:
                try:
                    data[key]['elapsed'] = '%f' % self.elapsed[key]
                except TypeError:
                    pass
            for exkey, exdat in self.extra.iteritems():
                try:
                    data[key][exkey] = '%f' % exdat[key]
                except TypeError:
                    pass
        return data


class TimingDict(collections.OrderedDict):

    def __init__(self, add_subprocs=False, process=None, wall=None):
        super(TimingDict, self).__init__()
        self['process'] = None
        self['wall'] = None
        self.add_subprocs = add_subprocs
        if process is not None:
            self['process'] = process
        if wall is not None:
            self['wall'] = wall

    def __add__(self, td):
        process = self['process'] + td['process']
        wall = self['wall'] + td['wall']
        return TimingDict(
            process=process, wall=wall, add_subprocs=self.add_subprocs)

    def __truediv__(self, x):
        process = self['process'] / x
        wall = self['wall'] / x
        return TimingDict(
            process=process, wall=wall, add_subprocs=self.add_subprocs)

    def __mul__(self, x):
        process = self['process'] * x
        wall = self['wall'] * x
        return TimingDict(
            process=process, wall=wall, add_subprocs=self.add_subprocs)

    def __nonzero__(self):
        return self['process'] is not None or self['wall'] is not None

    def __sub__(self, td):
        process = self['process'] - td['process']
        wall = self['wall'] - td['wall']
        return TimingDict(
            process=process, wall=wall, add_subprocs=self.add_subprocs)

    @property
    def _pind(self):
        return 3 if self.add_subprocs else 2

    def clear(self):
        self['process'] = None
        self['wall'] = None
        return True

    def formatted(self, key):
        try:
            gmt = time.gmtime(self[key])
        except ValueError:
            return ''
        ftd = ''
        d = int(time.strftime('%d', gmt)) - 1
        if d > 0:
            ftd += '%02dd ' % d
        h = int(time.strftime('%H', gmt))
        m = int(time.strftime('%M', gmt))
        if h > 0:
            ftd += '%02dh ' % h
        if d > 0 or h > 0 or m > 0:
            ftd += '%02dm ' % m
        if not d and not h:
            ftd += time.strftime('%Ss', gmt)
        return ftd

    def set_current(self):
        self['process'] = sum(os.times()[:self._pind])
        self['wall'] = time.time()
        return True


class ResidueResult(collections.OrderedDict):

    def __init__(self, measure, mol):
        super(ResidueResult, self).__init__()
        self.measure = measure
        self.mol = mol
        self._sorted_by_value = False
        self._top_residues = None
        self._top_residues_normed = None
        self._llim = None
        self._ulim = None

    def _clear_private_attributes(self):
        self._sorted_by_value = False
        self._top_residues = None
        self._top_residues_normed = None
        self._llim = None
        self._ulim = None
        return True


class BasicResidueResult(ResidueResult):

    def __init__(self, measure, mol):
        super(BasicResidueResult, self).__init__(measure, mol)

    @property
    def llim(self):
        if self._llim is not None or not self:
            return self._llim
        self._llim = min(self.itervalues())
        return self._llim

    @property
    def ulim(self):
        if self._ulim is not None or not self:
            return self._ulim
        self.sort_by_value()
        values = self.values()
        self._ulim = numpy.mean(values[:20])
        return self._ulim

    def get_top_residues(self, normalize=False):
        if normalize:
            if self._top_residues_normed is not None or not self:
                return self._top_residues_normed
        else:
            if self._top_residues is not None or not self:
                return self._top_residues
        self.sort_by_value()
        ulim = self.ulim
        if normalize:
            llim = self.llim
            topres = [
                (_r, murdock.math.normalize(_val, llim, ulim)) for _r, _val in
                self.iteritems() if _val < ulim]
            self._top_residues_normed = collections.OrderedDict(topres)
            return self._top_residues_normed
        else:
            topres = [
                (_r, _val) for _r, _val in self.iteritems() if _val < ulim]
            self._top_residues = collections.OrderedDict(topres)
            return self._top_residues

    def sort_by_value(self, reverse=False):
        if self._sorted_by_value:
            return True
        data = sorted(self.items(), key=lambda _x: _x[1], reverse=reverse)
        self.clear()
        for resname, resval in data:
            self[resname] = resval
        self._sorted_by_value = True
        return True

    def match(self, ref, top=False):
        """Return matching residues.

        Residues in ``self`` and in ``ref`` are filtered keeping only values
        below ``ulim``. Then a list of all residue names in ``ref`` which are
        also found in ``self`` is returned. The second return value is the
        length of all residues below ``ulim`` in ``ref``, so the quotient of
        the two return values is the relative matching.

        """
        if top:
            ress = self.get_top_residues()
            ref_ress = ref.get_top_residues()
        else:
            ress = self
            ref_ress = ref
        common = [_rn for _rn in ref_ress.iterkeys() if _rn in ress]
        return len(common), len(ref_ress)

    def from_json(self, data):
        self.clear()
        self._clear_private_attributes()
        for resname, resval in data.iteritems():
            self[resname] = resval
        return True

    def set_llim(self, val):
        if val == self._llim:
            return True
        self._llim = val
        self._top_residues = None
        self._top_residues_normed = None
        return True

    def set_ulim(self, val):
        if val == self._ulim:
            return True
        self._ulim = val
        self._top_residues = None
        self._top_residues_normed = None
        return True

    def unset_llim(self):
        self._llim = None
        self._top_residues = None
        self._top_residues_normed = None
        return True

    def unset_ulim(self):
        self._ulim = None
        self._top_residues = None
        self._top_residues_normed = None
        return True


class MultiResidueResult(ResidueResult):

    def __init__(self, measure, mol):
        super(MultiResidueResult, self).__init__(measure, mol)
        self._medians = None

    @property
    def llim(self):
        if self._llim is not None or not self:
            return self._llim
        self._llim = min(self.medians.itervalues())
        return self._llim

    @property
    def ulim(self):
        if self._ulim is not None or not self:
            return self._ulim
        medians = self.medians
        self._ulim = numpy.mean(medians.values()[:20])
        return self._ulim

    @property
    def medians(self):
        if self._medians is not None or not self:
            return self._medians
        self._medians = collections.OrderedDict(
            (_k, numpy.median(_vals)) for _k, _vals in self.iteritems() if
            _vals)
        return self._medians

    def add(self, result):
        for resname, resval in result.iteritems():
            self.add_res(resname, resval)
        return True

    def add_res(self, res, resval):
        self._clear_private_attributes()
        if res not in self:
            self[res] = []
        self[res].append(resval)
        return True

    def get_top_residues(self, normalize=False):
        if normalize:
            if self._top_residues_normed is not None or not self:
                return self._top_residues_normed
        else:
            if self._top_residues is not None or not self:
                return self._top_residues
        self.sort_by_value()
        medians = self.medians
        ulim = self.ulim
        if normalize:
            llim = self.llim
            topres = (
                (_r, murdock.math.normalize(_val, llim, ulim)) for _r, _val in
                medians.iteritems() if _val < ulim)
            self._top_residues_normed = collections.OrderedDict(topres)
            return self._top_residues_normed
        else:
            topres = (
                (_r, _val) for _r, _val in medians.iteritems() if _val < ulim)
            self._top_residues = collections.OrderedDict(topres)
            return self._top_residues

    def sort_by_value(self, reverse=False):
        if self._sorted_by_value:
            return True
        data = sorted(
            self.items(), key=lambda _x: numpy.percentile(_x[1], 25),
            reverse=reverse)
        self.clear()
        for resname, resvals in data:
            self[resname] = resvals
        self._sorted_by_value = True
        return True

    def _clear_private_attributes(self):
        super(MultiResidueResult, self)._clear_private_attributes()
        self._medians = None
        return True


class ResidueAnalysis(collections.OrderedDict):

    def __init__(self, step, measure):
        super(ResidueAnalysis, self).__init__()
        self.measure = measure
        self.step = step


class BasicResidueAnalysis(ResidueAnalysis):

    def __init__(self, step, measure):
        super(BasicResidueAnalysis, self).__init__(step, measure)

    def add_mol(self, mol, result):
        self[mol] = result
        return True

    def from_json(self, data):
        self.clear()
        for mollabel, moldata in data.iteritems():
            mol = self.step.mainres.get_mol(label=mollabel)
            b = BasicResidueResult(self.measure, mol)
            b.from_json(moldata)
            self.add_mol(mol, b)
        return True

    def to_json(self):
        data = collections.OrderedDict()
        for mol, moldata in self.iteritems():
            data[mol.label] = moldata
        return data


class MultiResidueAnalysis(ResidueAnalysis):

    def add(self, ress):
        for mol, molres in ress.iteritems():
            self.add_mol(mol, molres)
        return True

    def add_mol(self, mol, molres):
        try:
            msrr = self[mol]
        except KeyError:
            msrr = self[mol] = MultiResidueResult(self.measure, mol)
        msrr.add(molres)
        return True


class RotatableBondAnalysis(collections.OrderedDict):

    def __init__(self, step):
        super(RotatableBondAnalysis, self).__init__()
        self.step = step


class BasicRotatableBondAnalysis(RotatableBondAnalysis):

    def __init__(self, step):
        super(BasicRotatableBondAnalysis, self).__init__(step)

    def add(self, data):
        for mol, moldata in data.iteritems():
            self.add_mol(mol, moldata)
        return True

    def add_mol(self, mol, moldata):
        if mol not in self:
            self[mol] = []
        self[mol].extend(moldata)
        return True

    def from_json(self, data):
        self.clear()
        for mollabel, moldata in data.iteritems():
            if moldata:
                mol = self.step.mainres.get_mol(label=mollabel)
                self.add_mol(mol, moldata)
        return True

    def get_bond_dict(self, mol, norm=1):
        if mol not in self:
            return {}
        bd = collections.OrderedDict()
        for bond in self[mol]:
            bname = bond['name']
            if bname not in bd:
                bd[bname] = []
            bd[bname].append(norm * bond['angle'])
        return bd

    def get_unique_bondnames(self):
        return set(
            _bond['name'] for _molbonds in self.itervalues() for _bond in
            _molbonds)

    def to_json(self):
        data = collections.OrderedDict()
        for mol, moldata in self.iteritems():
            data[mol.label] = moldata
        return data


class ScoringResult(object):

    def __init__(self, step):
        self.step = step

    @property
    def termnames(self):
        return self.terms.keys()


class BasicScoringResult(ScoringResult):

    def __init__(self, step):
        super(BasicScoringResult, self).__init__(step)
        self.terms = {}
        self.total = None
        self.unweighted = {}

    def __nonzero__(self):
        return self.total is not None

    @property
    def rank(self):
        try:
            return self.step.run.mainres.ranks[id(self)]
        except KeyError:
            ms = self.step.run.mainres.steps[self.step.ind]
            ms.scoring.create_ranking()
            return self.step.run.mainres.ranks[id(self)]

    def from_json(self, data):
        self.total = data['total']
        self.terms = data['terms']['weighted']
        self.unweighted = data['terms']['unweighted']
        return True

    def to_json(self):
        data = collections.OrderedDict()
        if not self:
            return data
        data['total'] = self.total
        if self.terms or self.unweighted:
            data['terms'] = {}
        if self.terms:
            data['terms']['weighted'] = self.terms
        if self.unweighted:
            data['terms']['unweighted'] = self.unweighted
        return data


class MultiScoringResult(ScoringResult):

    def __init__(self, step):
        super(MultiScoringResult, self).__init__(step)
        self.scorings = []
        self._terms = None
        self._total = None
        self._unweighted = None
        self._max_total = None
        self._min_total = None
        self._mean_total = None
        self._std_total = None
        self._max_term = {}
        self._min_term = {}
        self._mean_term = {}
        self._std_term = {}

    @property
    def terms(self):
        if self._terms is None:
            self._terms = {}
            for scoring in self.scorings:
                for tname, tval in scoring.terms.iteritems():
                    try:
                        term = self._terms[tname]
                    except KeyError:
                        term = self._terms[tname] = []
                    term.append(tval)
        return self._terms

    @property
    def total(self):
        if self._total is None:
            self._total = [_s.total for _s in self.scorings]
        return self._total

    @property
    def unweighted(self):
        if self._unweighted is None:
            self._unweighted = {}
            for scoring in self.scorings:
                for tname, tval in scoring.unweighted.iteritems():
                    try:
                        term = self._unweighted[tname]
                    except KeyError:
                        term = self._unweighted[tname] = []
                    term.append(tval)
        return self._unweighted

    def add(self, scoring):
        self._clear_private_attributes()
        self._clear_ranking()
        self.scorings.append(scoring)
        return True

    def create_ranking(self):
        ranks = scipy.stats.rankdata(self.total, method='ordinal')
        for scoring, rank in zip(self.scorings, ranks):
            self.step.mainres.ranks[id(scoring)] = rank
        return True

    def max_total(self):
        if self._max_total is None:
            try:
                self._max_total = max(self.total)
            except (TypeError, ValueError):
                return None
        return self._max_total

    def min_total(self):
        if self._min_total is None:
            try:
                self._min_total = min(self.total)
            except (TypeError, ValueError):
                return None
        return self._min_total

    def mean_total(self, std=False):
        if self._mean_total is None:
            try:
                self._mean_total = numpy.mean(self.total)
            except (TypeError, ValueError):
                return None
        return self._mean_total

    def std_total(self):
        if self._std_total is None:
            try:
                self._std_total = numpy.std(self.total)
            except (TypeError, ValueError):
                return None
        return self._std_total

    def max_term(self, tname):
        if tname not in self._max_term:
            try:
                self._max_term[tname] = max(self.terms[tname])
            except (KeyError, TypeError, ValueError):
                return None
        return self._max_term[tname]

    def min_term(self, tname):
        if tname not in self._min_term:
            try:
                self._min_term[tname] = min(self.terms[tname])
            except (KeyError, TypeError, ValueError):
                return None
        return self._min_term[tname]

    def mean_term(self, tname):
        if tname not in self._mean_term:
            try:
                self._mean_term[tname] = numpy.mean(self.terms[tname])
            except (KeyError, TypeError, ValueError):
                return None
        return self._mean_term[tname]

    def std_term(self, tname):
        if tname not in self._std_term:
            try:
                self._std_term[tname] = numpy.std(self.terms[tname])
            except (KeyError, TypeError, ValueError):
                return None
        return self._std_term[tname]

    def _clear_private_attributes(self):
        self._terms = None
        self._total = None
        self._unweighted = None
        self._max_total = None
        self._min_total = None
        self._mean_total = None
        self._std_total = None
        self._max_term = {}
        self._min_term = {}
        self._mean_term = {}
        self._std_term = {}
        return True

    def _clear_ranking(self):
        for scoring in self.scorings:
            try:
                del self.step.mainres.ranks[id(scoring)]
            except KeyError:
                pass
        return True


class TrainingTerm(object):

    def __init__(self, name, weight):
        self.name = name
        self.weight = weight


class Quality(collections.OrderedDict):

    def __init__(self, step, measure):
        super(Quality, self).__init__()
        self.step = step
        self.measure = measure
        self._mean = None
        self._std = None

    @property
    def mean(self):
        if self._mean is None:
            self._mean = numpy.mean(self.values())
        return self._mean

    @property
    def std(self):
        if self._std is None:
            self._std = numpy.std(self.values())
        return self._std

    def _clear_private_attributes(self):
        self._mean = None
        self._std = None
        return True


class BasicQuality(Quality):

    @property
    def rank(self):
        try:
            return self.step.run.mainres.ranks[id(self)]
        except KeyError:
            ms = self.step.run.mainres.steps[self.step.ind]
            ms.qualities[self.measure].create_ranking()
            return self.step.run.mainres.ranks[id(self)]

    def from_json(self, data):
        self.clear()
        self._clear_private_attributes()
        for mollabel, molval in data.iteritems():
            if molval is not None:
                mol = self.step.mainres.get_mol(label=mollabel)
                self[mol] = molval
        return True

    def to_json(self):
        data = collections.OrderedDict()
        for mol, molval in self.iteritems():
            data[mol.label] = molval
        return data


class MultiQuality(Quality):

    def __init__(self, step, measure):
        super(MultiQuality, self).__init__(step, measure)
        self.qualities = []

    def add(self, quality):
        self._clear_private_attributes()
        self._clear_ranking()
        for mol, val in quality.iteritems():
            try:
                ress = self[mol]
            except KeyError:
                ress = self[mol] = []
            ress.append(val)
        self.qualities.append(quality)
        return True

    def create_ranking(self):
        meanvals = [_s.mean for _s in self.qualities]
        if not meanvals:
            return False
        ranks = scipy.stats.rankdata(meanvals, method='ordinal')
        for quality, rank in zip(self.qualities, ranks):
            self.step.mainres.ranks[id(quality)] = rank
        return True

    def get_rate(self, ulim, top_ranked=False, top_scored=False, err=False):
        rates = self.mainres._get_rates(
            self.step.ind, self.measure, ulim, top_ranked=top_ranked,
            top_scored=top_scored)
        if err:
            return numpy.mean(rates), numpy.std(rates) / numpy.sqrt(len(rates))
        else:
            return numpy.mean(rates)

    def get_rates(self, ulim, top_ranked=False, top_scored=False, err=False):
        rates = []
        if err:
            errs = []
        wsize = 1
        while True:
            wrates = self.step.mainres._get_rates(
                self.step.ind, self.measure, ulim, top_ranked=top_ranked,
                top_scored=top_scored, wsize=wsize)
            if not wrates:
                break
            rates.append(numpy.mean(wrates))
            if err:
                errs.append(numpy.std(wrates) / numpy.sqrt(len(wrates)))
            wsize += 1
        if err:
            return rates, errs
        else:
            return rates

    def get_std(self):
        vals = [_val for _vals in self.itervalues() for _val in _vals]
        if not vals:
            return None
        return numpy.std(vals)

    def _clear_ranking(self):
        for quality in self.qualities:
            try:
                del self.step.mainres.ranks[id(quality)]
            except KeyError:
                pass
        return True


def _timing_fmt_meanstd(mean_dt, std_dt=None):
    fmt_times = collections.OrderedDict()
    for ttype in ('process', 'wall'):
        fmt_times[ttype] = mean_dt.formatted(ttype)
        if std_dt:
            fmt_times[ttype] += ' +/- %s' % std_dt.formatted(ttype)
    return fmt_times


def _timing_mean(timings):
    return TimingDict(
        process=numpy.mean([_t['process'] for _t in timings]),
        wall=numpy.mean([_t['wall'] for _t in timings]))


def _timing_std(timings):
    return TimingDict(
        process=numpy.std([_t['process'] for _t in timings]),
        wall=numpy.std([_t['wall'] for _t in timings]))
