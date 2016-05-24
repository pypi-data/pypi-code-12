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
Module :mod:`murdock.molstruct`
-------------------------------

A module to store and modify molecular structures.

Contains the following classes:
    - :class:`MolecularStructure`: Represents a molecular structure as a set of
      models.
    - :class:`Model`: Represents a molecular model as a set of chains.
    - :class:`Chain`: Respresents a chain as a set of residues.
    - :class:`Residue`: Respresents a residue as a set of atoms.
    - :class:`Atom`: Represents a single atom.
    - :class:`Bond`: Represents a molecular bond.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future.utils import viewitems

import logging
import re

import numpy

import murdock.config
import murdock.math
import murdock.misc


log = logging.getLogger('molstruct')


class MolecularStructureError(Exception):
    pass


class MolecularStructure(object):
    """A class to represent a molecular structure.
    """

    def __init__(
            self, serial=None, name=None, label=None, source=None,
            reference=None):
        #: molecule identifier (i.e. 4)
        self.serial = serial
        #: molecule name (i.e. 'Heparin Sulfate')
        self.name = name
        if label is not None:
            label = murdock.misc.cleanup_filename(label)
        elif name is not None:
            label = murdock.misc.cleanup_filename(name)
        #: molecule label used in result filenames (no special characters)
        self.label = label
        #: reference to a data source
        #: (i.e. a :class:`~murdock.moldata.pdb.PDBFile`)
        self.source = source
        #: list of :class:`Model` instances
        self.models = []
        #: reference class:`MolecularStructure` used for comparison purposes
        self.reference = reference

    def __str__(self):
        return (
            'Type: {ctype}\nSource: {source}\nserial: {serial}\nName: {name}\n'
            'Number of models: {num_models}\nNumber of chains: {num_chains}\n'
            'Number of residues: {num_residues}\n'
            'Number of atoms: {num_atoms}\n'.format(
                ctype=type(self), serial=self.serial, name=self.name,
                num_models=len(self.models), num_chains=len(self.chains()),
                num_residues=len(self.residues()), num_atoms=len(self.atoms()),
                source=type(self.source)))

    def add_model(self, model):
        model.structure = self
        self.models.append(model)
        return model

    def atoms(self):
        """Return a list of all atoms within this structure.
        """
        return [_a for _a in self.iterate_atoms()]

    def bonds(self):
        """Return a list of all bonds in the :class:`MolecularStructure`.
        """
        if len(self.models) == 1:
            return self.models[0].bonds
        bonds = []
        for model in self.models:
            bonds.extend(model.bonds)
        return bonds

    def chains(self):
        """Return a list of all chains within the structure.
        """
        return [_c for _c in self.iterate_chains()]

    def iterate_atoms(self):
        """Iterate over all atoms of this structure
        """
        for model in self.models:
            for atom in model.iterate_atoms():
                yield atom

    def iterate_chains(self):
        """Iterate over all chains within the structure.
        """
        for model in self.models:
            for chain in model.chains:
                yield chain

    def iterate_residues(self):
        """Iterate over all residues within the structure.
        """
        for model in self.models:
            for residue in model.iterate_residues():
                yield residue

    def residues(self):
        """Return a list of all residues within the structure.
        """
        return [_r for _r in self.iterate_residues()]

    def select(
            self, model_serials=None, chain_serials=None, residue_serials=None,
            atom_serials=None, model_names=None, chain_names=None,
            residue_names=None, atom_names=None):
        """Return a list of atoms with the corresponding properties.

        All parameters are `None` or lists of serials or names. Each atom whose
        (model/chain/...) serials or names are in the corresponding lists are
        added to the selection and returned.

        Usage Example::

            atoms = molstruct.select(
                residue_serials=[1,2,3], atom_names=['CA'])

        (Return a list of all atoms named 'CA' within residues 1, 2 and 3.)

        """
        atoms = []
        for model in self.models:
            if model_serials and model.serial not in model_serials:
                continue
            if model_names and model.name not in model_names:
                continue
            for chain in model.chains:
                if chain_serials and chain.serial not in chain_serials:
                    continue
                if chain_names and chain.name not in chain_names:
                    continue
                for residue in chain.residues:
                    if (
                            residue_serials and residue.serial not in
                            residue_serials):
                        continue
                    if residue_names and residue.name not in residue_names:
                        continue
                    for atom in residue.atoms:
                        if atom_serials and atom.serial not in atom_serials:
                            continue
                        if atom_names and atom.name not in atom_names:
                            continue
                        atoms.append(atom)
        return atoms

    def set_serials(self):
        """Renumber models, chains, residues and atoms in :attr:`structure`.
        """
        mod_index = 0
        for mod in self.models:
            chain_index = 0
            res_index = 0
            atom_index = 0
            mod_index += 1
            mod.serial = mod_index
            for chain in mod.chains:
                chain_index += 1
                chain.serial = chain_index
                for res in chain.residues:
                    res_index += 1
                    res.serial = res_index
                    for atom in res.atoms:
                        atom_index += 1
                        atom.serial = atom_index


