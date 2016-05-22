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
Module :mod:`murdock.runner.screening`
--------------------------------------

Provides the class :class:`Screening` used to initialize and run a screening
setup. Multiple :class:`~murdock.runner.docking.Docking` instances are spawned
using the class :class:`ParallelScreeningWorker`.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import multiprocessing
import os
import signal
import time

import murdock.config
import murdock.runner.docking
from murdock.report import ScreeningReport
from murdock.results import DockingResult, ScreeningResult
from murdock.logger import Logger
from murdock.misc import int_gt_zero
from murdock.runner.runner import MurdockInterrupt, MurdockTerminate, Runner


log = Logger(name='screening').logger


class ScreeningError(Exception):
    pass


class Screening(Runner):
    """A screening class.

    The class is used to sequentially perform docking runs on all
    receptor-ligand sets given as input using the same setup (specified by a
    list of :attr:`docking_steps`.

    """

    def __init__(
            self, label, title, moldata, docking_steps, resdir='.',
            restore=False, resume=False, num_runs=1, docked_suffix='',
            result_suffix='-results', num_procs=1, num_threads=None,
            preprocessing=None, dry=False, report_projects=None, reverse=False,
            notes=None, update_interval=1, debugsampling=False,
            pymolexec=None, pymolscript=None, failmode='continue',
            draw_resscore_charts=False, draw_resdist_charts=False,
            outfmts=None, logger=None):
        if logger is not None:
            global log
            log = logger
        super(Screening, self).__init__(
            log, moldata, resdir=resdir, restore=restore, resume=resume,
            result_suffix=result_suffix)
        #: :class:`ParallelScreeningWorker` instances (one per docking)
        self.workers = []
        #: number of parallel processes used
        self.num_procs = num_procs
        #: idle time before results are updated (optionally Sphinx-built)
        self.update_interval = update_interval
        #: :class:`murdock.runner.docking.Docking` arguments
        self.dkwargs = {
            'docking_steps': docking_steps, 'docked_suffix': docked_suffix,
            'result_suffix': result_suffix, 'restore': restore,
            'resume': self.resume, 'num_runs': num_runs,
            'preprocessing': preprocessing, 'dry': dry,
            'report_projects': report_projects, 'screening_pid': os.getpid(),
            'debugsampling': debugsampling, 'pymolexec': pymolexec,
            'pymolscript': pymolscript, 'num_threads': num_threads,
            'failmode': failmode, 'draw_resscore_charts': draw_resscore_charts,
            'draw_resdist_charts': draw_resdist_charts, 'outfmts': outfmts}
        #: screening result container
        self.result = ScreeningResult(label=label, notes=notes, title=title)
        #: formatted report
        self.report = ScreeningReport(
            backends=[_p.get_document(label) for _p in report_projects],
            resdir=self.resdir, result=self.result, pymolexec=pymolexec,
            pymolscript=pymolscript, num_threads=num_threads,
            num_runs=num_runs)
        if reverse:
            self.moldata = moldata[::-1]

    def update(self):
        changed = False
        for worker in self.workers:
            if worker.update():
                log.info(
                    ' Docking `%s` changed status to `%s`.', worker.title,
                    worker.status)
                changed = True
        if len(self.result.dress) != len(self.workers) or changed:
            self.result.clear_dress()
            for worker in self.workers:
                self.result.add_dres(worker.result)
        return changed

    def _run(self):
        if self.resume:
            log.info('Resume screening `%s`.', self.title)
        else:
            log.info('Start screening `%s`.', self.title)
        if self.resume or self.restore:
            try:
                self.result.load_json(self.json_filepath)
            except ValueError as exc:
                log.warning(
                    'Can not parse screening result file `%s`: %s.',
                    self.json_filepath, str(exc))
            except IOError as exc:
                log.info(
                    'No existing screening result file `%s` found.',
                    self.json_filepath)
            else:
                log.info(
                    'Timing information from existing result file `%s` will '
                    'be used.', self.json_filepath)
        self.update()
        self._write_results()
        waiting = self.workers[:]
        while waiting or self._workers_running():
            try:
                while (
                        len(self._workers_running()) < self.num_procs and
                        len(waiting) > 0):
                    d = waiting.pop(0)
                    d.process.start()
                    d.pid = d.process.pid
                    log.info('Start docking `%s` [%d].', d.title, d.pid)
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
        return True

    def _setup(self, file_level=logging.INFO, console_level=None):
        """Set up screening, fill :attr:`workers`.
        """
        if file_level is not None:
            log.logger.add_file_handler(
                level=file_level, logdir=self.resdir,
                filename='%s.log' % self.label)
        if console_level is not None:
            log.logger.add_console_handler(level=console_level)
        for dockdat in self.moldata:
            dkwargs = self.dkwargs.copy()
            dkwargs['label'] = dockdat['label']
            dkwargs['title'] = dockdat['title']
            dkwargs['moldata'] = {
                'receptor': dockdat['receptor'], 'ligands': dockdat['ligands']}
            dkwargs['notes'] = dockdat['notes'] if 'notes' in dockdat else None
            dkwargs['resdir'] = os.path.join(
                self.resdir, 'dockings', dockdat['label'])
            w = ParallelScreeningWorker(
                sres=self.result, log_file_level=file_level, dkwargs=dkwargs)
            self.workers.append(w)
        return True

    def _shutdown(self, quick=False):
        """Do final chores before the sun goes down.
        """
        try:
            self.result.timing.end.set_current()
            if quick:
                log.info('Shut down (quick).')
                for worker in self.workers:
                    worker.stop(
                        signum=signal.SIGTERM, timeout=1, kill=True)
                    if worker.result.running:
                        worker.result.set_status('aborted')
                self.update_full = False
            else:
                log.info('Shut down.')
                for worker in self.workers:
                    worker.stop()
                self.update()
                self.update_full = True
            self._write_results()
        except (MurdockInterrupt, MurdockTerminate):
            return self._shutdown(quick=True)
        for worker in self.workers:
            worker.stop()
        log.info('%s done.', self.__class__.__name__)
        return True

    def _workers_running(self):
        return [_w for _w in self.workers if _w.alive]


