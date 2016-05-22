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
Module :mod:`murdock.custom.flexx`
----------------------------------

A wrapper module for the software FlexX. It provides the classes
:class:`Search` and :class:`Scoring` which are conform with the Murdock
:mod:`~murdock.search` and :mod:`~murdock.scoring` APIs.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import codecs
import collections
import logging
import os
import re
import subprocess
import traceback

import murdock.config
import murdock.misc
import murdock.molstruct
import murdock.moldata
import murdock.scoring
import murdock.scoring.pool
import murdock.search.rescore


log = logging.getLogger('custom.flexx')


class Scoring(murdock.scoring.Scoring):

    def setup(self, parms, docking, name='FlexX', copy=False):
        #: minimization parameters, paths, terms and weights
        self.parms = parms
        #: name of this scoring method
        self.name = name
        #: :class:`~murdock.runner.docking.Docking` instance associated with
        #: this scoring
        self.docking = docking
        #: path to FlexX executable
        self.leadit_exec = self.parms['leadit_executable']
        #: whether to perform a blind docking
        self.blind = self.parms['blind']
        #: local docking margin around the initial ligand position
        self.margin = self.parms['margin']
        # Add dummy scoring term.
        term = murdock.scoring.pool.Manual()
        term.setup(name='FlexX', weight=1)
        self.add_term(term)
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
        # Write structure, perform FlexX docking and parse the output.
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
        recnode, recpath, ligpaths = self._write_input_structs()
        for lignode, ligpath in ligpaths.iteritems():
            if not self._dock_ligand(recnode, recpath, lignode, ligpath):
                return False
        log.info('Docking successful (`%s`).', self.outdir)
        return True

    def _dock_ligand(self, recnode, recpath, lignode, ligpath):
        ligstruct = lignode.source.source.source
        liglabel = ligstruct.label
        workdir = os.path.join(self.outdir, liglabel)
        ligpath = os.path.basename(ligpath)
        run_logpath = os.path.join(workdir, 'run.log')
        outpath = os.path.join(workdir, '%s-docked.mol2' % liglabel)
        if os.path.exists(outpath) and self.docking.restore:
            log.info(
                'FlexX docking result file `%s` found: Restored.',
                self._get_relpath(outpath))
        else:
            runscript = FLEXX_SCRIPT.format(
                leadit_exec=self.leadit_exec, workdir=workdir,
                recpath=os.path.relpath(recpath, workdir),
                ligpath=ligpath, outpath=os.path.basename(outpath))
            if not self._run_script(runscript, workdir, run_logpath):
                log.fatal('FlexX script failed.')
                self._log_flexx_errors(run_logpath)
                return False
        if not os.path.exists(outpath):
            log.warning(
                'There is no FlexX result file `%s`.',
                self._get_relpath(outpath))
            self._log_flexx_errors(run_logpath)
            return False
        dockstruct = murdock.moldata.get_molstruct(outpath)
        if not dockstruct:
            log.error(
                'Docked molecular structure can not be retrieved from '
                'file `%s`.', self._get_relpath(outpath))
            self._log_flexx_errors(run_logpath)
            return False
        self._fix_flexx_struct(dockstruct)
        if not self._match_and_overwrite(lignode, dockstruct):
            self._log_flexx_errors(run_logpath)
            return False
        self._parse_score((recnode, lignode), run_logpath)
        self._log_flexx_errors(run_logpath)
        return True

    def _fix_flexx_struct(self, molstruct):
        return True

    def _get_mol2file(self, molstruct):
        sourcefile = molstruct.source
        ext = os.path.splitext(sourcefile.filepath)[1]
        if ext == '.mol2':
            mol2file = sourcefile
        else:
            mol2file = murdock.moldata.convert_to_file(
                molstruct, '.mol2', sort_atom_serials=True,
                sort_residue_serials=True, sort_chain_serials=False)
        mol2file.reduce_long_residue_names()
        return mol2file

    def _get_molstruct_and_file(self, node):
        molstruct = node.source.source.source
        mol2file = self._get_mol2file(molstruct)
        if not self._sybyl_types_used(mol2file):
            log.warning(
                'In `%s` there are no SYBYL atom types assigned. FlexX will '
                'not work properly without assigned SYBYL atom types.',
                mol2file.filepath)
            reffile = (
                molstruct.reference.source if molstruct.reference else None)
            if reffile and self._sybyl_types_used(reffile):
                log.warning(
                    'SYBYL atom types are copied from the reference file '
                    '`%s`.', reffile.filepath)
                lines = mol2file.dataline_dict['@<TRIPOS>ATOM']
                reflines = reffile.dataline_dict['@<TRIPOS>ATOM']
                for line, refline in zip(lines, reflines):
                    line.data[5] = refline.data[5]
        return molstruct, mol2file

    def _log_flexx_errors(self, run_logpath):
        errors = []
        try:
            with codecs.open(run_logpath, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            log.warning(
                'Can not read FlexX log file `%s`.',
                self._get_relpath(run_logpath))
            return False
        errors = [
            _l for _l in content.splitlines() if re.search('ERROR', _l) or
            re.search('WARNING', _l)]
        if not errors:
            return True
        log.warning(
            'Collected FlexX warnings and errors (`%s`):',
            self._get_relpath(run_logpath))
        for error in errors:
            log.warning('  [%s] %s', os.path.basename(run_logpath), error)
        return True

    def _match_and_overwrite(self, node, dockstruct):
        matches = murdock.molstruct.match_atoms(
            node.atoms, dockstruct.atoms(), match_serial=True, match_name=True)
        missing_in_old = [
            _a for _a in dockstruct.atoms() if _a not in matches.itervalues()]
        missing_in_docked = [
            _a for _a in node.atoms if _a not in matches.iterkeys()]
        dpath = self._get_relpath(dockstruct.source.filepath)
        if not matches or missing_in_docked:
            log.error(
                'Error during atom matching between original and '
                'docked stucture.')
            if missing_in_docked:
                log.error(
                    'The docked structure `%s` can not be used because the '
                    'following atoms have been removed by FlexX: %s.', dpath,
                    ', '.join(
                        '%d (`%s`)' % (_a.serial, _a.name) for _a in
                        missing_in_docked))
            return False
        if missing_in_old:
            log.warning(
                'The following atoms in `%s` have been added by FlexX and '
                'will be ignored: %s.', dpath, ', '.join([
                    '%d (`%s`)' % (_a.serial, _a.name) for _a in
                    missing_in_old]))
        for oldatom, dockatom in matches.iteritems():
            oldatom.coords = dockatom.coords.copy()
        return True

    def _get_relpath(self, filepath):
        """Return the ``filepath`` relative to the docking directory.
        """
        return os.path.relpath(
            filepath, os.path.join(self.docking.resdir, '../'))

    def _run_script(self, runscript, workdir, run_logpath):
        scriptname = 'run.bat'
        runscriptpath = os.path.join(workdir, scriptname)
        log.info('Run FlexX script `%s`.', self._get_relpath(runscriptpath))
        with codecs.open(runscriptpath, 'w', encoding='utf-8') as f:
            f.write(runscript)
        cmd = [self.leadit_exec, '-b', scriptname]
        try:
            with codecs.open(run_logpath, 'w', encoding='utf-8') as f:
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

    def _parse_score(self, nodes, run_logpath):
        try:
            with codecs.open(run_logpath, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            self.terms[0].values[nodes] = 0.
        else:
            lines = content.splitlines()
            i = 0
            for line in lines:
                i += 1
                if re.search('BATCH> soltab  n', line):
                    break
            score = float(lines[i].split()[1])
            self.terms[0].values[nodes] = score
        self.interactions.append(nodes)
        return True

    def _sybyl_types_used(self, mol2file):
        lines = mol2file.dataline_dict['@<TRIPOS>ATOM']
        return True in (len(_l.data[5].split('.')) > 1 for _l in lines)

    def _write_input_structs(self):
        recnode = None
        ligpaths = collections.OrderedDict()
        for child in self.root.children:
            if not child.static:
                continue
            if recnode is not None:
                raise scoring.ScoringError(
                    'This FlexX module supports only systems with one '
                    'static molecule.')
            recnode = child
            recstruct, recfile = self._get_molstruct_and_file(recnode)
        if recnode is None:
            raise scoring.ScoringError(
                'This FlexX module supports only systems with one fully '
                'static receptor.')
        for child in self.root.children:
            if child is recnode:
                continue
            lignode = child
            ligstruct, ligfile = self._get_molstruct_and_file(lignode)
            workdir = os.path.join(self.outdir, ligstruct.label)
            if not os.path.exists(workdir):
                os.makedirs(workdir)
            # Prepare and write receptor (including the binding site).
            recpath = os.path.join(
                self.outdir, workdir, '%s.mol2' % recstruct.label)
            if not self.blind:
                bsite = []
                bress = []
                recdists, ligdists = recnode.residue_distances(lignode)
                mindist = None
                log.info(
                    'Binding site (ligand-distance < %.1f Angstroem):',
                    self.margin)
                for res, dist in recdists.iteritems():
                    if dist < self.margin:
                        bsite.extend([_a.serial for _a in res.atoms])
                        bress.append(res)
                    if mindist is None or mindist > dist:
                        mindist = dist
                if not bsite:
                    log.error(
                        '  No atoms found. Shortest ligand distance: %.1f',
                        mindist)
                    return False
                bsite.sort()
                bress.sort(key=lambda x: x.serial)
                log.info(
                    '  Select %d atoms in %d residues: %s', len(bsite),
                    len(bress), ', '.join([
                        '%s%d' % (_res.name, _res.serial) for _res in bress]))
                rti = '@<TRIPOS>SET'
                line = murdock.moldata.mol2.Mol2DataLine(rti=rti)
                line.data = ['FLEXX_BINDING_SITE STATIC ATOMS <user>']
                recfile.add_dataline(line)
                lines = [murdock.moldata.mol2.Mol2DataLine(rti=rti)]
                line = lines[0]
                line.data = ['%d' % len(bsite)]
                num_lines = 2
                for dat in ('%d' % _serial for _serial in bsite):
                    if len(line.data[0]) + len(dat) > 77:
                        line.data[0] += '\\'
                        line = murdock.moldata.mol2.Mol2DataLine(rti=rti)
                        num_lines += 1
                        line.data = ['']
                        lines.append(line)
                    line.data[0] += ' %s' % dat
                for line in lines:
                    recfile.add_dataline(line)
            recfile.write(recpath, overwrite=True)
            if not self.blind:
                del recfile.dataline_dict[rti]
                recfile.datalines = recfile.datalines[:-num_lines]
            # Prepare and write ligand.
            ligpaths[lignode] = os.path.join(
                self.outdir, workdir, '%s.mol2' % ligstruct.label)
            ligfile.write(ligpaths[lignode], overwrite=True)
        return recnode, recpath, ligpaths


class Search(murdock.search.rescore.Search):
    pass


class ConfigDeclaration(murdock.config.ConfigDeclaration):

    def parameters(self):
        """Configuration options for this `flexx`-based scoring module:

            - "workdirname":
                name of working directory to be created within docking results
                directory `(dtype=str, default=flexx_work)`

            - "leadit_executable":
                path to the external `leadit` executable
                `(dtype=str, required=True)`

            - "blind":
                whether to perform a blind docking without using the docked
                solution from the last docking step
                `(dtype=bool, default=False)`

            - "margin":
                local search margin around an input ligand; not used in a blind
                docking (`dtype=float, default=10.0)`.

        """
        Option = murdock.config.ConfigOption
        opt = self.get_default_options()
        opt.append(Option(
            name='workdirname', dtype=basestring, description='name of '
            'working directory to be created', default='flexx_work'))
        opt.append(Option(
            name='leadit_executable', dtype=basestring, description='path to '
            'the external `leadit` executable', check_filepath=True))
        opt.append(Option(
            name='blind', dtype=bool, default=False, description='whether to '
            'perform a blind docking'))
        opt.append(Option(
            name='margin', dtype=murdock.misc.float_gt_zero, default=10.0,
            description='local search margin around an input ligand'))
        return opt


FLEXX_SCRIPT = """\
set max_nof_comp_to_dock 100

receptor
read {recpath}
end

ligand
read {ligpath}
end

docking
selbas a # Automatically select base frag.
placebas 3 # Place base frag. with triangle alg.
complex all # Add all fragments.
info y 0 # Output a summary table.
listsol 1 # Output best-scored info.
soltab y # Output column headers.
soltab n # Output best total score.
end

ligand
write {outpath} y y 1-1 n
end

delall y
quit y
"""