class Model(object):
    """A class to represent a model of a molecular structure.

    Attributes:
        serial -- Model identifier.
        name -- Model name.
        source -- Original identifier from the input file.
        chains[] -- List of chains.
        structure -- Reference to the containing `MolecularStructure` instance.

    """

    def __init__(self, serial=None, name=None, source=None, structure=None):
        #: model identifier
        self.serial = serial
        #: model name
        self.name = name
        #: data source
        self.source = source
        #: :class:`MolecularStructure` containing this model
        self.structure = structure
        #: list of chains (:class:`Chain`) within this model
        self.chains = []
        #: list of bonds (:class:`Bond`) within this model
        self.bonds = []

    def __str__(self):
        return (
            'Type: {ctype}\nSource: {source}\nSerial: {serial}\nName: '
            '{name}\nChains: {num_chains:d}\nResidues: {num_res:d}\n'
            'Atoms: {num_atoms:d}\n'.format(
                ctype=type(self), serial=self.serial, name=self.name,
                num_chains=len(self.chains), num_res=len(self.residues()),
                num_atoms=len(self.atoms()), source=type(self.source)))

    def add_chain(self, chain):
        chain.model = self
        self.chains.append(chain)
        return chain

    def atoms(self):
        """Return a list of all atoms within this model.
        """
        return [_a for _a in self.iterate_atoms()]

    def iterate_atoms(self):
        """Iterate over all atoms within this model.
        """
        for chain in self.chains:
            for atom in chain.iterate_atoms():
                yield atom

    def iterate_residues(self):
        """Iterate over all residues within this model.
        """
        for chain in self.chains:
            for residue in chain.residues:
                yield residue

    def residues(self):
        """Return a list of all all residues within this model.
        """
        return [_r for _r in self.iterate_residues()]


class Chain(object):
    """A class to represent a chain within a molecule.

    Attributes:
        `serial` -- Chain identifier.
        `name` -- Chain name.
        `source` -- Original identifier from the input file.
        `residues` -- List of residues.

    """

    def __init__(self, serial=None, name=None, source=None, model=None):
        self.serial = serial
        self.name = name
        self.source = source
        self.model = model
        self.residues = []

    def __str__(self):
        return (
            'Type: {ctype}\nSource: {source}\nSerial: {serial}\nName: {name}\n'
            'Number of residues: {num_residues:d}\n'
            'Number of atoms: {num_atoms:d}\n'.format(
                ctype=type(self), serial=self.serial, name=self.name,
                num_residues=len(self.residues), num_atoms=len(self.atoms()),
                source=type(self.source)))

    def add_residue(self, residue):
        """Add :class:`Residue` to self.
        """
        residue.chain = self
        self.residues.append(residue)
        return residue

    def atoms(self):
        """Return a list of all atoms within this chain.
        """
        return [_a for _a in self.iterate_atoms()]

    def iterate_atoms(self):
        """Iterate over all atoms within this chain.
        """
        for residue in self.residues:
            for atom in residue.atoms:
                yield atom

    def bonds(self):
        bonds = []
        for atom in self.iterate_atoms():
            bonds.extend([
                _b for _b in atom.bonds if _b not in bonds and
                _b.atoms[0].residue.chain is self and
                _b.atoms[1].residue.chain is self])
        return bonds


