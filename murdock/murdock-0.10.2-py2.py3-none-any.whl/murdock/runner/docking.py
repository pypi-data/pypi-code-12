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
Module :mod:`murdock.runner.docking`
------------------------------------

Provides the classes :class:`Docking` and :class:`DockingStep` used to
initialize and run a docking setup.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future.utils import viewitems

import collections
import logging
import os
import shutil
import traceback

import scipy.constants

import murdock.config
import murdock.math
import murdock.misc
import murdock.moldata
from murdock.report import DockingReport
from murdock.results import DockingResult
from murdock.pymol import PyMOLVideo
from murdock.logger import Logger
import murdock.molstruct
from murdock.runner.runner import MurdockInterrupt, MurdockTerminate, Runner
from murdock.transforms import Rotation, Translation
import murdock.tree


log = Logger(name='docking').logger


class Docking(Runner):
    """A class to represent a full docking protocol on a single system.

    The class holds all information needed for a docking run. It can be used
    to perform docking on a single system. Alternatively, it is set up
    automatically in the context of a :mod:`murdock.runner.screening`.

    """
    def __init__(
            self, label, title, moldata, docking_steps, resdir='.',
            restore=False, resume=False, num_runs=1, docked_suffix='',
            result_suffix='-results', preprocessing=None, dry=False,
            screening_pid=None, report_projects=None, notes=None,
            debugsampling=False, pymolexec=None, pymolscript=None,
            num_threads=None, failmode='continue', draw_resscore_charts=False,
            draw_resdist_charts=False, outfmts=None, logger=None):
        if logger is not None:
            global log
            log = logger
        super(Docking, self).__init__(
            log, moldata, resdir=resdir, restore=restore, resume=resume,
            result_suffix=result_suffix)
        #: suffix for docked structures
        self.docked_suffix = docked_suffix
        #: list of `DockingStep` instances to be run
        self.dsteps = []
        for dstep in docking_steps:
            self._add_dstep(dstep)
            dstep.init_extvideo()
        #: ligand :class:~murdock.molstruct.MolecularStructure` instances
        self.ligands = []
        #: number of identical docking runs performed
        self.num_runs = num_runs
        #: receptor :class:~murdock.molstruct.MolecularStructure` instance
        self.receptor = None
        #: input :attr:`~murdock.search.Search.root` node (used as
        #: template)
        self.input_root = None
        #: reference :attr:`~murdock.search.Search.root` node (used for
        #: comparison)
        self.ref_root = None
        #: dictionary holding a module, a function and its arguments for the
        #: preprocessing of input structures
        self.preprocessing = preprocessing
        #: whether to only score the input structure and skip the whole docking
        self.dry = dry
        #: process id of parent screening process (to check if it is alive)
        self.screening_pid = screening_pid
        #: whether to write a :attr:`murdock.transforms.Transformation.history`
        self.debugsampling = debugsampling
        #: what to do if a docking run fails (`continue`, `abort` or `repeat`)
        self.failmode = failmode
        #: list of output formats for docked structures (e.g. ['pdb', 'mol2'])
        self.outfmts = outfmts
        #: docking result container
        self.result = DockingResult(label=label, notes=notes, title=title)
        #: formatted report
        self.report = DockingReport(
            backends=[_p.get_document(label) for _p in report_projects],
            resdir=self.resdir, result=self.result,
            headline=(None if screening_pid is None else title),
            pymolexec=pymolexec, pymolscript=pymolscript,
            num_threads=num_threads, num_runs=num_runs,
            draw_resscore_charts=draw_resscore_charts,
            draw_resdist_charts=draw_resdist_charts,
            search_filepath=self.get_search_filepath())

    @property
    def current_run(self):
        try:
            return self.result.runs[-1]
        except IndexError:
            return None

    @property
    def current_step(self):
        try:
            return self.current_run.steps[-1]
        except (AttributeError, IndexError):
            return None

    def docked_filepath(self, molstruct, ext=None):
        """Return the filepath for docked structures.
        """
        if ext is None:
            ext = os.path.splitext(
                os.path.basename(molstruct.source.filepath))[1]
        dockdir = os.path.join(self.resdir, 'docked')
        if not os.path.exists(dockdir):
            os.makedirs(dockdir)
        filename = '%s%s-run%05d-step%02d-%s%s' % (
            self.label, self.docked_suffix,
            self.current_run.serial, self.current_step.serial, molstruct.label,
            ext)
        filepath = os.path.join(dockdir, filename)
        return filepath

    def get_search_filepath(self, label='search'):
        return get_search_filepath(self.resdir, self.label, label)

    def molstructs(self):
        """Iterate over all ligands and the receptor.
        """
        yield self.receptor
        for lig in self.ligands:
            yield lig

    def update(self):
        if self.update_full:
            log.info('Update result files.')
            self._create_clustering()
        self._write_results()
        return True

    def _add_docked(self, docked_root, scoring):
        """Add docked :class:`~murdock.tree.Node` to results
        """
        step = self.current_step
        step.new_scoring_result(scoring)
        if self.ref_root:
            measures = (
                ('RMSD', murdock.math.atoms_rmsd),
                ('RMSATD', murdock.math.atoms_rmsatd))
            for mlabel, mfunc in measures:
                qdata = _dist_to_ref(mfunc, docked_root, self.ref_root)
                step.new_quality(mlabel, qdata)
        resdists = _residue_distances(scoring.root)
        if resdists:
            step.new_residue_analysis('distances', resdists)
        resscores = _residue_scores(scoring)
        if resscores:
            step.new_residue_analysis('scores', resscores)
        fmt_rotbonds = collections.OrderedDict()
        for child in docked_root.children:
            rotbonds = [_bond for _bond in child.bonds if _bond.rotatable]
            if not rotbonds:
                continue
            mol = murdock.misc.get_source(
                child, src_type=murdock.molstruct.MolecularStructure)
            fmt_rotbonds[mol] = _formatted_rotbonds(rotbonds)
        if fmt_rotbonds:
            step.new_rotbond_analysis(fmt_rotbonds)
        if self.debugsampling:
            sampling = _formatted_sampling(docked_root)
            step.new_sampling_analysis(sampling)
        return True

    def _add_dstep(self, dstep):
        """Add a :class:`DockingStep` to :attr:`dsteps`.
        """
        dstep.docking = self
        self.dsteps.append(dstep)
        return True

    def _add_references(self):
        """Add reference structure infos to results file.
        """
        if not self._has_references():
            return True
        root = self.ref_root.deepcopy()
        log.info('Reference scores:')
        for ds in self.dsteps:
            log.info('  Step %d (`%s`):', ds.serial, ds.title)
            if not ds.setup_transforms(root):
                log.fatal(
                    '    Error in setup of transformations for reference.')
                return False
            scoring = ds.get_scoring(root=root)
            if not scoring:
                log.fatal(
                    '    Error in setup of scoring function for reference.')
                return False
            residues = {}
            resscores = _residue_scores(scoring)
            if resscores:
                residues['scores'] = resscores
            resdists = _residue_distances(scoring.root)
            if resdists:
                residues['distances'] = resdists
            rotbonds = ds.get_formatted_rotbonds(root)
            if self.debugsampling:
                for tf in (
                        _d for _node in root.descendants() for _d in
                        _node.transforms):
                    tf.history.append(tf.get_fmt_state())
                sampling = _formatted_sampling(root)
            else:
                sampling = None
            ref = self.result.new_reference(
                ds.ind, ds.title, scoring, rotbonds=rotbonds,
                residues=residues, sampling=sampling)
            for term in scoring.terms:
                log.info('    %s: %.3e', term.name, term.weighted())
            ref.timing.end.set_current()
        return True

    def _add_unbonded(self):
        log.info('Unbonded scores (used as offset for all reported scores):')
        for ds in self.dsteps:
            log.info('  Step %d (`%s`):', ds.serial, ds.title)
            scoring = ds.get_unbonded_scoring()
            rotbonds = ds.get_formatted_rotbonds(self.input_root)
            for term in scoring.terms:
                log.info('    %s: %.5e', term.name, term.weighted())
            ub = self.result.new_unbonded(ds.ind, ds.title, scoring, rotbonds)
            ub.timing.end.set_current()
        return True

    def _center_dynamic(self, root):
        """Center dynamic :attr:`ligands` onto :attr:`receptor`.
        """
        static_center = murdock.molstruct.get_center(self.receptor.atoms())
        for node in root.children[1:]:
            if not node.static:
                murdock.molstruct.set_center(node.atoms, static_center)
        return True

    def _create_clustering(self, measure='RMSD', step=None):
        if step is None:
            step = self.current_step
        try:
            samples = self.result.steps[step.ind].samples
        except (AttributeError, IndexError):
            return False
        # Set algorithm and parameters.
        epsilons = range(2, 9)
        min_num_clusters = 2
        min_point_fract = 0.1
        algorithm_func = murdock.misc.cluster_structs_dbscan
        algorithm_name = 'DBSCAN'
        if measure == 'RMSD':
            func = murdock.math.atoms_rmsd
        elif measure == 'RMSATD':
            func = murdock.math.atoms_rmsatd
        else:
            raise ValueError(
                'Unknown clustering method `%s` (use `RMSD` or `RMSATD`).' %
                measure)
        if not self.result.clustering:
            if step.ind == 0:
                method = collections.OrderedDict()
                method['algorithm'] = algorithm_name
                method['measure'] = measure
                self.result.new_clustering(method=method)
            else:
                # If clustering for previous docking steps is missing, call
                # this method recursively (occurs in resume/restore mode).
                self._create_clustering(
                    measure=measure, step=self.current_run.steps[step.ind - 1])
        cres = self.result.clustering.new_step(step.ind, step.title)
        # Perform clustering.
        structs = []
        indices = {}
        for i, sample in enumerate(samples):
            filepaths = [
                os.path.abspath(os.path.join(self.resdir, _fp)) for _fp in
                sample.filepaths.values()]
            parse = murdock.moldata.get_molstruct
            stepstructs = [
                parse(_fp, infolog=False) for _fp in filepaths]
            err_fps = [
                _fp for _fp, _ss in zip(filepaths, stepstructs) if not _ss]
            if err_fps:
                log.error(
                    'Files could not be read for clustering: %s',
                    ', '.join(err_fps))
                return False
            for ss in stepstructs:
                indices[ss] = i
            structs.append(stepstructs)
        if len(structs) < 3:
            return True
        # Set dynamic parameters for the DBSCAN clustering algorithm.
        if min_point_fract is not None:
            minpoints = [max(2, round(min_point_fract * len(structs)))]
        else:
            minpoints = [2]
        clusterparms = [[_e, _m] for _e in epsilons for _m in minpoints]
        clusters = None
        for eps, minpts in clusterparms:
            newclusters = algorithm_func(
                [_ls for _s in structs for _ls in _s], epsilon=eps,
                minpoints=minpts, func=func)
            if clusters is None or len(newclusters) > len(clusters):
                clusters = newclusters
                opt_eps, opt_minpts = eps, minpts
            if len(clusters) >= min_num_clusters:
                break
        if not clusters:
            return True
        log.info(
            'Cluster %d structures from step %d with %s < %.1f A: [%s]',
            len(structs), step.serial, measure, opt_eps,
            ', '.join(['%d' % len(_c) for _c in clusters]))
        cres.parameters['max_distance'] = opt_eps
        cres.parameters['min_points'] = opt_minpts
        cres.parameters['min_num_clusters'] = min_num_clusters
        for cstructs in clusters:
            cinds = set([indices[_s] for _s in cstructs])
            csamples = [samples[_i] for _i in cinds]
            cres.new_cluster(step.title, csamples)
        return True

    def _create_tree(self, ref=False):
        """Create a :mod:`~murdock.tree` from all :meth:`molstructs`.
        """
        if ref:
            name = 'ref_system'
        else:
            name = 'system'
        root = murdock.tree.Node(name=name)
        for i, molstruct in enumerate(self.molstructs()):
            node = murdock.tree.Node(
                name=molstruct.label, parent=root, object_serial=i)
            if ref:
                node.source = molstruct.reference
            else:
                node.source = molstruct
            node.add_atoms(node.source.atoms())
            for bond in node.source.bonds():
                node.add_bond(bond)
            if molstruct is not self.receptor:
                node.set_as_dynamic()
        if ref:
            self.ref_root = root.deepcopy()
        else:
            self.input_root = root.deepcopy()
        for input_bond, bond in zip(self.input_root.bonds, root.bonds):
            bond.unbonded = input_bond
        if not ref and self._has_references():
            self._create_tree(ref=True)
        return True

    def _end_run(self, status):
        if self.current_run is None:
            return False
        self.current_run.timing.end.set_current()
        self.current_run.set_status(status)
        return True

    def _end_step(self, status):
        if self.current_step is None:
            return False
        self.current_step.timing.end.set_current()
        self.current_step.set_status(status)
        if status == 'finished':
            self.result.add_step(self.current_step)
        return True

    def _has_references(self):
        return None not in (_mol.reference for _mol in self.molstructs())

    def _parent_process_alive(self):
        try:
            os.kill(self.screening_pid, 0)
        except OSError:
            return False
        return True

    def _parse_input(self):
        """Parse :attr:`moldata` and fill :attr:`ligands` and :attr:`receptor`.
        """
        inputdir = os.path.join(self.resdir, 'input')
        # Create input directory.
        if not os.path.exists(inputdir):
            os.makedirs(inputdir)
        # Copy residuals to `input` directory.
        if 'residuals_filepath' in self.moldata['receptor']:
            filepath = self.moldata['receptor']['residuals_filepath']
            ext = os.path.splitext(filepath)[1]
            trg_filename = '%s-residuals%s' % (
                self.moldata['receptor']['label'], ext)
            trg_filepath = os.path.join(inputdir, trg_filename)
            if not os.path.exists(trg_filepath):
                shutil.copyfile(filepath, trg_filepath)
            self.moldata['receptor']['residuals_filepath'] = os.path.join(
                'input', trg_filename)
        # Parse ligands.
        for ligand in self.moldata['ligands']:
            molstruct = self._parse_molstruct(ligand)
            if not molstruct:
                return False
            self.ligands.append(molstruct)
        # Parse receptor.
        molstruct = self._parse_molstruct(self.moldata['receptor'])
        if not molstruct:
            return False
        self.receptor = molstruct
        if self.receptor.reference is None:
            log.info(
                'No reference structure for the receptor was given. The input '
                'structure will be used as reference instead.')
            self.receptor.reference = molstruct
        num_rec_atoms = len(self.receptor.atoms())
        num_lig_atoms = sum(len(_lig.atoms()) for _lig in self.ligands)
        if num_rec_atoms < num_lig_atoms:
            log.warning(
                'There are less receptor atoms (%d) than ligand atoms (%d).',
                num_rec_atoms, num_lig_atoms)
        return True

    def _parse_molstruct(self, moldata, ref=False):
        """Parse molecular structure (and its reference) from input file.

        """
        inputdir = os.path.join(self.resdir, 'input')
        label = moldata['label']
        # Create filepaths in `input` directory.
        if ref:
            key = 'ref_filepath'
            suffix = '-ref'
        else:
            key = 'filepath'
            suffix = ''
        ext = os.path.splitext(moldata[key])[1]
        trg_filename = '%s%s%s' % (label, suffix, ext)
        trg_filepath = os.path.join(inputdir, trg_filename)
        # Determine filepaths to be used.
        if (self.resume or self.restore) and os.path.exists(trg_filepath):
            filepath = trg_filepath
        else:
            filepath = moldata[key]
        # Parse structures.
        molstruct = murdock.moldata.get_molstruct(filepath=filepath)
        if not molstruct:
            log.fatal(
                'Parsing/conversion of input file `%s` failed.', filepath)
            return False
        if len(molstruct.models) > 1:
            log.warning(
                'There is more than one model in the input file. Only the '
                'first model will be used.')
            molstruct.models = molstruct.models[0:1]
        molstruct.label = label
        if 'name' not in moldata:
            moldata['name'] = label
        molstruct.name = moldata['name']
        # Sort structures to allow easier zip-iterations.
        mod = molstruct.models[0]
        for chain in mod.chains:
            chain.residues.sort(key=lambda r: r.serial)
            for res in chain.residues:
                res.atoms.sort(key=lambda a: a.name)
        for bond in mod.bonds:
            bond.atoms.sort(key=lambda a: a.name)
        mod.bonds.sort(key=lambda b: '%d%d%s%s' % (
            b.atoms[0].residue.serial, b.atoms[1].residue.serial,
            b.atoms[0].name, b.atoms[1].name))
        # Write structures to `input` directory.
        if not os.path.exists(trg_filepath):
            fmol = murdock.moldata.convert_to_file(molstruct, ext)
            fmol.write(trg_filepath)
        # Overwrite input filepaths with local filepaths.
        molstruct.source.filepath = trg_filepath
        moldata[key] = os.path.join('input', trg_filename)
        # Parse reference structure.
        if not ref and 'ref_filepath' in moldata:
            ref_molstruct = self._parse_molstruct(moldata, ref=True)
            num_atoms = len(molstruct.atoms())
            if not num_atoms == len(ref_molstruct.atoms()):
                log.fatal(
                    'File `%s` can not be used as reference for file `%s`; '
                    'different numbers of atoms found.',
                    moldata['ref_filepath'], filepath)
                return False
            matches = murdock.molstruct.match_atoms(
                molstruct.atoms(), ref_molstruct.atoms(), match_name=True,
                match_residue_name=True, match_residue_serial=True)
            if not matches or num_atoms != len(matches):
                log.fatal(
                    'File `%s` can not be used as reference for file `%s`. '
                    'Atoms from both files could not be matched unambigiously '
                    'based on their atom name, residue name and residue '
                    'serial.', moldata['ref_filepath'], filepath)
                return False
            log.info(
                'File `%s` is used as reference for `%s`.',
                ref_molstruct.source.filepath, molstruct.source.filepath)
            molstruct.reference = ref_molstruct
        return molstruct

    def _preprocess_input(self):
        """Use function :attr:`preprocessing` on all :meth:`molstructs()`.
        """
        mod = murdock.misc.get_python_module(
            self.preprocessing['module'])
        preprocessing = murdock.misc.get_python_function(
            mod, self.preprocessing['function'])
        kwargs = self.preprocessing['arguments']
        for molstruct in self.molstructs():
            log.info('Preprocess `%s`.', molstruct.name)
            try:
                control = preprocessing(molstruct, **kwargs)
            except (MurdockTerminate, MurdockInterrupt):
                raise
            except:
                log.fatal(traceback.format_exc())
                log.fatal(
                    'Preprocessing function `%s.%s` crashed for structure '
                    '`%s`. Check traceback, function log and documentation '
                    'for more information.', self.preprocessing['module'],
                    self.preprocessing['function'], molstruct.source.filepath)
                return False
            if control is False:
                log.fatal(
                    'Preprocessing function `%s.%s` returned `False` for '
                    'structure `%s`. Check function log and documentation for '
                    'more information.', self.preprocessing['module'],
                    self.preprocessing['function'], molstruct.source.filepath)
                return False
            if molstruct.reference is not None:
                log.info(
                    'Preprocess reference structure for `%s`.', molstruct.name)
                if control != preprocessing(molstruct.reference, **kwargs):
                    log.fatal(
                        'During preprocessing, the structure `%s` could not '
                        'be validated as reference for `%s`.',
                        molstruct.source.filepath,
                        molstruct.reference.source.filepath)
                    return False
        return True

    def _run(self):
        if self.dry and not self.restore:
            log.info('Dry run finished. Docking will be skipped.')
            self.result.set_status('finished')
            return True
        while not self.current_run or self.current_run.serial < self.num_runs:
            if not self.current_run or self.current_run.done:
                self.result.new_run()
            self.current_run.set_status('started')
            log.info('Start docking run %d.', self.current_run.serial)
            if not self._run_steps():
                self._end_run('failed')
                log.warning(
                    'Docking run %d finished without success (`%s`).',
                    self.current_run.serial, self.title)
                if self.failmode == 'abort':
                    log.warning('Abort docking `%s`.', self.title)
                    return False
                elif self.failmode == 'repeat':
                    log.info(
                        'Repeat docking run %d.',
                        self.result.runs.pop().serial)
            else:
                self._end_run('finished')
            if self.screening_pid and not self._parent_process_alive():
                log.error(
                    'The parent screening process %d has been found dead and '
                    'its child docking process %d (`%s`) has become a zombie. '
                    'After careful consideration of its situation the orphan '
                    'zombie child has decided to shut down.',
                    self.screening_pid, os.getpid(), self.title)
                return False
        if not self.dry:
            self.result.update_status(self.num_runs)
        return True

    def _run_steps(self):
        """Run all docking steps once and write results.
        """
        root = self.input_root.deepcopy(
            suffix='-run%05d' % self.current_run.serial)
        self._center_dynamic(root)
        start = 0 if not self.current_step else self.current_step.ind + 1
        for ds in self.dsteps[start:]:
            if ds.extvideo and self.current_run.ind == 0:
                ds.extvideo.add_static(root)
            step = self.current_run.new_step(ds.title)
            step.set_status('started')
            log.info(
                'Start docking run %d, step %d.', step.run.serial, step.serial)
            self.update()
            self.update_full = True
            success, scoring = ds.run(root)
            if success:
                self._add_docked(root, scoring)
                self._write_docked(root)
                self._end_step('finished')
            else:
                log.warning(
                    'Docking step %d failed (`%s`).', step.serial, self.title)
                self._end_step('failed')
                return False
        return True

    def _setup(
            self, file_level=logging.INFO, console_level=None, full_log=True):
        """Set up :class:`Docking` for usage of :meth:`run`.
        """
        if file_level is not None:
            if full_log:
                l = Logger()
            else:
                l = log.logger
            l.add_file_handler(
                level=file_level, logdir=self.resdir,
                filename='%s.log' % self.label)
        if console_level is not None:
            log.logger.add_console_handler(level=console_level)
        if self.resume or self.restore:
            log.info('Resume docking `%s`.', self.title)
        else:
            log.info('Start docking `%s`.', self.title)
        try:
            if self.restore and self.result.load_json(
                    self.json_filepath, full=False):
                log.info(
                    'Timing information from existing result file `%s` will '
                    'be used.', self.json_filepath)
                self.result.timing.end.clear()
            if self.resume and self.result.load_json(
                    self.json_filepath, full=True):
                log.info(
                    'Existing results file `%s` read successfully. %d docking '
                    'runs have been found.', self.json_filepath,
                    len(self.result.runs))
                self.result.update_status(self.num_runs)
                if self.result.done:
                    return True
                self.result.timing.end.clear()
        except ValueError as exc:
            log.warning(
                'Can not parse docking result file `%s`: %s.',
                self.json_filepath, str(exc))
        except IOError as exc:
            log.info(
                'No existing docking result file `%s` found.',
                self.json_filepath)
        log.info('Parse and convert input structures.')
        if not self._parse_input():
            return False
        if self.preprocessing is not None and not self._preprocess_input():
            return False
        log.info('Create tree structure.')
        if not self._create_tree():
            log.fatal(
                'Error while creating tree structure from input structures.')
            return False
        if not self.result.receptor:
            self.result.new_molecules(self.moldata)
        if not self.result.unbonded and not self._add_unbonded():
            return False
        if not self.result.references and not self._add_references():
            log.fatal('Error in determination of reference information.')
            return False
        return True

    def _shutdown(self, quick=False):
        """Do final chores before the sun goes down.
        """
        try:
            self.result.timing.end.set_current()
            if quick:
                log.info('Shut down (quick).')
                self.update_full = False
            else:
                log.info('Shut down.')
                self._write_extvideoscripts()
                self.update_full = True
            if self.result.running:
                self.result.set_status('aborted')
                self._end_step(self.status)
                self._end_run(self.status)
            self.update()
        except (MurdockInterrupt, MurdockTerminate):
            return self._shutdown(quick=True)
        log.info('Docking done.')
        return True

    def _write_docked(self, root):
        """Write docked structures.
        """
        overwrite = (
            self.restore or self.resume or
            self.failmode == 'repeat')
        for atom in root.atoms:
            atom.source.source.coords = atom.coords.copy()
        for (node, molstruct) in zip(
                root.children, self.molstructs()):
            if node.static:
                continue
            if self.outfmts is None:
                outpaths = [self.docked_filepath(molstruct)]
            else:
                outpaths = [
                    self.docked_filepath(molstruct, _ext) for _ext in
                    self.outfmts]
            for outpath in outpaths:
                ext = os.path.splitext(outpath)[1]
                f = murdock.moldata.convert_to_file(molstruct, ext)
                f.write(outpath, overwrite=overwrite)
            self.current_step.filepaths[molstruct] = os.path.join(
                'docked', os.path.basename(outpaths[0]))
        return True

    def _write_extvideoscripts(self):
        for ds in self.dsteps:
            if ds.extvideo is not None:
                ds.extvideo.write_script()
        return True


