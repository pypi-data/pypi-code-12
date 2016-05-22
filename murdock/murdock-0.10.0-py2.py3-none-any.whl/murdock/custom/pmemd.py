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
Module :mod:`murdock.custom.pmemd`
----------------------------------

A wrapper module for the software package `Amber` software package. It provides
the classes :class:`Search` and :class:`Scoring` which are conform with the
Murdock :mod:`~murdock.search` and :mod:`~murdock.scoring` APIs.

.. warning::

    This is a custom module working exclusively in the Pisabarro group due to
    the hard-coded setup script. However, it can be easily adapted for any
    other system with `Amber` or a similar molecular dynamics package
    installed.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import codecs
import collections
import logging
import os
import subprocess
import traceback

import murdock.config
import murdock.misc
import murdock.molstruct
import murdock.moldata
import murdock.scoring
import murdock.scoring.pool
import murdock.search.rescore


log = logging.getLogger('custom.pmemd')


class MatchingError(Exception):
    pass


class Scoring(murdock.scoring.Scoring):
    """Perform an Amber minimization and scoring.
    
    Receptor and ligand structures are written to a PDB file. These are loaded
    into ``tleap``, which writes the initial coordinates and `Amber` input
    files.  Then ``pmemd`` is called to mimimize the ligands (the receptor is
    strongly constrained). In a last step, the system is read from the output
    PDB file, and the minimized coordinates are written to the initial receptor
    and ligand structures by matching atoms.

    .. warning::

        To properly match input and output atoms, ``tleap`` must not add any
        atoms to the system.

    """

    def setup(self, parms, docking, name='pmemd', copy=False):
        #: minimization parameters, paths, terms and weights
        self.parms = parms
        #: name of this scoring method
        self.name = name
        #: :class:`~murdock.runner.docking.Docking` instance associated with
        #: this scoring
        self.docking = docking
        #: interpreter to call script
        self.interpreter = self.parms['interpreter']
        #: a list of lines added to the top of the leap input file
        self.header = parms['header']
        #: number of conjugate gradient iterations
        self.num_conjgrad = self.parms['num_conjugate_gradient_iterations']
        #: number of steepest descent iterations
        self.num_steepdesc = self.parms['num_steepest_descent_iterations']
        #: number of threads
        self.num_threads = self.docking.report.num_threads
        #: name of output directory
        self.outdir = None
        #: whether to restrain the receptor during minimization
        self.restrain_rec = self.parms['restrain_receptor']
        if len(self.root.children) == 1:
            self.outdir = os.path.join(
                self.docking.resdir, self.parms['workdirname'], 'unbonded',
                self.root.children[0].name)
        elif self.docking.current_run is not None:
            self.outdir = os.path.join(
                self.docking.resdir, self.parms['workdirname'],
                'run%05d' % self.docking.current_run.serial,
                'step%02d' % self.docking.current_step.serial)
        else:
            serial = len(self.docking.result.references) + 1
            self.outdir = os.path.join(
                self.docking.resdir, self.parms['workdirname'], 'reference',
                'step%02d' % serial)
        # Setup terms.
        for label, weight in parms['terms'].iteritems():
            term = murdock.scoring.pool.Manual()
            try:
                term.offset = -self.parms['unbonded_scores'][label]
            except KeyError:
                pass
            term.setup(name=label, weight=weight)
            self.add_term(term)
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)
        # Set `Node.static` attribute for unrestrained nodes.
        for child in self.root.children:
            molstruct = murdock.misc.get_source(
                child, src_type=murdock.molstruct.MolecularStructure)
            if molstruct.name == self.docking.receptor.name:
                if not self.restrain_rec:
                    child.set_as_dynamic()
            else:
                child.set_as_dynamic()
        if copy:
            return True
        # Write structure, perform `pmemd`-minimization and parse the output.
        if not self._minimize_and_score():
            return False
        return True

    def rescore(self, node=None):
        return 0

    def residue_scores(self, *args):
        return False, False

    def _minimize_and_score(self):
        """Write input structures, call script and read output structures.
        """
        log.info('Create `tleap` + `pmemd` shell script.')
        for atom in self.root.atoms:
            atom.source.source.coords = atom.coords.copy()
        mols = collections.OrderedDict()
        sorted_atoms = []
        if self.restrain_rec:
            restr_start, restr_end = None, None
        recnode = None
        for child in self.root.children:
            molstruct = murdock.misc.get_source(
                child, src_type=murdock.molstruct.MolecularStructure)
            if molstruct.name == self.docking.receptor.name:
                recnode = child
            if (
                    self.restrain_rec and
                    molstruct.name == self.docking.receptor.name):
                restr_start = len(sorted_atoms) + 1
            sorted_atoms.extend(molstruct.atoms())
            if (
                    self.restrain_rec and
                    molstruct.name == self.docking.receptor.name):
                restr_end = len(sorted_atoms)
                log.info(
                    '%d receptor atoms restrained during minimization.',
                    restr_end - restr_start + 1)
            sourcefile = molstruct.source
            ext = os.path.splitext(os.path.basename(sourcefile.filepath))[1]
            if ext == '.pdb':
                pdbfile = sourcefile
            else:
                pdbfile = murdock.moldata.convert_to_file(
                    molstruct, '.pdb', sort_atom_serials=True,
                    sort_residue_serials=True, sort_chain_serials=False)
            filename = '%s.pdb' % molstruct.label
            pdbfile.write(
                os.path.join(self.outdir, filename), drop_records='CONECT',
                overwrite=True)
            mols[molstruct.label] = filename
        inputstr = '\n'.join(
            '%s = loadpdb %s' % (_label, _mp) for _label, _mp in
            mols.iteritems())
        inputstr += '\nc = combine {%s}' % ' '.join(mols.keys())
        if recnode is not None and self.restrain_rec:
            restraints = (
                ' ntr = 1\n'
                ' restraint_wt = 1000.0\n'
                ' restraintmask = \\\"@%d-%d\\\",' % (restr_start, restr_end))
        else:
            restraints = ''
        # The `mpirun executable` needs to use at least two parallel processes.
        if self.num_threads is None or self.num_threads < 2:
            num_threads = 2
        elif len(self.root.atoms) / 10 < self.num_threads:
            num_threads = len(self.root.atoms) / 10
        else:
            num_threads = self.num_threads
        if self.header is None:
            strheader = ''
        else:
            strheader = '\n'.join(self.header)
        runscript = SHELLSCRIPT.format(
            header=strheader, inputstr=inputstr, restraints=restraints,
            nprocs=num_threads, ncyc=self.num_steepdesc,
            maxcyc=self.num_conjgrad + self.num_steepdesc)
        filepath = os.path.join(self.outdir, 'out.pdb')
        if os.path.exists(filepath):
            log.info('PMEMD output file `%s` found.', filepath)
            if (
                    self._copy_coords(filepath, mols, sorted_atoms) and
                    self._parse_energies()):
                log.info('Skip minimization.')
                return True
            else:
                log.info('File `%s` can not be used.', filepath)
        if not self._run_script(runscript):
            logpath = os.path.join(self.outdir, 'run.log')
            log.fatal(
                'Minimization failed. Check log files `%s`, `%s` and `%s`.',
                os.path.join(self.outdir, 'leap.log'), logpath,
                os.path.join(self.outdir, 'mdinfo'))
            return False
        if not self._copy_coords(filepath, mols, sorted_atoms):
            return False
        if not self._parse_energies():
            return False
        log.info('Minimization and scoring successful (`%s`).', self.outdir)
        return True

    def _copy_coords(self, filepath, mols, sorted_atoms):
        molstruct = murdock.moldata.get_molstruct(filepath)
        if not molstruct:
            log.fatal(
                'Minimized molecular structure can not be retrieved from PDB '
                'file `%s`.', filepath)
            return False
        if len(molstruct.atoms()) != len(sorted_atoms):
            log.fatal(
                'The minimized molecular structure (`%s`) has %d atoms '
                'whereas the input structures (%s) had %d atoms total. Make '
                'sure the minimization does not add or remove any atoms and '
                'check the input, output and log files for errors.',
                filepath, len(molstruct.atoms()), ', '.join(
                    '`%s`' % os.path.join(self.outdir, _fp) for _fp in
                    mols.itervalues()), len(sorted_atoms))
            return False
        # Sort residues by serial, atoms by name.
        for chain in molstruct.models[0].chains:
            chain.residues.sort(key=lambda r: r.serial)
            for res in chain.residues:
                res.atoms.sort(key=lambda a: a.name)
        for nodeatom, inatom in zip(sorted_atoms, molstruct.atoms()):
            if nodeatom.name != inatom.name:
                log.error(
                    'Error during atom matching between original and '
                    'minimized stucture. The last atoms to match were atom %d '
                    '(`%s`) and atom %d (`%s`).', nodeatom.serial,
                    nodeatom.name, inatom.serial, inatom.name)
                return False
            nodeatom.coords = inatom.coords.copy()
        for atom in self.root.atoms:
            atom.coords = atom.source_atom.coords.copy()
        return True

    def _run_script(self, runscript):
        logpath = os.path.join(self.outdir, 'run.log')
        runscriptpath = os.path.join(self.outdir, 'run.sh')
        log.info('Run shell script `%s` to minimize and score.', runscriptpath)
        with codecs.open(runscriptpath, 'w', encoding='utf-8') as f:
            f.write(runscript)
        cmd = [self.interpreter, 'run.sh']
        try:
            with open(logpath, 'w') as f:
                r = subprocess.call(cmd, stderr=f, stdout=f, cwd=self.outdir)
        except KeyboardInterrupt:
            raise
        except:
            errmsg = traceback.format_exc().splitlines()[-1]
            log.error('Error during script call: %s', errmsg)
            return False
        if r != 0:
            return False
        return True

    def _parse_energies(self):
        self.interactions = [(self.root, )]
        filepath = os.path.join(self.outdir, 'min.out')
        with codecs.open(filepath, 'r', encoding='utf-8') as f:
            pmemd = f.readlines()
        for term in self.terms:
            term.values = None
        ressection = False
        for line in pmemd:
            if line.strip() == 'FINAL RESULTS':
                ressection = True
                continue
            if ressection:
                for column in (line[:25], line[25:50], line[50:75]):
                    try:
                        label, value = column.split('=')
                    except ValueError:
                        continue
                    label = label.strip()
                    try:
                        value = float(value)
                    except ValueError:
                        continue
                    for term in self.terms:
                        if term.name == label:
                            term.values = {self.root: value}
        if not ressection:
            log.fatal(
                'No `FINAL RESULTS` section found in file `%s`. No scoring '
                'data available.', filepath)
            return False
        missing = [_term.name for _term in self.terms if _term.values is None]
        if missing:
            log.fatal(
                'There are invalid term values (%s) in the `FINAL RESULT` '
                'section of file `%s`.', ', '.join(
                    '`%s`' % _termname for _termname in missing), filepath)
            return False
        return True