class Residue(object):
    """A class to represent a residue within a molecule.

    """

    def __init__(self, serial=None, name=None, source=None, chain=None):
        #: residue identifier
        self.serial = serial
        #: residue name
        self.name = name
        #: reference to data source (i.e. a
        #: :class:`~murdock.moldata.pdb.PDBRecord`)
        self.source = source
        #: parent :class:`Chain` of this residue
        self.chain = chain
        #: list of :class:`Atom` instances within this residue
        self.atoms = []

    def __str__(self):
        return (
            'Type: {ctype}\nSource: {source}\nSerial: {serial}\nName: {name}\n'
            'Number of Atoms: {num_atoms:d}\n'.format(
                ctype=type(self), serial=self.serial, name=self.name,
                num_atoms=len(self.atoms), source=type(self.source)))

    def add_atom(self, atom):
        """Add :class:`Atom` to self.
        """
        atom.residue = self
        self.atoms.append(atom)
        return atom

    def bonds(self):
        bonds = []
        for atom in self.atoms:
            bonds.extend([
                _b for _b in atom.bonds if _b not in bonds and
                _b.atoms[0].residue is self and _b.atoms[1].residue is self])
        return bonds


class Atom(object):
    """A class to represent a single atom.

    """

    def __init__(
            self, serial=None, name=None, element=None, source=None,
            coords=None, part_charge=None, form_charge=None, vdw_radius=None,
            residue=None):
        #: atom identifier (i.e. 103)
        self.serial = serial
        #: atom name (i.e. 'CA')
        self.name = name
        #: element (i.e. 'C')
        self.element = element
        #: cartesian coordinates
        self.coords = numpy.array(coords, numpy.float64)
        if coords is None:
            self.coords = numpy.array([None, None, None], numpy.float64)
        #: partial charge of the atom (i.e. 0.54)
        self.part_charge = part_charge
        #: format charge of the atom (i.e. -1)
        self.form_charge = form_charge
        #: optional reference to a data source (i.e. an `ATOM`
        #: :class:`~murdock.moldata.pdb.PDBRecord` from a
        #: :class:`~murdock.moldata.pdb.PDBFile`)
        self.source = source
        #: original source atom (used if the atom is deepcopied to maintain
        #: access to residue-, chain- or other source information; the atom
        #: is only referenced, not copied)
        self.source_atom = self
        #: reference to the parent :class:`Residue`
        self.residue = residue
        #: list of molecular :class:`Bond` instances (two atoms share one
        #: :class:`Bond` instance)
        self.bonds = []
        #: list of bonded :class:`Atom` instances
        self.bonded = []
        #: dictionary of :attr:`bonds` indexed by :class:`Atom` instance
        self.bonds_by_atom = {}
        #: van-der-Waals radius
        self.vdw_radius = vdw_radius

    def __str__(self):
        return (
            'Type: {ctype}\nSource: {source}\nSerial: {serial}\nName: {name}\n'
            'Element: {element}\n'
            'Cartesian coordinates in Angstroem: {x} {y} {z}\n'
            'Partial charge: {part_charge}\nFormal charge: {form_charge}\n'
            'Bonded to (atom serials): {bonded}\n'.format(
                ctype=type(self), serial=self.serial, name=self.name,
                element=self.element, x=self.coords[0], y=self.coords[1],
                z=self.coords[2], part_charge=self.part_charge,
                form_charge=self.form_charge, source=type(self.source),
                bonded=', '.join([
                    '%d(`%s`)' % (_a.serial, _a.name) for _a in self.bonded])))

    def add_bond(self, bond):
        if self is bond.atoms[0]:
            atom = bond.atoms[1]
        elif self is bond.atoms[1]:
            atom = bond.atoms[0]
        else:
            raise MolecularStructureError(
                'A `Bond` instance can only be added to an `Atom` instance '
                'after the `Atom` has been added to the `Bond.atoms` list.')
        if bond in self.bonds:
            raise MolecularStructureError(
                'The same `Bond` instance can not be added to an `Atom` '
                'instance twice.')
        self.bonds.append(bond)
        if atom not in self.bonded:
            self.bonded.append(atom)
        try:
            self.bonds_by_atom[atom].append(bond)
        except KeyError:
            self.bonds_by_atom[atom] = [bond]
        return True

    def connected(self, no_go=None):
        """List all connected atoms ordered by the number of links from `self`.

        The list includes all atoms somehow connected to `self`, first `self`
        itself (for convenience in some usage cases), then all directly bonded
        atoms, then all atoms connected by two links, then by three and so on.
        The parameter `no_go` is a list of atoms at which the iteration through
        the bond structure is stopped.

        Starting from `self` the bond structure is iterated using the
        :attr:`~murdock.molstruct.Atom.bonds`. To build an
        :class:`~murdock.molstruct.Atom` list in order of links, a number of
        walkers go through the bond structure step by step. For each bonded
        atom a new walker is created to walk through the new branch. The
        :class:`~murdock.molstruct.Atom` list `walkers` holds the current
        atoms (current position of each walker). The
        :class:`~murdock.molstruct.Atom` list `visited` holds all atoms
        already visited by walkers. No walker steps back on an atom included in
        `visited` and hence always walk forward until it reaches the end. When
        all walkers have finished (no way to walk without touching `visited`),
        the list `visited` is returned holding all atoms connected to `self` in
        order of link number.

        The parameter `no_go` is a list of atoms which are to be avoided by the
        walkers. This way a direction from `self` can be blocked, i.e. to
        retrieve a branch/list of atoms on one side of `self` only.

        Usage Example:

            Let `node` be a :class:`~murdock.Node`. First, the root atom is
            picked::

                root = node.find_root()

            A random bonded atom is picked::

                neighbor = root.bonded[0]

            A list of all atoms i) connected to `root` and ii) on the opposing
            side/branch of neighbor is retrieved::

                sidebranch = root.connected(no_go=[neighbor,])

        """
        visited = []
        if no_go is None:
            no_go = []
        visited.append(self)
        walkers = [_a for _a in self.bonded if _a not in no_go]
        while True:
            next_walkers = []
            for atom in walkers:
                visited.append(atom)
                batoms = [
                    _batom for _batom in atom.bonded if (
                        _batom not in visited and _batom not in no_go and
                        _batom not in next_walkers)]
                if batoms:
                    next_walkers.extend(batoms)
            if next_walkers:
                walkers = next_walkers[:]
            else:
                return visited

    def deepcopy(self):
        """Return a deepcopy of this atom.

        The original atom is set as :attr:`source` for the copied atom.

        """
        new_atom = Atom(
            serial=self.serial, name=self.name, element=self.element,
            source=self, part_charge=self.part_charge,
            form_charge=self.form_charge, vdw_radius=self.vdw_radius)
        new_atom.coords = self.coords.copy()
        if self.source_atom is not None:
            new_atom.source_atom = self.source_atom
        return new_atom

    def get_bonded(
            self, num_bonds=None, min_bonds=None, max_bonds=None, skip=None):
        """Return a list of atoms connected to `self` by a :class:`Bond`.

        If `num_bonds` > 1, not the directly bonded atoms but a list of atoms
        connected by exactely `num_bonds` is returned. If `max_bonds` is given,
        all atoms bonded by less or equal than that number of bonds are retured
        (correspondingly for `min_bonds`).  The parameter `skip` is a list of
        atoms to be skipped (not added to `bonded`) which is mainly used for
        recursive calls of :meth:`get_bonded()`.

        """
        if num_bonds is not None and max_bonds is not None:
            raise MolecularStructureError(
                'Parameters `num_bonds` and `max_bonds` are exclusive.')
        if num_bonds is not None and min_bonds is not None:
            raise MolecularStructureError(
                'Parameters `num_bonds` and `min_bonds` are exclusive.')
        if num_bonds is None and max_bonds is None and min_bonds is None:
            num_bonds = 1
        elif num_bonds is None and min_bonds is None:
            min_bonds = max_bonds
        elif num_bonds is None and max_bonds is None:
            max_bonds = min_bonds
        if skip is None:
            skip = []
        skip.append(self)
        bonded = []
        for batom in self.bonded:
            if batom in skip:
                continue
            if num_bonds is None and max_bonds >= min_bonds:
                bonded.extend([
                    _atom for _atom in batom.get_bonded(
                        max_bonds=max_bonds-1, min_bonds=min_bonds, skip=skip)
                    if _atom not in bonded])
                if batom not in bonded:
                    bonded.append(batom)
            if num_bonds is not None:
                if num_bonds > 1:
                    bonded.extend([_atom for _atom in batom.get_bonded(
                        num_bonds=num_bonds-1, skip=skip) if _atom not in
                        bonded])
                elif batom not in bonded:
                    bonded.append(batom)
        return bonded