class DockingStep(object):
    """A class to store parameters of a single step in a docking workflow.
    """

    def __init__(self, search_module, search_parms, scoring_module,
                 scoring_parms, transform_parms, ind=None, title='unnamed',
                 write_intvideo=False, write_extvideo=False,
                 store_decoy_scores=False):
        #: index within docking
        self.ind = ind
        #: title for this step (e.g. `global search` or `refinement`)
        self.title = title
        #: search module used (must be compatible to :mod:`search.`)
        self.search_module = search_module
        #: parameters for :attr:`search_module`
        self.search_parms = search_parms
        #: scoring module used (must be compatible to :mod:`scoring`)
        self.scoring_module = scoring_module
        #: parameters for :attr:`scoring_module`
        self.scoring_parms = scoring_parms
        #: parameters for the :class:`~murdock.tree.Node.transforms`
        self.transform_parms = transform_parms
        #: :class:`Docking` instance this step is associated with
        self.docking = None
        #: external video all search runs can add objects and frames to
        self.extvideo = None
        #: whether to write an external video
        self.write_extvideo = write_extvideo
        #: whether to write an internal video for each search run
        self.write_intvideo = write_intvideo
        #: whether to store the score of every state sampled during the search
        self.store_decoy_scores = store_decoy_scores

    @property
    def serial(self):
        try:
            return self.ind + 1
        except TypeError:
            return None

    def get_scoring(self, root):
        """Return a :class:`~murdock.scoring.Scoring` instance.

        The instance is created using :attr:`scoring_module` and
        :attr:`scoring_parms`.

        Unbonded scores are calculated for each `child` of ``root``
        individually and set as offset for each scoring term in the main
        `scoring` object returned (i.e. the unbonded scores will be substracted
        for every scoring term in the `scoring` object).

        """
        scoring = self.scoring_module.Scoring(root=root)
        if not scoring.setup(self.scoring_parms, docking=self.docking):
            return False
        return scoring

    def get_search(self, root, scoring):
        """Return a :class:`~murdock.search.Search` instance.

        The instance is created using :attr:`search_module` and
        :attr:`search_parms`.

        """
        intvideo = self._get_intvideo()
        search = self.search_module.Search(
            docking=self.docking, root=root, scoring=scoring,
            parms=self.search_parms, debugsampling=self.docking.debugsampling,
            intvideo=intvideo, extvideo=self.extvideo,
            store_decoy_scores=self.store_decoy_scores)
        if not search.setup():
            return False
        return search

    def get_formatted_rotbonds(self, root):
        try:
            rotbondconfig = self.transform_parms['rotatable_bonds']
        except KeyError:
            return collections.OrderedDict()
        fmt_rotbonds = collections.OrderedDict()
        for node in root.children:
            rotbonds = _get_rotbonds(rotbondconfig, node)
            if not rotbonds:
                continue
            mol = murdock.misc.get_source(
                node, src_type=murdock.molstruct.MolecularStructure)
            fmt_rotbonds[mol] = _formatted_rotbonds(rotbonds)
        return fmt_rotbonds

    def get_unbonded_scoring(self):
        scoring = self.scoring_module.Scoring(murdock.tree.Node())
        scoring.setup(self.scoring_parms, docking=self.docking)
        for child in self.docking.input_root.children:
            original_parent = child.parent
            croot = murdock.tree.Node()
            child.parent = croot
            croot.add_node(child)
            cscoring = self.scoring_module.Scoring(root=croot)
            if not cscoring.setup(self.scoring_parms, docking=self.docking):
                child.parent = original_parent
                continue
            cscoring.rescore()
            for sum_term, term in zip(scoring.terms, cscoring.terms):
                sum_term.values[child] = term.unweighted()
            child.parent = original_parent
        self.scoring_parms['unbonded_scores'] = {
            _term.name: _term.weighted() for _term in scoring.terms}
        return scoring

    def init_extvideo(self):
        if not self.write_extvideo:
            return False
        outdir = os.path.join(
            self.docking.resdir, 'pymol', 'video', 'compilation',
            'step%02d' % self.serial)
        prefix = '%s-step%02d' % (self.docking.label, self.serial)
        self.extvideo = PyMOLVideo(outdir=outdir, prefix=prefix)
        return True

    def run(self, root):
        """Run docking step.
        """
        if not self.setup_transforms(root):
            log.fatal('Error in setup of degrees of freedom.')
            return False, False
        scoring = self.get_scoring(root=root)
        if not scoring:
            log.fatal('Error in setup of scoring function.')
            return False, False
        search = self.get_search(root, scoring)
        if not search:
            log.fatal('Error in setup of conformational search method.')
            return False, False
        if self.docking.restore or self.docking.resume:
            if self._restore_docked_structure(root):
                self.docking.update_full = False
                scoring.set_postdocking_scoring_terms()
                return True, scoring
            elif self.docking.dry:
                self.docking.update_full = True
                log.info(
                    'No docked structures found for step `%s`. Mark as '
                    'failed.', self.title)
                return False, False
            elif self.docking.update_full:
                self.docking.update()
        self.docking.update_full = True
        log.info(
            'Run conformational search `%s`.', self.search_module.__name__)
        try:
            if search.run():
                success = True
            else:
                success = False
                log.warning(
                    'Conformational search step `%s` failed (`%s`).',
                    self.title, self.docking.title)
        finally:
            if search.intvideo is not None:
                try:
                    search.intvideo.write_script()
                except KeyboardInterrupt:
                    search.intvideo.write_script()
                    raise
            if search.extvideo is not None:
                search.extvideo.write_script()
        scoring.set_postdocking_scoring_terms()
        return success, scoring

    def setup_transforms(self, root):
        """Setup up transformations sampled by the search algorithm.

        All transformations defined in
        :meth:`~murdock.transforms.ConfigDeclaration.transforms` are set
        up and their (default) sampling step lengths are defined here:

        1) Translation:
            For the first search step of each docking, the maximum step length
            is set to the receptor radius (half of the maximum atom distance)
            so that each point of the receptor can be reached within two
            iterations and - effectively - the whole receptor surface is
            sampled (global search).

            For all consecutive search steps, the sampling maximum step length
            is set to 3.0 Angstroem so that an approximate binding region is
            sampled more densely (local search).

        2) Rigit ligand rotation:
            For all search steps, the full rotational space is sampled.

        3) Bond rotation:
            For all search steps, the full rotational range is sampled.

        These settings can be overridden (for each search step individually)
        using the parameters described in
        `murdock.transforms.ConfigDeclaration.basic_tf()`.

        """
        tf_parms = self.transform_parms
        # Clear all formerly defined subtrees and tranformations from `root`.
        for child in root.children:
            child.children = []
            child.transforms = []
            molstruct = child.source.source.source
            if (
                    molstruct is self.docking.receptor or
                    molstruct is self.docking.receptor.reference):
                child.static = True
        for bond in root.bonds:
            bond.rotatable = False
        # Define transformation parameters.
        if 'translation' in tf_parms:
            try:
                scaling_t = tf_parms['translation']['scaling']
            except KeyError:
                if self is self.docking.dsteps[0]:
                    scaling_t = murdock.molstruct.radius(
                        self.docking.receptor.atoms())
                else:
                    scaling_t = 3.0
            try:
                maxstep_t = tf_parms['translation']['max_step']
            except KeyError:
                maxstep_t = None
        if 'rotation' in tf_parms:
            try:
                scaling_r = tf_parms['rotation']['scaling']
            except KeyError:
                scaling_r = scipy.constants.pi
            try:
                maxstep_r = tf_parms['rotation']['max_step']
            except KeyError:
                maxstep_r = None
        if 'rotatable_bonds' in tf_parms:
            try:
                scaling_b = tf_parms['rotatable_bonds']['scaling']
            except KeyError:
                scaling_b = scipy.constants.pi
            try:
                maxstep_b = tf_parms['rotatable_bonds']['max_step']
            except KeyError:
                maxstep_b = None
            if not self.setup_rotbonds(root, scaling_b, maxstep_b):
                return False
        for node in root.children:
            # For the receptor, do not set up translation nor rotation.
            molstruct = node.source.source.source
            if (
                    molstruct is self.docking.receptor or
                    molstruct is self.docking.receptor.reference):
                continue
            # Get anchor atom.
            anchor = murdock.molstruct.get_center_atom(node.atoms)
            # Set up translation.
            if 'translation' in tf_parms:
                tf_t = Translation(
                    node=node, anchor=anchor, scaling=scaling_t,
                    max_step=maxstep_t)
                node.add_transformation(tf_t)
            # Set up rigid rotation.
            if 'rotation' in tf_parms:
                tf_r = Rotation(
                    node=node, anchor=anchor, scaling=scaling_r,
                    max_step=maxstep_r)
                node.add_transformation(tf_r)
        return True

    def setup_rotbonds(self, root, scaling, max_step):
        """Setup rotatable bonds in `root` for this docking step.
        """
        for node in root.children:
            # Select and measure/set bond angles
            rotbonds = _get_rotbonds(
                self.transform_parms['rotatable_bonds'], node)
            if rotbonds is False:
                return False
            elif rotbonds:
                for bond in rotbonds:
                    bond.rotatable = True
                try:
                    node.init_rotbonds(
                        bonds=rotbonds, scaling=scaling, max_step=max_step)
                except murdock.tree.TreeError:
                    log.fatal(
                        'Can not set up the torsional tree using the given '
                        '%d rotatable bonds in `%s`. Make sure that the '
                        'method defined in the `rotatable bonds` section of '
                        'the configuration file selects the right bonds and '
                        'that there are proper bond data in the input files '
                        'used.', len(rotbonds), node.name)
                    return False
        return True

    def _get_intvideo(self):
        if not self.write_intvideo:
            return None
        run_serial, = self.docking.current_run.serial
        step_serial, = self.docking.current_step.serial
        outdir = os.path.join(
            self.docking.resdir, 'pymol', 'video', 'runs',
            'run%05d' % run_serial, 'step%02d' % step_serial)
        prefix = '%s-run%05d-step%02d' % (
            self.docking.label, run_serial, step_serial)
        return PyMOLVideo(outdir=outdir, prefix=prefix)

    def _restore_docked_structure(self, root):
        for node, molstruct in zip(root.children, self.docking.molstructs()):
            if node.static:
                continue
            outpaths = [self.docking.docked_filepath(molstruct)]
            if self.docking.outfmts is not None:
                for ext in self.docking.outfmts:
                    filepath = self.docking.docked_filepath(molstruct, ext)
                    if filepath not in outpaths:
                        outpaths.append(filepath)
            for filepath in outpaths:
                if not os.path.exists(filepath):
                    continue
                docked = murdock.moldata.get_molstruct(filepath)
                if not docked:
                    log.warning(
                        'Docked structure file `%s` found: Parsing error.',
                        filepath)
                    continue
                break
            else:
                return False
            matches = murdock.molstruct.match_atoms(
                node.atoms, docked.atoms(), match_name=True,
                match_residue_name=False, match_residue_serial=True,
                match_chain_name=False, match_chain_serial=False)
            if len(matches) != len(node.atoms):
                log.error(
                    'Docked structure file `%s` found: Atom mapping '
                    'error.', filepath)
                return False
            for atom, restored_atom in viewitems(matches):
                atom.coords = restored_atom.coords.copy()
            log.info('Docked structure file `%s` found: Restored.', filepath)
        return True


