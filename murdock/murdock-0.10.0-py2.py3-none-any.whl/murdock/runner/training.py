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
Module :mod:`murdock.runner.training`
-------------------------------------

Provides the class :class:`Training` used to initialize and run a scoring
weight training setup. The class :class:`Training` inherits from the
:class:`~murdock.runner.screening.Screening` and iteratively alternates between
a docking phase and a scoring weight calibration phase performed using
the classes :class:`DockingTrainer` and :class:`ScreeningTrainer`.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import collections
import itertools
import os
import time
import signal

import numpy

import murdock.config
from murdock.logger import Logger
from murdock.misc import int_gt_zero, int_ge_zero
from murdock.report import TrainingReport
from murdock.results import TrainingResult
from murdock.runner.runner import MurdockInterrupt, MurdockTerminate
import murdock.runner.screening


log = Logger(name='training').logger


class TrainingError(Exception):
    pass


class Training(murdock.runner.screening.Screening):
    """A training class.

    The class is used to iteratively train scoring weights by alternating
    between a screening step creating training decoys and a tuning step
    optimizing the weights.

    """

    def __init__(
            self, label, title, moldata, docking_steps, raster, resdir='.',
            restore=False, resume=False, num_runs=1, docked_suffix='',
            result_suffix='-results', num_procs=1, num_threads=None,
            preprocessing=None, dry=False, report_projects=None, reverse=False,
            notes=None, update_interval=1, debugsampling=False,
            pymolexec=None, pymolscript=None, failmode='continue',
            draw_resscore_charts=False, draw_resdist_charts=False,
            outfmts=None, function=None, term_kwargs=None, logger=None):
        if logger is not None:
            global log
            log = logger
        super(Training, self).__init__(
            moldata, docking_steps, resdir=resdir, restore=restore,
            resume=resume, num_runs=1, docked_suffix=docked_suffix,
            result_suffix=result_suffix, num_procs=num_procs,
            num_threads=num_threads, preprocessing=preprocessing, dry=dry,
            report_projects=report_projects, reverse=reverse, notes=notes,
            update_interval=update_interval, debugsampling=debugsampling,
            pymolexec=pymolexec, pymolscript=pymolscript, failmode=failmode,
            draw_resscore_charts=draw_resscore_charts,
            draw_resdist_charts=draw_resdist_charts, outfmts=outfmts,
            logger=log)
        #: Python function used to rate a set of scoring weights
        self.function = function
        #: number of points to be sampled for each scoring weight
        self.raster = raster
        #: screening result container
        self.result = TrainingResult(label=label, notes=notes, title=title)
        #: formatted report
        self.report = TrainingReport(
            backends=[_p.get_document(label) for _p in report_projects],
            resdir=self.resdir, result=self.result, pymolexec=pymolexec,
            pymolscript=pymolscript, num_threads=num_threads,
            num_runs=num_runs)
        #: number of training iterations
        self.num_runs = num_runs
        #: list of :class:`TrainingStep` instances
        self.steps = []
        #: arguments for scoring term section
        self.term_kwargs = term_kwargs

    @property
    def current_iteration(self):
        try:
            return self.result.iterations[-1]
        except IndexError:
            return None

    @property
    def current_step(self):
        try:
            return self.current_iteration.steps[-1]
        except (IndexError, AttributeError):
            return None

    def update(self):
        super(Training, self).update()
        self.result.update_status(self.num_runs)
        if self.current_iteration is not None:
            self.current_iteration.update_status(len(self.workers))
        return True

    def _check_references(self):
        for dres in self.result.dress:
            for step in self.steps:
                try:
                    dres.references[step.ind]
                except IndexError:
                    log.fatal(
                        'Missing reference for docking `%s`, step %d (`%s`).',
                        dres.title, step.serial, step.title)
                    return False
        return True

    def _end_iteration(self, status='finished'):
        self.current_iteration.timing.end.set_current()
        self.current_iteration.set_status(status)
        return True

    def _end_step(
            self, termnames, weights, status='finished', outliers=None,
            ratings=None):
        if weights is not None:
            self.current_step.new_weights(termnames, weights)
        self.current_step.timing.end.set_current()
        self.current_step.set_status(status)
        if outliers is not None:
            self.current_step.new_outliers(outliers)
        if ratings is not None:
            self.current_step.new_ratings(ratings)
        return True

    def _setup(self, *args, **kwargs):
        super(Training, self)._setup(*args, **kwargs)
        if self.function is None:
            self.function = _normed_rank
        for dstep in self.dkwargs['docking_steps']:
            dstep.store_decoy_scores = True
            try:
                step_kwargs = self.term_kwargs[dstep.ind]
            except (AttributeError, IndexError):
                step_kwargs = {}
            step = TrainingStep(self, dstep)
            if not step.setup(**step_kwargs):
                return False
            self.steps.append(step)
        if self.resume or self.restore:
            log.info('Resume training `%s`.', self.title)
        else:
            log.info('Start training `%s`.', self.title)
        try:
            if self.resume and self.result.load_json(
                    self.json_filepath, full=True):
                log.info(
                    'Existing results file `%s` read successfully. %d '
                    'training iterations have been found.', self.json_filepath,
                    len(self.result.runs))
                self.result.update_status(self.num_runs)
                if self.result.done:
                    return True
                self.result.timing.end.clear()
        except ValueError as exc:
            log.warning(
                'Can not parse training result file `%s`: %s.',
                self.json_filepath, str(exc))
        except IOError as exc:
            log.info(
                'No existing training result file `%s` found.',
                self.json_filepath)
        if self.current_iteration is not None:
            for w in self.workers:
                w.dkwargs['num_runs'] = self.current_iteration.serial
        return True

    def _shutdown(self, quick=False):
        if self.result.running:
            self.result.set_status('aborted')
        if (
                self.current_iteration is not None and
                self.current_iteration.running):
            self._end_iteration('aborted')
        if (
                self.current_step is not None and
                self.current_step.running):
            self._end_step('aborted', weights=None)
        return super(Training, self)._shutdown(quick=quick)

    def _run(self):
        self.update()
        if self.current_iteration is None:
            self.result.new_iteration()
            log.info('Determine initial scoring weights.')
            self._init_weights()
            self._end_iteration()
        else:
            for step, res in zip(self.steps, self.result.iterations[0].steps):
                num_terms = len(step.termnames)
                norms = [num_terms * _w for _w in res.weights.itervalues()]
                step.set_norms(norms)
        if not self._check_references():
            return False
        while (
                not self.current_iteration or
                self.current_iteration.serial < self.num_runs):
            if not self.current_iteration or self.current_iteration.done:
                self.result.new_iteration()
                for w in self.workers:
                    w.dkwargs['num_runs'] = self.current_iteration.serial
                    w.setup_process()
                log.info(
                    'Run dockings (iteration %d).',
                    self.current_iteration.serial)
                self._run_iteration()
                self.update()
                self._write_results()
            log.info(
                'Optimize weights (iteration %d).',
                self.current_iteration.serial)
            if not self._optimize_weights():
                self._end_iteration(status='failed')
                return False
            for w in self.workers:
                w.dkwargs['resume'] = True
            self._end_iteration()
        return True

    def _init_weights(self):
        for w in self.workers:
            w.dkwargs['dry'] = True
            w.result.set_status('initializing')
        self._run_iteration()
        for w in self.workers:
            w.update()
            w.dkwargs['dry'] = False
            w.setup_process()
        for step in self.steps:
            self.current_iteration.new_step(step.title)
            norms = [
                1. / abs(_t) if _t else 1. for _t in
                step.mean_unweighted_reference_terms()]
            step.set_norms(norms)
            num_terms = len(step.termnames)
            weights = [_norm / num_terms for _norm in norms]
            step.set_weights(weights)
            self._end_step(step.termnames, step.weights)
        return True

    def _optimize_weights(self):
        for step in self.steps:
            self.update()
            self._write_results()
            try:
                stepres = self.current_iteration.steps[step.ind]
                if stepres.done:
                    step.set_weights(stepres.weights.values())
                    continue
            except (AttributeError, IndexError):
                pass
            if self.current_step is None or self.current_step.done:
                self.current_iteration.new_step(step.title)
            log.info(' Optimize step %d (`%s`).', step.serial, step.title)
            t = ScreeningTrainer(
                self.function, self.resdir, self.raster, self.result, step)
            if not t.run():
                log.info(
                    '  Optimization for step %d failed, weights will not be '
                    'changed.', step.serial)
                continue
            if len(t.opt_keys) > 1:
                log.warning(
                    '  Training yielded %d sets of scoring weights, one of '
                    'which will be chosen arbitrarily.', len(t.opt_keys))
            step.set_weights(t.opt_weights[0])
            self._end_step(
                step.termnames, step.weights, outliers=t.outliers[0],
                ratings=t.ratings[0])
        return True

    def _run_iteration(self):
        waiting = self.workers[:]
        while waiting or self._workers_running():
            try:
                while (
                        len(self._workers_running()) < self.num_procs and
                        len(waiting) > 0):
                    d = waiting.pop(0)
                    d.process.start()
                    d.pid = d.process.pid
                    log.info(' Start docking `%s` [%d].', d.title, d.pid)
                if self.update():
                    self._write_results()
                time.sleep(self.update_interval)
            except MurdockInterrupt:
                for w in self.workers:
                    w.stop(signum=signal.SIGINT, wait=False)
                raise
            except MurdockTerminate:
                for w in self.workers:
                    w.stop(signum=signal.SIGTERM, wait=False)
                raise
        for w in self.workers:
            w.stop(wait=True)
        return 'failed' not in (_w.status for _w in self.workers)