class ParallelScreeningWorker(object):

    def __init__(self, sres, dkwargs, log_file_level=logging.INFO):
        self.dkwargs = dkwargs
        self.process = None
        self.pid = None
        self.result = DockingResult(sres=sres)
        self.result.from_json(dkwargs)
        self.log_file_level = log_file_level
        self.resdir = self.dkwargs['resdir']
        self.log_filepath = os.path.join(self.resdir, '%s.log' % self.label)
        self.setup_process()

    @property
    def alive(self):
        return self.pid is not None and self.process.is_alive()

    @property
    def label(self):
        return self.result.label

    @property
    def json_filepath(self):
        return os.path.join(self.resdir, '%s%s.json' % (
            self.label, self.dkwargs['result_suffix']))

    @property
    def status(self):
        return self.result.status

    @property
    def title(self):
        return self.result.title

    def run(self, dkwargs):
        self.pid = self.process.pid
        for p in dkwargs['report_projects']:
            p.build_exec = None
        docking = murdock.runner.docking.Docking(**dkwargs)
        try:
            docking.run(file_level=None, full_log=False)
        finally:
            logging.shutdown()

    def setup_process(self):
        self.process = multiprocessing.Process(
            target=self.run, args=(self.dkwargs, ))
        self.pid = None
        return True

    def stop(self, signum=None, wait=True, timeout=None, kill=False):
        if not self.alive:
            return True
        if signum is not None:
            os.kill(self.pid, signum)
        if wait:
            self.process.join(timeout=timeout)
            if self.process.is_alive() and kill:
                log.debug(
                    'Docking process %d (`%s`) still alive after `%d` second '
                    'timeout. Send kill signal.', self.pid, self.title,
                    timeout)
                os.kill(self.pid, signal.SIGKILL)
                self.result.set_status('KILLED')
        return True

    def update(self):
        if self.status == 'KILLED':
            return False
        old_status = self.status
        alive = self.alive
        try:
            self.result.load_json(self.json_filepath, done=False)
        except (IOError, ValueError):
            return False
        if self.pid is None:
            self.result.set_status('not started')
        elif alive and not self.result.running:
            self.result.set_status(old_status)
        elif not alive and self.result.running:
            log.fatal(
                'Docking process %d (`%s`) has been found dead with status '
                '`%s`. The process was probably killed from the outside.',
                self.pid, self.title, self.status)
            self.result.set_status('KILLED')
            return True
        if self.status == old_status:
            return False
        if self.status == 'CRASHED':
            log.fatal(
                'Docking `%s` crashed. Check docking log file `%s`.',
                self.title, self.log_filepath)
        return True


