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
Module :mod:`murdock.custom.ehits`
----------------------------------

A wrapper module for the software eHiTS. It provides the classes
:class:`Search` and :class:`Scoring` which are conform with the Murdock
:mod:`~murdock.search` and :mod:`~murdock.scoring` APIs.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future.utils import viewitems

import codecs
import collections
import logging
import os
import re
import subprocess
import traceback

import murdock.config
import murdock.molstruct
import murdock.moldata
import murdock.scoring
import murdock.scoring.pool
import murdock.search.rescore


log = logging.getLogger('custom.ehits')


class Scoring(murdock.scoring.Scoring):

    def setup(self, parms, docking, name='eHiTS', copy=False):
        #: minimization parameters, paths, terms and weights
        self.parms = parms
        #: name of this scoring method
        self.name = name
        #: :class:`~murdock.runner.docking.Docking` instance associated with
        #: this scoring
        self.docking = docking
        #: interpreter to call script
        self.interpreter = self.parms['interpreter']
        #: path to eHiTS executable
        self.ehits_exec = self.parms['ehits_executable']
        #: eHiTS command-line parameter `-accuracy`
        self.accuracy = self.parms['accuracy']
        #: whether to perform a blind docking
        self.blind = self.parms['blind']
        #: eHiTS command-line parameter `-margin`
        self.margin = self.parms['margin']
        # Add dummy scoring term.
        term = murdock.scoring.pool.Manual()
        term.setup(name='eHiTS', weight=1)
        self.add_term(term)
        #: path to eHiTS-Tune parameter file (e.g. `receptors.rkba`)
        self.tuneparm_filepath = None
        try:
            self.tuneparm_filepath = self.parms['tune_parameters']
        except KeyError:
            pass
        #: name of output directory
        self.outdir = None
        if not self.docking.state[0]:
            return True
        self.outdir = os.path.abspath(os.path.join(
            self.docking.resdir, self.parms['workdirname'],
            'run%05d' % self.docking.state[0],
            'step%02d' % self.docking.state[1]))
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)
        if copy:
            return True
        # Write structure, perform eHiTS docking and parse the output.
        if not self._dock():
            return False
        return True

    def rescore(self, node=None):
        return 0

    def residue_scores(self, *args):
        return False, False

    def _dock(self):
        """Write input structures, call script and read output structures.
        """
        for atom in self.root.atoms:
            atom.source_atom.coords = atom.coords.copy()
        recnode, recpath, ligands = self._write_input_structs()
        for lignode, ligpath in viewitems(ligands):
            if not self._dock_ligand(recnode, recpath, lignode, ligpath):
                return False
        log.info('Docking successful (`%s`).', self.outdir)
        return True

    def _dock_ligand(self, recnode, recpath, lignode, ligpath):
        molstruct = lignode.source.source.source
        liglabel = molstruct.label
        workdir = os.path.join(self.outdir, liglabel)
        ligpath = os.path.basename(ligpath)
        ehits_logpath = os.path.join(
            workdir, 'results', recnode.source.name, liglabel, 'ehits.log')
        run_logpath = os.path.join(workdir, 'run.log')
        optargs = ''
        if not self.blind:
            optargs += ' -clip %s' % ligpath
        if self.tuneparm_filepath is not None:
            optargs += ' -rkb %s' % self.tuneparm_filepath
        outpath = os.path.join(workdir, '%s-docked.mol2' % liglabel)
        if os.path.exists(outpath) and self.docking.restore:
            log.info(
                'EHiTS docking result file `%s` found: Restored.',
                os.path.relpath(outpath, self.docking.resdir))
        else:
            runscript = SHELLSCRIPT.format(
                ehits_exec=self.ehits_exec, workdir=workdir,
                accuracy=self.accuracy, margin=self.margin,
                recpath=os.path.relpath(recpath, workdir), ligpath=ligpath,
                outpath=os.path.basename(outpath), optargs=optargs)
            if not self._run_script(runscript, workdir, run_logpath):
                log.fatal('EHiTS script failed.')
                self._log_ehits_errors(ehits_logpath)
                return False
        if not os.path.exists(outpath):
            log.warning(
                'There is no eHiTS result file `%s`.', os.path.relpath(
                    outpath, os.path.join(self.docking.resdir, '../')))
            self._log_ehits_errors(ehits_logpath)
            return False
        molstruct = murdock.moldata.get_molstruct(outpath)
        if not molstruct:
            log.error(
                'Docked molecular structure can not be retrieved from '
                'file `%s`.', os.path.relpath(outpath, self.docking.resdir))
            self._log_ehits_errors(ehits_logpath)
            return False
        self._fix_ehits_struct(molstruct)
        if not self._match_and_overwrite(lignode, molstruct):
            self._log_ehits_errors(ehits_logpath)
            return False
        self._parse_score((recnode, lignode), run_logpath)
        self._log_ehits_errors(ehits_logpath)
        return True

    def _fix_ehits_struct(self, molstruct):
        """Remove atoms added by eHiTS.
        """
        for residue in molstruct.iterate_residues():
            original_atoms = [
                _a for _a in residue.atoms if not
                _a.source.data[7].startswith('MOL')]
            diff = len(residue.atoms) - len(original_atoms)
            if diff:
                log.info(
                    'In residue %s (`%s`), delete %d atoms created by '
                    'eHiTS.', str(residue.serial), str(residue.name), diff)
            residue.atoms = original_atoms
        return True

    def _log_ehits_errors(self, ehits_logpath):
        errors = []
        try:
            with codecs.open(ehits_logpath, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            log.warning('Can not read eHiTS log file `%s`.', ehits_logpath)
            return False
        errors = [
            _l for _l in content.splitlines() if re.search('ERROR', _l) or
            re.search('segmentation fault', _l) or (
                re.search('WARNING', _l) and not re.search(
                    'WARNING clip file was not specified', _l))]
        if not errors:
            return True
        log.warning(
            'Collected eHiTS warnings and errors (`%s`):', os.path.relpath(
                ehits_logpath, os.path.join(self.docking.resdir, '../')))
        for error in errors:
            log.warning('  [%s] %s', os.path.basename(ehits_logpath), error)
        return True

    def _match_and_overwrite(self, lignode, molstruct):
        matches = murdock.molstruct.match_atoms(
            lignode.atoms, molstruct.atoms(), match_serial=True,
            match_name=True)
        missing_in_old = [
            _a for _a in molstruct.atoms() if _a not in matches.values()]
        missing_in_docked = [_a for _a in lignode.atoms if _a not in matches]
        if not matches or missing_in_old or missing_in_docked:
            log.error(
                'Error during atom matching between original and '
                'docked stucture.')
            if missing_in_old:
                log.error(
                    'The following atoms have been added by eHiTS: %s.',
                    ', '.join([
                        '%d (`%s`)' % (_a.serial, _a.name) for _a in
                        missing_in_old]))
            if missing_in_docked:
                log.error(
                    'The following atoms have been removed by eHiTS: %s.',
                    ', '.join([
                        '%d (`%s`)' % (_a.serial, _a.name) for _a in
                        missing_in_docked]))
            return False
        for old_atom, docked_atom in viewitems(matches):
            old_atom.coords = docked_atom.coords.copy()
        return True

    def _run_script(self, runscript, workdir, logpath):
        runscriptpath = os.path.join(workdir, 'run.sh')
        log.info(
            'Run eHiTS via shell script `%s`.',
            os.path.relpath(runscriptpath, self.docking.resdir))
        with codecs.open(runscriptpath, 'w', encoding='utf-8') as f:
            f.write(runscript)
        cmd = [self.interpreter, 'run.sh']
        try:
            with codecs.open(logpath, 'w', encoding='utf-8') as f:
                r = subprocess.call(cmd, stderr=f, stdout=f, cwd=workdir)
        except KeyboardInterrupt:
            raise
        except:
            errmsg = traceback.format_exc().splitlines()[-1]
            log.error('Error during script call: %s', errmsg)
            return False
        if r != 0:
            return False
        return True

    def _parse_score(self, nodes, logpath):
        try:
            with codecs.open(logpath, 'r', encoding='utf-8') as f:
                content = f.read()
            score = float(content.split('Pose# 0 Score:')[1].split('Name')[0])
        except:
            self.terms[0].values[nodes] = 0.
        else:
            self.terms[0].values[nodes] = score
        self.interactions.append(nodes)
        return True

    def _write_input_structs(self):
        recnode = None
        recpath = None
        ligands = collections.OrderedDict()
        for child in self.root.children:
            molstruct = child.source.source.source
            sourcefile = molstruct.source
            ext = os.path.splitext(sourcefile.filepath)[1]
            if ext == '.mol2':
                mol2file = sourcefile
            else:
                mol2file = murdock.moldata.convert_to_file(
                    molstruct, '.mol2', sort_atom_serials=True,
                    sort_residue_serials=True, sort_chain_serials=False)
            if child.static:
                if recpath is not None:
                    raise scoring.ScoringError(
                        'This EHiTS module supports only systems with one '
                        'static molecule.')
                recnode = child
                recpath = os.path.join(
                    self.outdir, '%s.mol2' % molstruct.label)
                mol2file.write(recpath, overwrite=True)
            else:
                workdir = os.path.join(self.outdir, molstruct.label)
                if not os.path.exists(workdir):
                    os.makedirs(workdir)
                filename = os.path.join(
                    workdir, '%s.mol2' % molstruct.label)
                mol2file.write(filename, overwrite=True)
                ligands[child] = filename
        if recpath is None:
            raise scoring.ScoringError(
                'This EHiTS module supports only systems with one fully '
                'static receptor.')
        return recnode, recpath, ligands


class Search(murdock.search.rescore.Search):
    pass


class ConfigDeclaration(murdock.config.ConfigDeclaration):

    def parameters(self):
        """Configuration options for this `ehits`-based scoring module:

            - "interpreter":
                filepath to shell interpreter `(dtype=str, required=True)`

            - "workdirname":
                name of working directory to be created within docking results
                directory `(dtype=str, default=ehits_work)`

            - "ehits_executable":
                path to the external eHiTS executable
                `(dtype=str, required=True)`

            - "accuracy":
                eHiTS command-line parameter `-accuracy`
                `(dtype=int, required=true)`

            - "blind":
                whether to perform a blind docking without using the docked
                solution from the last docking step
                `(dtype=bool, default=False)`

            - "margin":
                eHiTS command-line parameter `-margin`
                `(dtype=int, default=10.0)`

            - "tune_parameters":
                (optional) eHiTS-Tune parameter file (e.g. `receptors.rkba`)
                `(dtype=str, required=False)`

        """
        Option = murdock.config.ConfigOption
        opt = self.get_default_options()
        opt.append(Option(
            name='interpreter', dtype=Option.string, description='filepath to '
            'shell interpreter', check_filepath=True))
        opt.append(Option(
            name='workdirname', dtype=Option.string, description='name of '
            'working directory to be created', default='ehits_work'))
        opt.append(Option(
            name='ehits_executable', dtype=Option.string, description='path '
            'to the external eHiTS executable', check_filepath=True))
        opt.append(Option(
            name='accuracy', dtype=Option.int_gt_zero, description='eHiTS '
            'command-line parameter `-accuracy`'))
        opt.append(Option(
            name='blind', dtype=bool, default=False, description='whether to '
            'perform a blind docking'))
        opt.append(Option(
            name='margin', dtype=Option.int_gt_zero, description='eHiTS '
            'command-line parameter `-margin`', default=10.0))
        opt.append(Option(
            name='tune_parameters', dtype=Option.string, required=False,
            description='path to eHiTS-Tune parameter file (e.g. '
            '`receptor.rkba`)', check_filepath=True))
        return opt


SHELLSCRIPT = """\
{ehits_exec} -toprank 1 -drop -dropdir -clean -workdir {workdir} \
-out temp.tmb -accuracy {accuracy} -margin {margin} -receptor {recpath} \
-ligand {ligpath}{optargs}

/projects/bioinfp_apps/eHitS/eHiTS_2009.1/Linux/bin/convert temp.tmb \
{outpath} -noLp -noBuild -mol 0 \
-config /projects/bioinfp_apps/eHitS/eHiTS_2009.1/data/parameters.cfg

rm temp.tmb
"""