class TrainingStep(object):

    def __init__(self, training, docking_step):
        self.training = training
        self.dstep = docking_step
        self.norms = None
        self._terminds = None
        self.exclude_nonzero = None

    @property
    def all_terms(self):
        try:
            return self.dstep.scoring_parms['terms']
        except KeyError:
            return None

    @property
    def all_termnames(self):
        try:
            return [_get_termname(_term) for _term in self.all_terms]
        except TypeError:
            return None

    @property
    def all_weights(self):
        try:
            return [_term['parameters']['weight'] for _term in self.all_terms]
        except TypeError:
            return None

    @property
    def ind(self):
        return self.dstep.ind

    @property
    def serial(self):
        return self.dstep.serial

    @property
    def title(self):
        return self.dstep.title

    @property
    def terms(self):
        terms = self.all_terms
        try:
            return [terms[_ind] for _ind in self._terminds]
        except TypeError:
            return terms

    @property
    def termnames(self):
        try:
            return [_get_termname(_t) for _t in self.terms]
        except TypeError:
            return None

    @property
    def weights(self):
        try:
            return [_term['parameters']['weight'] for _term in self.terms]
        except (KeyError, TypeError):
            return None

    def mean_reference_score(self):
        weights = self.weights
        termnames = self.termnames
        return numpy.mean([
            sum(
                _wgt * _dres.references[self.ind].scoring.unweighted[_tn] for
                _wgt, _tn in zip(weights, termnames)) for _dres in
            self.training.result.dress])

    def mean_unweighted_reference_terms(self):
        return [
            numpy.mean(
                [_dres.references[self.ind].scoring.unweighted[_tn] for _dres
                in self.training.result.dress])
            for _tn in self.termnames]

    def set_norms(self, norms):
        self.norms = norms
        return True

    def set_weights(self, weights):
        if weights is None:
            return False
        log.info(
            ' Set scoring weights for step %d (`%s`):', self.serial,
            self.title)
        for term, wgt in zip(self.terms, weights):
            term['parameters']['weight'] = wgt
        unwgt_terms = self.mean_unweighted_reference_terms()
        for term, wgt, unwgt in zip(self.terms, self.weights, unwgt_terms):
            log.info(
                '   %s: weight = %.3e; mean reference score = %.3f',
                _get_termname(term), wgt, wgt * unwgt)
        return True

    def setup(self, include=None, exclude=None, exclude_if_not_zero=None):
        if self.terms is None:
            log.fatal(
                'Scoring weights for step %d (`%s`) can not be '
                'trained. The the scoring configuration section '
                '`parameters` for the scoring module `%s` does '
                'not include the required list of `terms`).',
                self.serial, self.title,
                self.dstep.scoring_module.__name__)
            return False
        if include is not None and exclude is not None:
            log.fatal(
                'Error in section [training -> terms -> item %d]: the '
                'lists `include` and `exclude` are exclusive.',
                self.serial)
            return False
        elif include is None and exclude is None:
            self._terminds = range(len(self.terms))
        elif include is not None:
            classes = [_t['class'] for _t in include if 'class' in _t]
            names = [_t['name'] for _t in include if 'name' in _t]
            inds = [_t['index'] for _t in include if 'index' in _t]
            self._terminds = [
                _ind for _ind, _t in enumerate(self.terms) if _t['class'] in
                classes or _get_termname(_t) in names or _ind in inds]
        elif exclude is not None:
            classes = [_t['class'] for _t in exclude if 'class' in _t]
            names = [_t['name'] for _t in exclude if 'name' in _t]
            inds = [_t['index'] for _t in exclude if 'index' in _t]
            self._terminds = [
                _ind for _ind, _t in enumerate(self.terms) if _t['class'] not
                in classes and _get_termname(_t) not in names and _ind not in
                inds]
        if exclude_if_not_zero is not None:
            classes = [
                _t['class'] for _t in exclude_if_not_zero if 'class' in _t]
            names = [_t['name'] for _t in exclude_if_not_zero if 'name' in _t]
            inds = [_t['index'] for _t in exclude_if_not_zero if 'index' in _t]
            self.exclude_nonzero = [
                _get_termname(_t) for _t in self.all_terms if _t['class'] in
                classes or _get_termname(_t) in names or _ind in inds]
        return True