def _dist_to_ref(function, root, ref_root):
    rmsds = collections.OrderedDict()
    for node in root.children:
        node_name = node.source.source.source.name
        min_rmsd = None
        if not node.static:
            for ref_node in ref_root.children:
                ref_name = ref_node.source.source.name
                if node_name != ref_name:
                    if len(node.atoms) != len(ref_node.atoms):
                        continue
                    if False in (_a.name == _r.name for _a, _r in zip(
                            node.atoms, ref_node.atoms)):
                        continue
                    if False in (_a.serial == _r.serial for _a, _r in zip(
                            node.atoms, ref_node.atoms)):
                        continue
                rmsd = function(node.atoms, ref_node.atoms)
                if min_rmsd is None or min_rmsd > rmsd:
                    min_rmsd = rmsd
        mol = murdock.misc.get_source(
            node, src_type=murdock.molstruct.MolecularStructure)
        if min_rmsd is not None:
            rmsds[mol] = min_rmsd
    return rmsds


def _get_rotbonds(rotbondconfig, node):
    try:
        mod = murdock.misc.get_python_module(
            rotbondconfig['module'])
        func = murdock.misc.get_python_function(
            mod, rotbondconfig['function'])
        kwargs = rotbondconfig['arguments']
        receptor = (node.object_serial == 0)
        rotbonds = func(node.bonds, receptor, **kwargs)
    except (MurdockTerminate, MurdockInterrupt):
        raise
    except:
        log.fatal(traceback.format_exc())
        log.fatal(
            'Rotatable bond function `%s.%s` crashed for structure `%s`. '
            'Check function traceback, log and documentation for more '
            'information.', rotbondconfig['module'], rotbondconfig['function'],
            node.source.name)
        raise MurdockInterrupt
    if rotbonds is False:
        log.fatal(
            'Rotatable bond function `%s.%s` returned `False` for structure '
            '`%s` (should return empty list if no bonds are selected). Check '
            'function log and documentation for more information.',
            rotbondconfig['module'], rotbondconfig['function'],
            node.source.name)
        raise MurdockInterrupt
    return rotbonds