class Bond(object):
    """A class to represent a molecular bond.

    A list of :class:`Bond` instances can be assigned as attribute to each
    :class:`Atom` instance. It contains information on the bond :attr:`type`
    and of course to which :attr:`atom` the bond connects to. Every physical
    bond should be described by two :class:`Bond` instances, one for each atom.

    """

    def __init__(self, name=None, btype=None, atoms=None, angle=None,
                 unbonded=None, rotatable=False):
        #: `name` of the bond (e.g. `covalent`)
        self.name = name
        #: type of the bond (e.g. `single`, `double`, `amide`, `aromatic`)
        self.btype = btype
        #: list of two :class:`Atom` instances which are connected by this bond
        self.atoms = atoms
        #: unbonded angle (e.g. to calculate torsional angle deviations)
        self.unbonded = unbonded
        #: list of four atoms defining the torsional angle
        self.tors_atoms = None
        #: whether this bond is rotatable in docking
        self.rotatable = rotatable

    def deepcopy(self, atoms, tors_atoms=None, suffix=''):
        """Return a deepcopy where :attr:`atom` is replaced by new `atoms`.

        The replacement of :attr:`atoms` is necessary when atoms are copied '
        into a new system.

        """
        new_bond = Bond(
            atoms=atoms, name='%s%s' % (self.name, suffix), angle=self.angle,
            unbonded=self.unbonded, rotatable=self.rotatable)
        if tors_atoms is not None:
            new_bond.set_torsatoms(tors_atoms)
        return new_bond

    def inring(self, max_bonds=10):
        return True in (
            self.atoms[0] in _ba.bonded for _ba in
            self.atoms[1].get_bonded(
                min_bonds=2, max_bonds=max_bonds, skip=[self.atoms[0]]))

    def set_torsatoms(self, atoms):
        if len(atoms) != 4:
            raise MolecularStructureError(
                'The method `Bond.set_torsatoms()` requires a list of four '
                '`Atom` instances as argument.')
        if self.atoms[0] not in atoms[1:3] or self.atoms[1] not in atoms[1:3]:
            raise MolecularStructureError(
                'List elements 2 and 3 given to `Bond.set_torsatoms()` must '
                'be the two `Bond.atoms`.')
        self.tors_atoms = atoms

    def angle(self):
        """Return the torsional angle defined by four bonded atoms.
        """
        return murdock.math.torsional_angle(
            self.tors_atoms[0].coords, self.tors_atoms[1].coords,
            self.tors_atoms[2].coords, self.tors_atoms[3].coords)