class ScreeningTrainer(object):

    def __init__(
            self, function, resdir, raster, screenres, step):
        #: Python function to be optimized (weighted total score as argument)
        self.function = function
        #: result directory
        self.resdir = resdir
        #: number of raster points for weight sampling
        self.raster = raster
        #: :class:`~murdock.results.ScreeningResult` instance
        self.screenres = screenres
        #: :class:`TrainingStep` instance
        self.step = step
        #: list of :class:`DockingTrainer` instances
        self.dtrainers = None
        #: number of sampled weight sets to determine :attr:`opt_keys`
        self.num_sampled = None
        #: optimized weights
        self.opt_keys = None
        #: minimum and maximum rating found during training
        self.rating_range = None
        self._cycles = []

    @property
    def opt_weights(self):
        if self.opt_keys is None:
            return None
        return [self._get_weights(_key) for _key in self.opt_keys]

    @property
    def outliers(self):
        return [
            [_dt.dres for _dt in self._cycles[0].outliers[_opt_key]] if
            _opt_key in self._cycles[0].outliers else [] for _opt_key in
            self.opt_keys]

    @property
    def rating(self):
        try:
            return self.rating_range[0]
        except TypeError:
            return None

    @property
    def ratings(self):
        if not self.dtrainers or not self.opt_keys:
            return None
        return [
            collections.OrderedDict(
                (_dt.dres, _dt.function(_dt.get_reweighted(_weights)))
                for _dt in self.dtrainers) for _weights in self.opt_weights]

    def run(self):
        self.dtrainers = []
        for dres in self.screenres.dress:
            dt = DockingTrainer(dres, self.function, self.raster, self.step)
            if not dt.add_refscore():
                log.error(
                    'Can not determine reference score for `%s`, step %d '
                    '(`%s`).', dres.label, self.step.serial, self.step.title)
                return False
            resdir = os.path.join(self.resdir, 'dockings', dres.label)
            filepath = dt.get_filepath(resdir)
            if not dt.add_file(filepath):
                return False
            self.dtrainers.append(dt)
        cycle_dts = self.dtrainers
        while True:
            cycle = self._add_cycle()
            log.info('  Start cycle %d.', cycle.serial)
            finished = []
            for dt in cycle_dts:
                log.info('   Optimize `%s`:', dt.title)
                if dt.run(keys=self.opt_keys):
                    finished.append(dt)
                else:
                    log.warning('   Optimization failed.')
            if not finished:
                return False
            cycle_dts = finished
            cycle.update(cycle_dts)
            log.info(
                '   Number of rank-optimized weight sets with %d top-ranked / '
                '%d systems: %d', cycle.num_common, len(cycle_dts),
                len(cycle.opt_keys))
            if self.opt_keys is not None and (
                    len(cycle.opt_keys) == len(self.opt_keys)):
                self.opt_keys = cycle.opt_keys
                break
            self.opt_keys = cycle.opt_keys
            if len(self.opt_keys) == 1:
                break
            if not cycle.outliers:
                break
            cycle_dts = cycle.dtrainers_in_outliers
        self.dtrainers = [_dt for _dt in self.dtrainers if _dt.num_decoys]
        for r_func in (numpy.mean, numpy.median, max, min):
            if len(self.opt_keys) <= 1:
                break
            for sr_func in (_normed_rank, _normed_separation):
                if len(self.opt_keys) <= 1:
                    break
                self._optimize_dockings(
                    self.dtrainers, self.opt_keys, r_func, sr_func)
        return True

    def _add_cycle(self):
        ind = len(self._cycles)
        tc = TrainingCycle(ind)
        self._cycles.append(tc)
        return tc

    def _get_weights(self, weight_key):
        return [
            _i * _norm / self.raster for _i, _norm in
            zip(weight_key, self.step.norms)]

    def _optimize_dockings(
            self, dtrainers, keys, rating_func, score_rating_func):
        """Optimize a function value over all :attr:`dockings`.
        """
        log.info(
            '  Optimize weights using the functions: %s and %s',
            rating_func.__name__, score_rating_func.__name__)
        self.opt_keys = []
        self.rating_range = [None, None]
        self.num_sampled = 0
        for inds in keys:
            if not sum(inds):
                continue
            self.num_sampled += 1
            rating = rating_func([
                score_rating_func(_dt.get_reweighted(_dt.get_weights(inds)))
                for _dt in dtrainers])
            if self.rating is None or rating < self.rating:
                self.rating_range[0] = rating
                self.opt_keys = [inds]
            elif rating == self.rating:
                self.opt_keys.append(inds)
            if self.rating_range[1] is None or rating > self.rating_range[1]:
                self.rating_range[1] = rating
        log.info('    Number of sampled weight sets: %d', self.num_sampled)
        log.info('    Number of optimized weight sets: %d', len(self.opt_keys))
        log.info(
            '    Ratings: %.3e to %.3e', self.rating_range[0],
            self.rating_range[1])
        return len(self.opt_keys) > 0