def _formatted_rotbonds(rotbonds):
    return [
        collections.OrderedDict(
            (('name', _rb.name), ('angle', _rb.angle()))) for _rb
        in sorted(rotbonds, key=lambda _x: id(_x.unbonded))]


def _formatted_sampling(root):
    sampling = collections.OrderedDict()
    for node in root.descendants():
        for tf in node.transforms:
            name = tf.name
            if name in sampling:
                i = 1
                name = '%s%05d' % (tf.name, i)
                sampling[name] = sampling[tf.name]
                del sampling[tf.name]
                while name in sampling:
                    i += 1
                    name = '%s%05d' % (tf.name, i)
            sampling[name] = {
                'labels': tf.history_labels, 'values': tf.history}
    return sampling


def _residue_distances(root, nres=None):
    root = root.deepcopy()
    dist = collections.OrderedDict()
    for child1 in root.children:
        mol1 = murdock.misc.get_source(
            child1, src_type=murdock.molstruct.MolecularStructure)
        if mol1 not in dist:
            dist[mol1] = collections.OrderedDict()
        for child2 in root.children:
            if child1 is child2:
                continue
            mol2 = murdock.misc.get_source(
                child2, src_type=murdock.molstruct.MolecularStructure)
            if mol2 not in dist:
                dist[mol2] = collections.OrderedDict()
            d1, d2 = child1.residue_distances(child2)
            for res, v in viewitems(d1):
                reskey = murdock.misc.ResidueFormatter.from_residue(res).key
                if (reskey not in dist[mol1] or
                        dist[mol1][reskey] > v):
                    dist[mol1][reskey] = v
            for res, v in viewitems(d2):
                reskey = murdock.misc.ResidueFormatter.from_residue(res).key
                if (reskey not in dist[mol2] or
                        dist[mol2][reskey] > v):
                    dist[mol2][reskey] = v
    for mol, vals in viewitems(dist):
        vals = sorted(list(viewitems(vals)), key=lambda _x: _x[1])
        if nres is not None:
            vals = vals[:nres]
        dist[mol] = collections.OrderedDict(vals)
    return dist