class ConfigDeclaration(murdock.runner.docking.ConfigDeclaration):

    def screening(self):
        """Configuration options for a screening setup:

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

            - "description":
                a short description of the screening setup `(dtype=str,
                required=False)`

            - "input_data":
                list of (molecular)
                :meth:`~murdock.runner.docking.ConfigDeclaration.input_data`
                for each docking `(dtype=list, required=True)`

        """
        Option = murdock.config.ConfigOption
        opt = self.get_default_options()
        opt.append(Option(
            name='title', dtype=basestring, description='project title used '
            'in formatted results', required=False))
        opt.append(Option(
            name='label', dtype=basestring, description='project label used '
            'in result filenames', required=False))
        opt.append(Option(
            name='user', dtype=basestring, description='program user / '
            'scientist responsible for the experiment', required=False))
        opt.append(Option(
            name='input_data', dtype=list, description='list of (molecular) '
            'input data to be included in the screening'))
        opt.append(Option(
            name='number_of_runs', dtype=int_gt_zero, default=1,
            description='number of independent docking runs per input '
            'complex'))
        opt.append(Option(
            name='fail-mode', dtype=basestring, description='what to do if a '
            'single docking run fails', default='continue',
            choices=('abort', 'continue', 'repeat')))
        opt.append(Option(
            name='preprocessing', dtype=dict, required=False,
            description='information on python function used to prepare or '
            'correct input structures'))
        opt.append(Option(
            name='steps', dtype=list, description='main parameter section '
            'defining docking workflow'))
        opt.append(Option(
            name='description', dtype=basestring, description='short '
            'description of the screening setup', required=False))
        return opt

    def input_data(self):
        """Configuration options for external input data:

            - "title":
                title used in formatted results `(dtype=str, required=True)`

            - "label":
                label used in result filenames (no special characters)
                `(dtype=str, required=False)`

            - "receptor":
                options for the input
                :meth:`~murdock.runner.docking.ConfigDeclaration.receptor`,
                i.e. the docking target `(dtype=dict, required=True)`

            - "ligands":
                list of input
                :meth:`~murdock.runner.docking.ConfigDeclaration.ligands`,
                which are docked onto the receptor simultaneously `(dtype=list,
                required=True)`

            - "tags":
                a list of tag strings for classification, sorting, etc. of
                input and output data `(dtype=str, required=False)`

        """
        Option = murdock.config.ConfigOption
        opt = self.get_default_options()
        opt.append(Option(
            name='receptor', dtype=dict, description='dictionary containing '
            'receptor information'))
        opt.append(Option(
            name='ligands', dtype=list, description='list containing ligand '
            'information'))
        opt.append(Option(
            name='label', dtype=basestring, description='label used in result '
            'filenames', required=False))
        opt.append(Option(
            name='title', dtype=basestring, description='title used in '
            'formatted results'))
        opt.append(Option(
            name='tags', dtype=list, description='list of tag strings',
            required=False, validate=False))
        return opt