class DockingTrainer(object):

    def __init__(self, dres, function, raster, step):
        #: :class:`~murdock.results.DockingResult` instance
        self.dres = dres
        #: Python function to be optimized (weighted total score as argument)
        self.function = function
        #: number of raster points for weight sampling
        self.raster = raster
        #: :class:`TrainingStep` instance
        self.step = step
        #: number of sampled weight sets to determine :attr:`opt_keys`
        self.num_sampled = None
        #: matrix with unweighted term scores;
        #: the 1st row is the reference, below are the decoys
        #: axis 0 (rows): reference and decoys; axis 1 (columns): terms
        self.scores = None
        #: optimized weights
        self.opt_keys = None
        #: minimum and maximum rating found during training
        self.rating_range = None
        self._exclude_keys = None

    @property
    def exclude_keys(self):
        if self._exclude_keys is None:
            ekeys = []
            for run in self.dres.iter_runs(status='failed'):
                try:
                    if run.steps[self.step.ind].status != 'failed':
                        continue
                except IndexError:
                    continue
                iteration = self.step.training.result.iterations[run.ind]
                weights = iteration.steps[self.step.ind].weights.values()
                part_key = self._get_key(weights)[:-1]
                ekeys.append(part_key)
            self._exclude_keys = set(ekeys)
            if self._exclude_keys:
                log.info(
                    '    Exclude %d weight sets yielding failed runs.',
                    len(self._exclude_keys))
        return self._exclude_keys

    @property
    def num_decoys(self):
        if self.scores is None:
            return 0
        return self.scores.shape[0] - 1

    @property
    def opt_weights(self):
        return [self.get_weights(_key) for _key in self.opt_keys]

    @property
    def rating(self):
        try:
            return self.rating_range[0]
        except TypeError:
            return None

    @property
    def title(self):
        return self.dres.title

    def add_file(self, filepath):
        if self.scores is None:
            raise TrainingError(
                'Reference scores must be added first. Then, decoy files can '
                'be added.')
        try:
            runs = murdock.misc.load_ordered_json(filepath)['runs']
        except (IOError, KeyError, ValueError) as exc:
            log.warning('Can not parse decoy file `%s`: %s', filepath, exc)
            return False
        exclude = lambda _tvals, _i: True in (
            _tvals[_xt][_i] != 0 for _xt in self.step.exclude_nonzero)
        num_runs = len(self.dres.runs)
        for run in runs[:num_runs]:
            try:
                tvals = run[self.step.title]['terms']['unweighted']
            except KeyError:
                continue
            if self.step.exclude_nonzero is None:
                scores = [tvals[_tn] for _tn in self.step.termnames]
            else:
                scores = [[
                    _t for _i, _t in enumerate(tvals[_tn]) if not
                    exclude(tvals, _i)] for _tn in self.step.termnames]
            self.scores = numpy.concatenate(
                (self.scores, numpy.matrix(scores).T))
        return True

    def add_refscore(self):
        try:
            return self.add_score(self.dres.references[self.step.ind].scoring)
        except (AttributeError, IndexError):
            return False

    def add_score(self, scoring):
        try:
            scores = [scoring.unweighted[_tn] for _tn in self.step.termnames]
        except (AttributeError, IndexError):
            return False
        if self.scores is None:
            self.scores = numpy.matrix(scores)
        else:
            self.scores.concatenate(scores)
        return True

    def get_filepath(self, resdir):
        return os.path.join(resdir, '%s-decoys.json' % self.dres.label)

    def get_reweighted(self, weights):
        return numpy.dot(self.scores, numpy.matrix(weights).T)

    def get_weights(self, weight_key):
        return [
            _i * _norm / self.raster for _i, _norm in
            zip(weight_key, self.step.norms)]

    def run(self, keys=None):
        log.info('    Number of decoys: %d', self.num_decoys)
        if not self.num_decoys:
            return False
        self.opt_keys = []
        self.rating_range = [None, None]
        self.num_sampled = 0
        for inds in self._iterate_keys(keys):
            self.num_sampled += 1
            scores = self.get_reweighted(self.get_weights(inds))
            rating = self.function(scores)
            if self.rating is None or rating < self.rating:
                self.rating_range[0] = rating
                self.opt_keys = [inds]
            elif self.rating == rating:
                self.opt_keys.append(inds)
            if self.rating_range[1] is None or rating > self.rating_range[1]:
                self.rating_range[1] = rating
        log.info('    Number of sampled weight sets: %d', self.num_sampled)
        log.info('    Number of optimized weight sets: %d', len(self.opt_keys))
        log.info(
            '    Ratings: %.3e to %.3e', self.rating_range[0],
            self.rating_range[1])
        return len(self.opt_keys) > 0

    def _get_key(self, weights):
        return tuple([
            int(round(_w / _norm * self.raster)) for _w, _norm in
            zip(weights, self.step.norms)])

    def _iterate_keys(self, keys=None):
        if keys is not None:
            for key in keys:
                part_key = key[:-1]
                if part_key not in self.exclude_keys:
                    yield key
        else:
            n = len(self.step.termnames) - 1
            for part_key in itertools.product(
                    *(tuple(xrange(self.raster)) for _ in xrange(n))):
                i = self.raster - sum(part_key) - 1
                if i >= 0 and part_key not in self.exclude_keys:
                    yield part_key + (i, )