def _residue_scores(scoring, nres=None):
    s = scoring.deepcopy()
    for term in s.terms:
        term.values = {}
    contr = collections.OrderedDict()
    for child1 in s.root.children:
        mol1 = murdock.misc.get_source(
            child1, src_type=murdock.molstruct.MolecularStructure)
        if mol1 not in contr:
            contr[mol1] = collections.OrderedDict()
        for child2 in s.root.children:
            if child1 is child2:
                continue
            mol2 = murdock.misc.get_source(
                child2, src_type=murdock.molstruct.MolecularStructure)
            if mol2 not in contr:
                contr[mol2] = collections.OrderedDict()
            d1, d2 = s.residue_scores(child1, child2)
            if False in (d1, d2):
                log.info(
                    'Scoring function `%s` does not give residue scores.',
                    scoring.name)
                return False
            for res, s1 in viewitems(d1):
                reskey = murdock.misc.ResidueFormatter.from_residue(res).key
                if reskey not in contr[mol1]:
                    contr[mol1][reskey] = 0.0
                contr[mol1][reskey] += s1
            for res, s2 in viewitems(d2):
                reskey = murdock.misc.ResidueFormatter.from_residue(res).key
                if reskey not in contr[mol2]:
                    contr[mol2][reskey] = 0.0
                contr[mol2][reskey] += s2
    for mol, vals in viewitems(contr):
        vals = sorted(list(viewitems(vals)), key=lambda _x: _x[1])
        if nres is not None and len(vals) > nres:
            vals = vals[:nres]
        contr[mol] = collections.OrderedDict(vals)
    return contr