class AtomParameterLibrary(object):
    """Class holding dictionaries of external atom parameters.
    """

    def __init__(self):
        pass

    def vdw_radii(self):
        """Van-der-Waals radii.

        Source: `The Cambridge Crystallographic Data Centre`

        .. seealso:: www.ccdc.cam.ac.uk/products/csd/radii

        """
        return {
            'H': 1.2, 'C': 1.7, 'N': 1.55, 'O': 1.52, 'F': 1.47, 'P': 1.8,
            'S': 1.8, 'Cl': 1.75, 'Co': 1.4, 'Ca': 2.0}


ATOM_PARAMETER_LIBRARY = AtomParameterLibrary()


def get_bonds(bonds, receptor, select=None):
    """Filter and return a list of ``bonds``.

    The selection syntax is destribed in
    :meth:`~murdock.molstruct.ConfigDeclaration.select`. If ``select``
    is ``None``, all bonds are returned.

    """
    validkeys = ['bond_name', 'molecule_type', 'atoms', 'rotatable']
    validatomkeys = [
        'molecule', 'atom_name', 'atom_serial', 'element', 'residue_name',
        'residue_serial', 'chain_name', 'chain_serial']

    def re_match(pattern, string):
        m = re.match(pattern, string)
        if m and len(set(m.span())) > 1:
            return True
        else:
            return False

    def match(s, atom):
        if atom.source_atom is not None:
            atom = atom.source_atom
        for key, val in viewitems(s):
            if key not in validatomkeys:
                log.fatal(
                    'Unknown key `%s` in dictionary `atoms`. Known keys '
                    'are: %s.', key, ', '.join(validkeys))
                return False
            if key == 'molecule' and not re_match(
                    val, atom.residue.chain.model.structure.label):
                return False
            if key == 'atom_name' and not re_match(val, atom.name):
                return False
            if key == 'atom_serial' and not re_match(
                    str(val), str(atom.serial)):
                return False
            if key == 'element' and not re_match(val, atom.element):
                return False
            if key == 'residue_name' and not re_match(val, atom.residue.name):
                return False
            if (
                    key == 'residue_serial' and not
                    re_match(str(val), str(atom.residue.serial))):
                return False
            if key == 'chain_name' and not re_match(
                    val, atom.residue.chain.name):
                return False
            if (
                    key == 'chain_serial' and not
                    re_match(str(val), str(atom.residue.chain.serial))):
                return False
        return True
    # Apply defaults.
    if not select:
        select = [dict()]
    for sel in select:
        for atkey in validatomkeys:
            if 'atoms' not in sel:
                sel['atoms'] = [dict() for _ in range(4)]
            if atkey in sel:
                for atom in sel['atoms']:
                    if atkey not in atom:
                        atom[atkey] = sel[atkey]
            if atkey in sel:
                del sel[atkey]
    # Select bonds.
    selbonds = []
    for isel, sel in enumerate(select):
        for key, val in viewitems(sel):
            if key not in validkeys:
                log.fatal(
                    'Unknown key `%s` in item %d of list `select`. Known '
                    'keys are: %s.', key, isel + 1, ', '.join(validkeys))
                return False
        if len(sel['atoms']) != 4:
            log.fatal('Each selection must include a list of four atoms.')
            return False
        if (
                receptor and ('molecule_type' not in sel or
                sel['molecule_type'] not in ('receptor', 'all'))):
            continue
        if (
                not receptor and 'molecule_type' in sel and
                sel['molecule_type'] == 'receptor'):
            continue
        for bond in bonds:
            if bond in selbonds:
                continue
            for a2, a3 in (bond.atoms, bond.atoms[::-1]):
                if not (
                        match(sel['atoms'][1], a2) and
                        match(sel['atoms'][2], a3)):
                    continue
                for ba2, ba3 in (
                        (_ba2, _ba3) for _ba2 in a2.bonded if _ba2 is not a3
                        for _ba3 in a3.bonded if _ba3 is not a2):
                    if (
                            match(sel['atoms'][0], ba2) and
                            match(sel['atoms'][3], ba3)):
                        a1, a4 = ba2, ba3
                        break
                else:
                    continue
                if (
                        ('rotatable' not in sel or sel['rotatable']) and
                        bond.inring()):
                    continue
                bond.set_torsatoms([a1, a2, a3, a4])
                if 'bond_name' in sel:
                    bond.name = sel['bond_name']
                elif None not in (a1.name, a2.name, a3.name, a4.name):
                    bond.name = '%s-%s-%s-%s' % (
                        a1.name, a2.name, a3.name, a4.name)
                elif None not in (
                        a1.element, a2.element, a3.element, a4.element):
                    bond.name = '%s-%s-%s-%s' % (
                        a1.element, a2.element, a3.element, a4.element)
                else:
                    bond.name = 'bond_%d' % bond.serial
                selbonds.append(bond)
                break
    return selbonds