class TrainingCycle(object):

    def __init__(self, ind):
        self.ind = ind
        self.common = {}
        self.outliers = {}

    @property
    def dtrainers_in_common(self):
        return set(_dt for _dts in self.common.itervalues() for _dt in _dts)

    @property
    def dtrainers_in_outliers(self):
        return set(_dt for _dts in self.outliers.itervalues() for _dt in _dts)

    @property
    def num_common(self):
        return len(self.common.values()[0])

    @property
    def num_outliers(self):
        return len(self.outliers.values()[0])

    @property
    def num_total(self):
        return self.num_common + self.num_outliers

    @property
    def serial(self):
        return self.ind + 1

    @property
    def opt_keys(self):
        return self.common.keys()

    def update(self, dtrainers):
        self.common = {}
        self.outliers = {}
        for dt in dtrainers:
            for opt_key in dt.opt_keys:
                try:
                    self.common[opt_key].append(dt)
                except KeyError:
                    self.common[opt_key] = [dt]
        max_len = max(len(_c) for _c in self.common.itervalues())
        self.common = {
            _wkey: _dts for _wkey, _dts in self.common.iteritems() if
            len(_dts) == max_len}
        for opt_key, common_dts in self.common.iteritems():
            for dt in dtrainers:
                if dt not in common_dts:
                    try:
                        self.outliers[opt_key].append(dt)
                    except KeyError:
                        self.outliers[opt_key] = [dt]
        return True