class ConfigDeclaration(murdock.config.ConfigDeclaration):

    def docking(self):
        """Configuration options for a docking setup:

            - "title":
                project title used in formatted results `(dtype=str,
                required=True)`

            - "label":
                project label used in result filenames (no special characters)
                `(dtype=str, required=False)`

            - "user":
                program user / scientist responsible for the experiment
                `(dtype=str, required=False, default=<username>)`

            - "number_of_runs":
                number of independent docking runs `(dtype=int, default=1)`

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

            - "input_data":
                information on (molecular)
                :meth:`~murdock.runner.docking.ConfigDeclaration.input_data` to
                be used `(dtype=dict, required=True)`

        """
        Option = murdock.config.ConfigOption
        opt = self.get_default_options()
        opt.append(Option(
            name='title', dtype=Option.string, description='project title '
            'used in formatted results'))
        opt.append(Option(
            name='label', dtype=Option.string, description='project label '
            'used in result filenames', required=False))
        try:
            username = os.environ['LOGNAME']
        except KeyError:
            username = None
        opt.append(Option(
            name='user', dtype=Option.string, description='program user / '
            'scientist responsible for the experiment', default=username,
            required=False))
        opt.append(Option(
            name='number_of_runs', dtype=Option.int_gt_zero, default=1,
            description='number of independent docking runs'))
        opt.append(Option(
            name='fail-mode', dtype=Option.string, description='what to do if '
            'a single docking run fails', default='continue',
            choices=('abort', 'continue', 'repeat')))
        opt.append(Option(
            name='preprocessing', dtype=dict, required=False,
            description='information on python function used to prepare or '
            'correct input structures'))
        opt.append(Option(
            name='steps', dtype=list, description='main section defining '
            'docking workflow'))
        opt.append(Option(
            name='input_data', dtype=dict, description='information on '
            '(molecular) input data to be used'))
        return opt

    def input_data(self):
        """Configuration options for external input data.

            - "receptor":
                options for the input
                :meth:`~murdock.runner.docking.ConfigDeclaration.receptor`,
                i.e. the docking target `(dtype=dict, required=True)`

            - "ligands":
                list of input
                :meth:`~murdock.runner.docking.ConfigDeclaration.ligands`,
                which are docked onto the receptor simultaneously `(dtype=list,
                required=True)`

        """
        Option = murdock.config.ConfigOption
        opt = self.get_default_options()
        opt.append(Option(
            name='receptor', dtype=dict, description='dictionary containing '
            'receptor information'))
        opt.append(Option(
            name='ligands', dtype=list, description='list containing ligand '
            'information'))
        return opt

    def receptor(self):
        """Configuration options for the input receptor.

        Refer to :meth:`murdock.runner.docking.ConfigDeclaration.moldata`.

        Additional configuration options:

            - "residuals_filepath":
                path to a file containing residual atoms not to be considered
                during docking which are only added to PyMOL pictures to mark
                possibly blocked binding sites `(dtype=str, required=False)`

        """
        Option = murdock.config.ConfigOption
        opt = self.moldata()
        opt.append(Option(
            name='residuals_filepath', dtype=Option.string, required=False,
            check_filepath=True, description='path to a file containing '
            'residual atoms not to be considered during docking but shown in '
            'PyMOL pictures'))
        return opt

    def ligands(self):
        """Configuration options for input ligands.

        Refer to :meth:`murdock.runner.docking.ConfigDeclaration.moldata`.

        """
        return self.moldata()

    def moldata(self):
        """Configuration options for molecular input structures.

            - "name":
                structure name used in formatted results; if not given, the
                input filename will be used `(dtype=str, required=False)`

            - "label":
                structure label used in result filenames (no special
                characters); if not given, the "name" without special
                characters will be used `(dtype=str, required=False)`

            - "filepath":
                filepath to input structure `(dtype=str, required=True)`

            - "ref_filepath":
                filepath to reference structure (if available); output
                conformations, scores, etc. are compared to this reference in
                the final results and statistics `(dtype=str, required=False)`

            - "description":
                a short description of the molecule `(dtype=str,
                required=False)`

            - "resolution":
                spacial resolution of the input structure `(dtype=float,
                required=False)`

            - "tags":
                a list of tag strings for classification, sorting, etc. of
                input and output data `(dtype=str, required=False)`

        """
        Option = murdock.config.ConfigOption
        opt = self.get_default_options()
        opt.append(Option(
            name='label', dtype=Option.string, description='label used in '
            'result filenames', required=False))
        opt.append(Option(
            name='name', dtype=Option.string, description='name used in '
            'formatted results', required=False))
        opt.append(Option(
            name='filepath', dtype=Option.string, description='filepath to '
            'input structure', check_filepath=True))
        opt.append(Option(
            name='ref_filepath', dtype=Option.string, description='filepath '
            'to reference structure', required=False, check_filepath=True))
        opt.append(Option(
            name='description', dtype=Option.string, description='short '
            'description of the molecule', required=False))
        opt.append(Option(
            name='resolution', dtype=Option.float_ge_zero,
            description='spacial resolution of the input structure',
            required=False))
        opt.append(Option(
            name='tags', dtype=list, description='list of tag strings',
            required=False, validate=False))
        return opt

    def preprocessing(self):
        """Configuration options for the preprocessing of input structures:

            - "module":
                name of the Python module containing the preprocessing function
                `(dtype=str, required=True)`

            - "function":
                name of the preprocessing Python function `(dtype=str,
                required=True)`

            - "arguments":
                dictionary of keyword arguments passed to the function
                `(dtype=dict, default={}, validate=False)`

        The preprocessing function may be an arbitrary Python function taking
        a :class:`~murdock.molstruct.MolecularStructure` as first argument (and
        optionally additional arguments) and modifying it in some way. The
        function must return ``True``/``False`` for successful/unsuccessful
        modification. Before any docking/screening is started Murdock calls the
        function once for each input structure.

        Example::

            # -*- coding: utf-8 -*-
            #
            \"\"\"Custom preprocessing module.

            This module contains two examples of functions which can be used
            for preprocessing.

            \"\"\"

            # recommended header for all custom Murdock modules
            from __future__ import unicode_literals
            import logging

            # Initialize logger.
            log = logging.getLogger('custom.preprocessing_example')

            def fix_terminal_residue_names(molstruct):
                \"\"\"Remove leading `N` and `C` from terminal residues.
                \"\"\"
                for res in molstruct.residues():
                    if len(res.name) > 4:
                        log.error(
                            'The residue name `%s` is too long. Check input '
                            'data.', res.name)
                        return False
                    elif len(res.name) == 4 and res.name[0] in ('N', 'C'):
                        res.name = res.name[1:]
                return True

            def remove_trailing_numbers_from_residue_names(molstruct):
                \"\"\"Remove trailing residue numbers from residue names.

                In some input files the residue number is added to the residue
                name (e.g. `ARG112`). This function removes the trailing
                number from the residue name if it corresponds to the residue
                id.

                \"\"\"
                for res in molstruct.residues():
                    numstr = str(res.serial)
                    if res.name.endswith(numstr):
                        cut = len(res.name) - len(numstr)
                        res.name = res.name[:cut]
                return True

        """
        Option = murdock.config.ConfigOption
        opt = self.get_default_options()
        opt.append(Option(
            name='module', dtype=Option.string, description='python module '
            'containing the preprocessing function'))
        opt.append(Option(
            name='function', dtype=Option.string, description='python '
            'function used to preprocess all molecular data before docking'))
        opt.append(Option(
            name='arguments', dtype=dict, description='dictionary of '
            'arguments passed to the function', default={}, validate=False))
        return opt

    def steps(self):
        """Configuration options defining a docking step:

            - "title":
                 step title used in formatted results `(dtype=str,
                 required=True)`

            - "label":
                step label used in result filenames (no special characters)
                `(dtype=str, required=False)`

            - "scoring":
                options for the
                :meth:`~murdock.scoring.ConfigDeclaration.\
                scoring()` function to be used `(dtype=dict, required=True)`

            - "transforms":
                definition of the
                :meth:`~murdock.transforms.ConfigDeclaration.\\
                transforms()` sampled during the conformational search
                `(dtype=list, required=True)`

            - "search":
                options for the conformational
                :meth:`~murdock.search.ConfigDeclaration.search()` method
                `(dtype=dict, required=True)`

            - "description":
                a short description of the docking setup `(dtype=str,
                required=False)`

        """
        Option = murdock.config.ConfigOption
        opt = self.get_default_options()
        opt.append(Option(
            name='label', dtype=Option.string, description='step label used '
            'in result filenames', required=False))
        opt.append(Option(
            name='title', dtype=Option.string, description='step title used '
            'in formatted results'))
        opt.append(Option(
            name='tags', dtype=list, description='list of tag strings',
            required=False, validate=False))
        opt.append(Option(
            name='scoring', dtype=dict, description='dictionary containing '
            'information on the scoring function used'))
        opt.append(Option(
            name='transforms', dtype=dict, description='dictionary of '
            'transformations sampled during the conformational search'))
        opt.append(Option(
            name='search', dtype=dict, description='dictionary containing '
            'information on the conformational search algorithm used'))
        opt.append(Option(
            name='description', dtype=str, description='short description of '
            'the docking setup', required=False))
        return opt


def get_search_filepath(resdir, mainlabel, sublabel='search'):
    return os.path.join(resdir, '%s-%s.json' % (mainlabel, sublabel))