class Search(murdock.search.rescore.Search):
    pass


class ConfigDeclaration(murdock.config.ConfigDeclaration):

    def parameters(self):
        """Configuration options for this `pmemd`-based scoring module:

            - "interpreter":
                filepath to shell interpreter `(dtype=str, required=True)`

            - "workdirname":
                name of working directory to be created within docking results
                directory `(dtype=str, required=True)`

            - "terms":
                dictionary of term labels and corresponding weights, such as
                ``{"BOND": 1.0, "VDWAALS": 0.5, "EEL": 0.3}`` etc.); these
                terms are extracted from the ``FINAL RESULTS`` section of the
                `pmemd` output file `(dtype=dict, required=True)`

            - "header":
                list of lines added to the leap input files (e.g. to import
                custom libraries `(dtype=list, required=False)`

        """
        Option = murdock.config.ConfigOption
        opt = self.get_default_options()
        opt.append(Option(
            name='interpreter', dtype=basestring, description='filepath to '
            'shell interpreter', required=True))
        default_header = [
            'source leaprc.GLYCAM_06h', 'source leaprc.GLYCAM_06h.sergeylibs',
            'source leaprc.ff12SB']
        opt.append(Option(
            name='header', dtype=list, validate=False,
            description='a list of lines added at the top of the leap input '
            'file', default=default_header))
        opt.append(Option(
            name='workdirname', dtype=basestring, description='name of '
            'working directory to be created', required=True))
        opt.append(Option(
            name='terms', dtype=dict, validate=False, description='dictionary '
            'of term labels to be extracted from the `pmemd` output file and '
            'their weights'))
        opt.append(Option(
            name='num_steepest_descent_iterations', dtype=int,
            description='number of steepest descent iterations',
            required=True))
        opt.append(Option(
            name='num_conjugate_gradient_iterations', dtype=int,
            description='number of conjugate gradient iterations',
            required=True))
        opt.append(Option(
            name='restrain_receptor', dtype=bool, default=True,
            description='whether to restrain the receptor during '
            'minimization'))
        return opt


SHELLSCRIPT = """
shopt -s expand_aliases

source \
/projects/bioinfp_apps/amber12_at13_centos58_intel1213_ompi164_cuda5/setup.sh

echo "Run TLEAP..."

echo "

{header}

{inputstr}

savepdb c initcoords.pdb
saveamberparm c top.prmtop initcoords.crd
quit
" | tleap -f - > /dev/null 2>&1

echo "TLEAP done."

echo "
steepest descent: ncyc, conjugate gradient: maxcyc-ncyc

&cntrl
 imin = 1,
 maxcyc = {maxcyc},
 ncyc = {ncyc},
 ntb = 0,
 igb = 5,
 cut = 16.0,
{restraints}
/
" > min.in

echo
echo "Run PMEMD..."
mpirun -np {nprocs} pmemd.MPI -O -i min.in -o min.out -p top.prmtop \
       -c initcoords.crd -r min.rst -ref initcoords.crd

if [ $? != 0 ]; then
    echo "Error during PMEMD run. Exit." 1>&2;
    exit 1
fi

echo "PMEMD done."

echo
echo "Write PDB file 'out.pdb'..."

ambpdb -p top.prmtop < min.rst > out.pdb

echo
echo "Script done."
"""