class ConfigDeclaration(murdock.runner.screening.ConfigDeclaration):

    def training(self):
        """Configuration options for a training setup:

            - "title":
                project title used in formatted results `(dtype=str,
                required=False)`

            - "label":
                project label used in result filenames (no special characters)
                `(dtype=str, required=False)`

            - "user":
                program user / scientist responsible for the experiment
                `(dtype=str, required=False)`

            - "number_of_runs":
                number of independent docking runs performed for each docking
                `(dtype=int, default=1)`

            - "fail-mode":
                what to do if a single docking run fails
                    * `abort` -> abort the docking (skip remaining runs)
                    * `continue` -> continue with the next run (default)
                    * `repeat` -> repeat the failed run

            - "preprocessing":
                options for the
                :meth:`~murdock.runner.docking.ConfigDeclaration.preprocessing`
                of molecular structures before a docking run `(dtype=dict,
                required=False)`

            - "steps":
                list of docking
                :meth:`~murdock.runner.docking.ConfigDeclaration.steps` to be
                performed consecutively within a docking run `(dtype=list,
                required=True)`

            - "terms":
                list of dictionaries - one for each docking step - defining how
                scoring terms to be trained are selected; if not given, all
                scoring terms are trained `(dtype=list, required=False)`

            - "raster":
                number of points to be sampled for each scoring weight
                `(dtype=int, default=10)`

            - "description":
                a short description of the training setup `(dtype=str,
                required=False)`

            - "input_data":
                list of (molecular)
                :meth:`~murdock.runner.docking.ConfigDeclaration.input_data`
                for each docking `(dtype=list, required=True)`

        """
        Option = murdock.config.ConfigOption
        opt = self.screening()
        opt.append(Option(
            name='terms', dtype=list, required=False, default=[],
            description='list of dictionaries containing scoring terms to be '
            'trained for each step'))
        opt.append(Option(
            name='raster', dtype=int_gt_zero, required=True, default=10,
            description='number of points to be sampled for each scoring '
            'weight'))
        return opt

    def terms(self):
        """Configuration options for the selection of scoring terms:

            - "include":
                list of scoring term names to include in the training
                `(dtype=list, required=False)`

            - "exclude":
                list of scoring term names to exclude in the training
                `(dtype=list, required=False)`

            - "exclude_if_not_zero":
                list of scoring term names, which exclude decoys if not zero
                `(dtype=list, required=False)`

        """
        Option = murdock.config.ConfigOption
        opt = self.get_default_options()
        opt.append(Option(
            name='include', dtype=list, required=False, description='list of '
            'scoring terms to include in the training'))
        opt.append(Option(
            name='exclude', dtype=list, required=False, description='list of '
            'scoring terms to include in the training'))
        opt.append(Option(
            name='exclude_if_not_zero', dtype=list, validate=False,
            description='list of scoring terms, which exclude decoys if not '
            'zero'))
        return opt

    def term(self):
        """Configuration option for a scoring term:

            - "class":
                scoring term class name `(dtype=str, required=False)`

            - "name":
                scoring term name `(dtype=str, required=False)`

            - "index":
                scoring term index `(dtype=int, required=False)`

        """
        Option = murdock.config.ConfigOption
        opt = self.get_default_options()
        opt.append(Option(
            name='class', dtype=basestring, required=False,
            description='scoring term class name'))
        opt.append(Option(
            name='name', dtype=basestring, required=False,
            description='scoring term name'))
        opt.append(Option(
            name='label', dtype=basestring, required=False,
            description='scoring term label (not implemented!)'))
        opt.append(Option(
            name='index', dtype=int_ge_zero, required=False,
            description='scoring term class name'))
        return opt

    def include(self):
        """Configuration options defining a scoring term to be trained.

        Refer to :meth:`term`.

        """
        return self.term()

    def exclude(self):
        """Configuration options defining a scoring term not to be trained.

        Refer to :meth:`term`.

        """
        return self.term()

    def exclude_if_not_zero(self):
        """Configuration options defining a scoring term to exclude decoys.

        Refer to :meth:`term`. If a decoy has a term contribution from this
        scoring term, it is excluded.

        """
        return self.term()


def _get_termname(term):
    try:
        return term['name']
    except KeyError:
        pass
    try:
        return term['class']
    except KeyError:
        pass
    return None


def _normed_rank(x):
    try:
        return sum(1 for _i in x[1:] if _i < x[0]) / (len(x) - 1.)
    except ZeroDivisionError:
        return 0.


def _normed_separation(x):
    return (x[0] - numpy.mean(x[1:])) / abs(x[0])