def get_center(atoms):
    """Return coordinate center of atoms (not weighted).
    """
    c = numpy.array([0., 0., 0.])
    for a in atoms:
        c += a.coords
    return c / len(atoms)


def get_center_atom(atoms):
    """Return atom closest to the coordinate center of atoms.
    """
    center = get_center(atoms)
    center_atom = None
    min_dist = None
    for atom in atoms:
        dist = numpy.linalg.norm(atom.coords - center)
        if min_dist is None or min_dist > dist:
            center_atom = atom
            min_dist = dist
    return center_atom


def match_atoms(atoms1, atoms2, match_serial=False, match_name=False,
                match_residue_name=False, match_residue_serial=False,
                match_chain_name=False, match_chain_serial=False):
    """Return a mapping of `atoms1` onto `atoms2` based on certain attributes.

    The dictionary returned has the form `{atom1:atom2, ...}` where `atom1` and
    `atom2` share the same attributes (e.g. :attr:`Atom.serial` or
    :attr:`Atom.name`).

    """
    if not match_serial and not match_name:
        raise MolecularStructureError(
            'Can not match atoms because `match_serial` and `match_name` are '
            'both False')
    matches = {}
    for atom2 in atoms2:
        for atom1 in atoms1:
            if match_serial and atom1.serial != atom2.serial:
                continue
            if match_name and atom1.name != atom2.name:
                continue
            if (
                    match_residue_name or match_residue_serial or
                    match_chain_name or match_chain_serial):
                if atom1.residue is not None:
                    res1 = atom1.residue
                else:
                    res1 = atom1.source_atom.residue
                if atom2.residue is not None:
                    res2 = atom2.residue
                else:
                    res2 = atom2.source_atom.residue
                if match_residue_name and res1.name != res2.name:
                    continue
                if match_residue_serial and res1.serial != res2.serial:
                    continue
            if match_chain_name or match_chain_serial:
                if res1.chain is not None:
                    chain1 = res1.chain
                else:
                    chain1 = res1.source_residue.chain
                if res2.chain is not None:
                    chain2 = res2.chain
                else:
                    chain2 = res2.source_residue.chain
                if match_chain_name and chain1.name != chain2.name:
                    continue
                if match_chain_serial and chain1.serial != chain2.serial:
                    continue
            if atom1 in matches:
                log.fatal(
                    'Ambiguous matching of atoms! In file `%s` there are two '
                    'atoms %d (`%s`) with residue name `%s` in lines %d and '
                    '%d.', atom1.source_atom.source.source.filepath,
                    atom1.serial, atom1.name, atom1.source_atom.residue.name,
                    atom1.source_atom.source.line_number,
                    atom2.source_atom.source.line_number)
                return {}
            matches[atom1] = atom2
    return matches


def radius(atoms):
    """Return the largest atom distance from the center.
    """
    center = get_center(atoms)
    max_dist = 0
    for atom in atoms:
        d = numpy.linalg.norm(atom.coords - center)
        if d > max_dist:
            max_dist = d
    return max_dist


def set_center(atoms, center):
    """Set center of atoms to new coordinates `center`.
    """
    diff = center - get_center(atoms)
    for atom in atoms:
        atom.coords += diff
    return True


class ConfigDeclaration(murdock.config.ConfigDeclaration):

    def arguments(self):
        """Configuration options for the default rotatable bond selection.

        Default options from
        :meth:`~murdock.config.ConfigDeclaration.get_default_options` are used.

            - "select":
                a list of :meth:`selection criteria
                <murdock.molstruct.ConfigDeclaration.select>`
                `(dtype=list, required=False)`

        The criteria given in
        :meth:`~murdock.molstruct.ConfigDeclaration.select` are applied to all
        bonds in the system. A bond will be selected and named based on the
        first match in in the list.

        Example I:

        Select all torsional bonds in all ligands::

          "rotatable_bonds": {}

        Example II:

        Select bonds `phi` and `psi` based on the names of their torsional
        atoms. Five of the atoms use regular expression syntax (e.g. `O[34]`
        matches `O3` and `O4`)::

          "rotatable_bonds": {
            "arguments": {
              "select": [
                {
                  "bond_name": "phi",
                  "atoms": [
                    {"atom_name": "O5"},
                    {"atom_name": "C1"},
                    {"atom_name": "O[34]},
                    {"atom_name": "C[34]}
                  ]
                },
                {
                  "bond_name": "psi",
                  "atoms": [
                    {"atom_name": "C1"},
                    {"atom_name": "O[34]"},
                    {"atom_name": "C[34]"},
                    {"atom_name": "C[23]"}
                  ]
                }
              ]
            }
          }

        Example III:

        Select bonds `phi3`, `phi4`, `psi3` and `psi4` based on the names of
        their torsional atoms. Select all other rotatable bonds using the last
        empty dictionary {} (use default names)::

          "rotatable_bonds": {
            "arguments": {
              "select": [
                {
                  "bond_name": "phi3",
                  "atoms": [
                    {"atom_name": "O5"},
                    {"atom_name": "C1"},
                    {"atom_name": "O3"},
                    {"atom_name": "C3"}
                  ]
                },
                {
                  "bond_name": "phi4",
                  "atoms": [
                    {"atom_name": "O5"},
                    {"atom_name": "C1"},
                    {"atom_name": "O4"},
                    {"atom_name": "C4"}
                  ]
                },
                {
                  "bond_name": "psi3",
                  "atoms": [
                    {"atom_name": "C1"},
                    {"atom_name": "O3"},
                    {"atom_name": "C3"},
                    {"atom_name": "C2"}
                  ]
                },
                {
                  "bond_name": "psi4",
                  "atoms": [
                    {"atom_name": "C1"},
                    {"atom_name": "O4"},
                    {"atom_name": "C4"},
                    {"atom_name": "C3"}
                  ]
                },
                {}
              ]
            }
          }

        Example IV:

        Select the CD-CE bonds in each Lysine in the receptor::

          "rotatable_bonds": {
            "arguments": {
              "select": [
                {
                  "molecule_type": "receptor",
                  "residue_name": "LYS",
                  "atoms": [
                    {"atom_name": "CG"},
                    {"atom_name": "CD"},
                    {"atom_name": "CE"},
                    {"atom_name": "N*"}
                  ]
                }
              ]
            }
          }

        """
        Option = murdock.config.ConfigOption
        opt = self.get_default_options()
        opt.append(Option(
            name='select', dtype=list, required=False,
            description='a list of selection criteria'))
        return opt

    def select(self):
        """Configuration options for the selection of bonds.

            - "bond_name":
                name given to bonds from this selection
                `(dtype=str, required=False)`

            - "molecule_type":
                select only bonds in molecules of this type: either `receptor`,
                `ligand` or `all` `(dtype=str, default=ligand)`

            - "rotatable":
                only select bonds which allow torsional rotation
                `(dtype=bool, default=True)`

            - "atoms":
                a list of four atoms defining the torsion angle
                `(dtype=list, length=4, required=False)`

        All configuration options (selection criteria) for
        :meth:`~murdock.molstruct.ConfigDeclaration.atoms` can also be
        placed in this section. They are used as default for all atoms (does
        not override options given directly for an atom).

        """
        Option = murdock.config.ConfigOption
        opt = self.atoms()
        opt.append(Option(
            name='bond_name', dtype=Option.string,
            description='name given to bonds from this selection',
            required=False))
        opt.append(Option(
            name='molecule_type', dtype=Option.string,
            description='either `receptor`, `ligand` or `all`',
            default='ligand'))
        opt.append(Option(
            name='rotatable', dtype=bool, default=True,
            description='only select bonds which allow torsional rotation'))
        opt.append(Option(
            name='atoms', dtype=list, length=4, required=False,
            description='a list of four atoms defining the torsional angle'))
        return opt

    def atoms(self):
        """Configuration options for an atom selection.

        Default options from
        :meth:`~murdock.config.ConfigDeclaration.get_default_options` are used.

            - "element":
                atom element as read from input file
                `(dtype=str, required=False)`

            - "atom_name":
                atom name `(dtype=str, required=False)`

            - "atom_serial":
                atom serial number `(dtype=int, required=False)`

            - "residue_name":
                residue name `(dtype=str, required=False)`

            - "residue_serial":
                residue serial number `(dtype=int, required=False)`

            - "chain_name":
                chain name `(dtype=str, required=False)`

            - "chain_serial":
                chain serial number `(dtype=int, required=False)`

            - "molecule":
                molecule label as given in
                :meth:`murdock.runner.docking.ConfigDeclaration.moldata
                `(dtype=str, required=False)`

        All atoms matching the given criteria are selected. None of the options
        is required, criteria not given are not considered for the selection.
        For all of the above options, `regular expression syntax
        <https://docs.python.org/2/library/re.html>`_ can be used.

        """
        Option = murdock.config.ConfigOption
        opt = self.get_default_options()
        opt.append(Option(
            name='atom_name', dtype=Option.string, required=False,
            description='atom name'))
        opt.append(Option(
            name='atom_serial', dtype=Option.string, required=False,
            description='atom serial number'))
        opt.append(Option(
            name='residue_name', dtype=Option.string, required=False,
            description='residue name'))
        opt.append(Option(
            name='residue_serial', dtype=Option.string, required=False,
            description='residue serial number'))
        opt.append(Option(
            name='chain_name', dtype=Option.string, required=False,
            description='chain name'))
        opt.append(Option(
            name='chain_serial', dtype=Option.string, required=False,
            description='chain serial number'))
        opt.append(Option(
            name='molecule', dtype=Option.string, required=False,
            description='molecule label as given in configuration file'))
        return opt
