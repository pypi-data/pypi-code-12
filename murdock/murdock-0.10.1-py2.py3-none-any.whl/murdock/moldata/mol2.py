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
Module :mod:`murdock.moldata.mol2`
----------------------------------

This module handles Mol2 files.

The format description can be found at http://tripos.com/data/support/mol2.pdf

From the format description:
`A Tripos Mol2 file (.mol2) is a complete, portable representation of a SYBYL
molecule. It is an ASCII file which contains all the information needed to
reconstruct a SYBYL molecule.`

The class :class:`File` holds all Mol2 data in a list of
:class:`Mol2DataLine` instances. It offers methods to parse and write data to
and from its instances. This class is the public interface.

Most format specific definitions (record names, data types) are found
in :class:`Mol2RecordLibrary`.

The classes :class:`FileToMolecularStructure` and
:class:`MolecularStructureToFile` are private functions containing methods
to convert data between :class:`File` and
:class:`~murdock.molstruct.MolecularStructure` instances.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import range

import codecs
import logging
import os

import murdock.misc
import murdock.molstruct


log = logging.getLogger('moldata.mol2')


class Mol2Error(Exception):
    pass


class Mol2DataLine(object):
    """A class to represent a single data line of a Mol2 file."""

    def __init__(
            self, source=None, line_number=None, rti=None, mol_serial=None,
            data=None):
        #: a reference to the source Mol2 file
        self.source = source
        #: the line number in the source Mol2 file
        self.line_number = line_number
        #: the record type indicator (`@<TRIPOS>ATOM`, @<TRIPOS>BOND, ...)
        self.rti = rti
        #: molecule serial (if multiple molecules are defined within a file, '
        #: a new molecule data block is started by `@<TRIPOS>MOLECULE`)
        self.mol_serial = mol_serial
        #: a list to hold the Mol2 data, each entry corresponds to a data field
        self.data = []
        if data is not None:
            self.data = data

    def __str__(self):
        d = ', '.join(['{0:s}'.format(str(_dat)) for _dat in self.data])
        try:
            filepath = self.source.filepath
        except AttributeError:
            filepath = None
        return (
            'Type: {ctype}\n'
            'Source file: {filepath} (mol2)\n'
            'Line number in source file: {line_number}\n'
            'Data: {data_str}\n'.format(
                ctype=type(self), tag=self.rti, filepath=filepath,
                line_number=self.line_number, data_str=d))


class File(object):
    """A class to represent the Mol2 file content on a high abstraction level.

    It includes methods to :meth:`parse()` a Mol2 file to a :class:`File`
    instance and - vice versa - to :meth:`write()` Mol2 files.

    """

    def __init__(self, filepath=None):
        #: file to be parsed
        self.filepath = filepath
        #: list of :class:`Mol2DataLine` instances
        self.datalines = []
        #: dictionary mapping a record :attr:`~Mol2DataLine.rti` to a list of
        #: all corresponding :class:`Mol2DataLine` instances found in
        #: :attr:`datalines`.
        self.dataline_dict = {}
        #: a string holding the full raw file content
        self.raw_lines = None

    def __str__(self):
        dataline_list = ''.join(
            '{0:>30s}: {1:>5d}\n'.format(_k, len(_r)) for _k, _r in
            self.dataline_dict.items())
        return (
            'Type: {ctype}\n'
            'Mol2 filepath: `{filepath}`\n'
            'DataLine entries:\n{dl}'.format(
                ctype=type(self), filepath=self.filepath, dl=dataline_list))

    def add_dataline(self, dataline):
        """Add a :class:`Mol2DataLine` instance to :attr:`dataline_dict`.
        """
        if dataline.rti not in self.dataline_dict:
            self.dataline_dict[dataline.rti] = []
        self.dataline_dict[dataline.rti].append(dataline)
        self.datalines.append(dataline)
        return True

    def coords_from_molstruct(self, atoms):
        """Overwrite coordinates with the ones found in `atoms`.
        """
        ms_to_mol2 = MolecularStructureToFile(self)
        return ms_to_mol2.replace_coordinates(atoms)

    def from_molstruct(self, molstruct, **kwargs):
        return MolecularStructureToFile(molstruct).convert(self)

    def reduce_long_residue_names(self):
        try:
            for dl in self.dataline_dict['@<TRIPOS>ATOM']:
                dl.data[7] = _reduce_long_residue_name(dl.data[7])
        except KeyError:
            pass
        try:
            for dl in self.dataline_dict['@<TRIPOS>SUBSTRUCTURE']:
                dl.data[1] = _reduce_long_residue_name(dl.data[1])
        except KeyError:
            pass

    def parse(self):
        """Parse the Mol2 file.

        For each line in :attr:`filepath` a new :class:`Mol2DataLine` is added
        to the :class:`File` using the method :meth:`_parse_line`. The
        `line_number + 1` is passed to :meth:`_parse_line` to make sure lines
        start at 1, not 0. `rti` keeps track of the current record. Only
        records defined in :class:`Mol2RecordLibrary` are used.

        """
        if not self.filepath:
            raise Mol2Error('`File` instance has no input filepath.')
        # Guarantee closing of the file handle after reading.
        with codecs.open(self.filepath, 'r', encoding='utf-8') as f:
            self.raw_lines = f.readlines()
        rti = None
        full_line = ''
        mol_serial = 0
        for line_number, line in enumerate(self.raw_lines):
            # Skip empty lines and comments.
            if not line.strip() or line.startswith('#'):
                continue
            # Check for new record type indicator (RTI).
            if line.startswith('@<TRIPOS>'):
                rti = line.strip()
                # Check for new molecule.
                if rti == '@<TRIPOS>MOLECULE':
                    mol_serial += 1
                if rti not in MOL2_RECORD_TYPES:
                    log.info('Mol2 record `%s` is ignored.', rti)
                continue
            # If RTI is not defined, skip.
            if rti not in MOL2_RECORD_TYPES:
                continue
            # Join continued lines.
            full_line = ' '.join((full_line, line.strip())).strip()
            # Catch empty lines and continuation characters.
            if not line.strip() or line.strip().split()[-1] == '\\':
                continue
            # Parse data line.
            if not self._parse_line(
                    full_line, line_number + 1, rti, mol_serial):
                log.warning('Line %d skipped.', line_number + 1)
            full_line = ''
        return True

    def to_molstruct(self):
        """Convert into a :class:`~murdock.molstruct.MolecularStructure`.

        """
        return FileToMolecularStructure(self).convert()

    def write(
            self, filepath, overwrite=False, keep_records=None,
            drop_records=None):
        """Write a :class:`File` instance to `filepath`.

        :param str filepath: output filepath/filename
        :param bool overwrite: set `True` to overwrite existing file
        :param list keep_records: list of Mol2 RTIs to be written
        :param list drop_records: list of Mol2 RTIs NOT to be written

        If neither `keep_records` nor `drop_records` is given, all
        :attr:`records` are written to `filepath`. The arguments
        `keep_records` and `drop_records` are exclusive: To write only selected
        records, use `keep_records`. To keep all but selected records, use
        `drop_records`. Records are specified by their
        :attr:`~Mol2DataLine.rti`.

        - Usage Example 1::

            mol2.write('path/to/filename.mol2',
                       keep_records=['@<TRIPOS>ATOM', '@<TRIPOS>SUBSTRUCTURE'])

        - Usage Example 2::

            mol2.write('path/to/filename.mol2',
                       drop_records=['@<TRIPOS>COMMENT', '@<TRIPOS>BOND'])

        If `overwrite` is set to `true`, any existing file will be overwritten.

        """
        if keep_records and drop_records:
            raise Mol2Error(
                'Arguments `keep_records` and `drop_records are exclusive!')
        if os.path.isfile(filepath) and not overwrite:
            log.error(
                'File `%s` already exists. Set `overwrite=True` to delete '
                'existing file.', filepath)
            return False
        lines = []
        rti = None
        for line_number, dataline in enumerate(self.datalines):
            if keep_records and dataline.rti not in keep_records:
                continue
            elif drop_records and dataline.rti in drop_records:
                continue
            if dataline.rti != rti:
                rti = dataline.rti
                lines.append(''.join([rti, '\n']))
                formatters = MOL2_RECORD_FORMATTERS[rti]
                types = MOL2_RECORD_TYPES[rti]
            line = []
            for i, (dat, form, typ) in enumerate(
                    zip(dataline.data, formatters, types)):
                if dat is None:
                    line.append('{dat:^{w}s}'.format(dat='****', w=4))
                    continue
                field = '{0:%s}' % form
                try:
                    line.append(field.format(dat))
                except ValueError:
                    log.error(
                        'Output error in file `%s`, record `%s` in line '
                        '%d. Field %d (`%s`) has type `%s`. Required for '
                        'Mol2 standard is type `%s`. Field will be '
                        'written as string and might not correspond to '
                        'Mol2 format.', filepath, dataline.rti,
                        line_number, i + 1, str(dat), type(dat), str(typ))
                    line.append('{dat:>{w}s}'.format(
                        dat=str(dat), w=len(str(dat))))
            strline = ' '.join(line) + '\n'
            lines.append(strline)
        if self.raw_lines is None:
            self.raw_lines = lines
        with codecs.open(filepath, 'w', encoding='utf-8') as f:
            f.write(''.join(lines))
        return True

    def _parse_line(self, line, line_number, rti, mol_serial):
        """Parse a line from a Mol2 file. If a valid data line is identified,
        add it to `self.dataline_dict`.

        :param line: a line (string) read from a (Mol2) file
        :param line_number: the line number
        :param rti: record type indicator to which the line belongs
        :returns: True (valid Mol2 data line detected) or False

        """
        types = MOL2_RECORD_TYPES[rti]
        required = MOL2_RECORD_REQUIRED[rti]
        dataline = Mol2DataLine(source=self, line_number=line_number, rti=rti)
        fields = line.split()
        # Check for correct number of fields.
        if len(fields) != len(types):
            num_req_fields = 0
            for req in required:
                if req:
                    num_req_fields += 1
            if num_req_fields > len(fields):
                log.error(
                    'Wrong number of data fields in file `%s`, line '
                    '%d. At least %d fields expected for `%s` but found %d '
                    'instead.', self.filepath, line_number, num_req_fields,
                    rti, len(fields))
                return False
        for i, (field, typ, req) in enumerate(zip(fields, types, required)):
            if field == '****':
                if req:
                    log.error(
                        'Missing required field in RTI `%s`, file `%s`, line '
                        '%d, field number %d. Expected %d. Field is skipped.',
                        rti, self.filepath, line_number, i + 1, str(typ))
                dataline.data.append(None)
                continue
            try:
                dataline.data.append(typ(field))
            except ValueError:
                log.error(
                    'TypeError in file `%s`, line %d, field number %d. '
                    'Expected `%s` but found `%s`. Field can not be '
                    'interpreted and is skipped.', self.filepath, line_number,
                    i, str(typ), field)
                dataline.data.append(None)
        dataline.mol_serial = mol_serial
        self.add_dataline(dataline)
        return True


class MolecularStructureToFile(object):
    """Convert data from a :class:`~murdock.molstruct.MolecularStructure`
       to a :class:`File`.

    """
    def __init__(self, source):
        #: :class:`murdock.molstruct.MolecularStructure` instance
        self.source = source

    def convert(self, mol2file):
        ln = lambda: len(mol2file.datalines) + 1
        for imol, mol in enumerate(self.source.models):
            rti = '@<TRIPOS>MOLECULE'
            mol2file.add_dataline(Mol2DataLine(
                source=mol, line_number=len(mol2file.datalines)+1, rti=rti,
                mol_serial=imol+1, data=[self.source.name]))
            mol2file.add_dataline(Mol2DataLine(
                source=mol, line_number=len(mol2file.datalines)+1, rti=rti,
                mol_serial=imol+1, data=[
                    '%d' % len(mol.atoms()), '%d' % len(mol.bonds),
                    '%d' % (len(mol.residues()) + len(mol.chains))]))
            mol2file.add_dataline(Mol2DataLine(
                source=mol, line_number=len(mol2file.datalines)+1, rti=rti,
                mol_serial=imol+1, data=['SMALL']))
            mol2file.add_dataline(Mol2DataLine(
                source=mol, line_number=len(mol2file.datalines)+1, rti=rti,
                mol_serial=imol+1, data=['USER_CHARGES']))
            rti = '@<TRIPOS>ATOM'
            tps = MOL2_RECORD_TYPES[rti]
            chnames = [_c.name for _c in mol.chains]
            if len(chnames) > len(set(chnames)):
                log.info(
                    'Chains do not have unique names and need to be renamed.')
                namechains = True
            else:
                namechains = False
            resserials = [_r.serial for _r in mol.iterate_residues()]
            if len(resserials) > len(set(resserials)):
                log.info(
                    'Residues do not have unique serials and need to be '
                    'renumbered.')
                numserials = True
            else:
                numserials = False
            atserials = [_a.serial for _a in mol.iterate_atoms()]
            if len(atserials) > len(set(atserials)):
                log.info(
                    'Atoms do not have unique serials and need to be '
                    'renumbered.')
                numatoms = True
            else:
                numatoms = False
            serial = 0
            atserial = 0
            atomdict = {}
            for i_ch, chain in enumerate(
                    sorted(mol.chains, key=lambda _c: _c.serial)):
                for res in sorted(chain.residues, key=lambda _r: _r.serial):
                    if numserials:
                        serial += 1
                    else:
                        serial = res.serial
                    for atom in sorted(res.atoms, key=lambda _a: _a.serial):
                        if numatoms:
                            atserial += 1
                        else:
                            atserial = atom.serial
                        atomdict[atom] = atserial
                        mol2file.add_dataline(Mol2DataLine(
                            source=atom, line_number=ln(), rti=rti,
                            mol_serial=imol+1, data=[
                                atom.serial, atom.name, atom.coords[0],
                                atom.coords[1], atom.coords[2], atom.element,
                                serial, res.name, atom.part_charge, '']))
            rti = '@<TRIPOS>BOND'
            tps = MOL2_RECORD_TYPES[rti]
            for i, bond in enumerate(mol.bonds):
                serials = sorted([bond.atoms[0].serial, bond.atoms[1].serial])
                dl = Mol2DataLine(
                    source=bond, line_number=ln(), rti=rti, mol_serial=imol+1,
                    data=[i + 1, serials[0], serials[1], '1'])
                if bond.atoms[0].residue is not bond.atoms[1].residue:
                    dl.data.append('INTERRES')
                mol2file.add_dataline(dl)
            rti = '@<TRIPOS>SUBSTRUCTURE'
            tps = MOL2_RECORD_TYPES[rti]
            serial = 0
            maxserial = 0
            for i_ch, chain in enumerate(
                    sorted(mol.chains, key=lambda _c: _c.serial)):
                if namechains:
                    ch_name = '%d' % (i_ch + 1)
                else:
                    ch_name = chain.name
                for res in sorted(chain.residues, key=lambda _r: _r.serial):
                    if numserials:
                        serial += 1
                    else:
                        serial = res.serial
                    if serial > maxserial:
                        maxserial = serial
                    mol2file.add_dataline(Mol2DataLine(
                        source=res, line_number=ln(), rti=rti,
                        mol_serial=imol+1, data=[
                            serial, res.name, res.atoms[0].serial,
                            'RESIDUE', 1, ch_name]))
            for i_ch, chain in enumerate(
                    sorted(mol.chains, key=lambda _c: _c.serial)):
                if namechains:
                    ch_name = '%d' % (i_ch + 1)
                else:
                    ch_name = chain.name
                serial = maxserial + i_ch + 1
                mol2file.add_dataline(Mol2DataLine(
                    source=chain, line_number=ln(), rti=rti, mol_serial=imol+1,
                    data=[
                        serial, ch_name, atomdict[chain.residues[0].atoms[0]],
                        'GROUP', 1, ch_name]))
        return True

    def replace_coordinates(self, atoms):
        """Replace coordinates in all `@<TRIPOS>ATOM` data lines of the
        :attr:`source`.

        For all `atoms`, the :attr:`~murdock.molstruct.Atom.source`
        attribute must reference the corresponding
        :class:`~murdock.moldata.mol2.Mol2DataLine` in the :attr:`source`
        file.

        """
        if type(atoms).__name__ == 'generator':
            atoms = [_a for _a in atoms]
        for atom in atoms:
            if atom.source_atom.source in self.source.datalines:
                atom.source_atom.source.data[2:5] = atom.coords[0:3]
        return True


class FileToMolecularStructure(object):
    """Convert data from a :class:`File` to a
    :class:`~murdock.molstruct.MolecularStructure`.

    """

    def __init__(self, source):
        #: source :class:`File`
        self.source = source
        #: new target :class:`~murdock.molstruct.MolecularStructure`
        self.structure = murdock.molstruct.MolecularStructure(source=source)
        #: dictionary mapping the molecule and substructure serial to
        #: the corresponding `SUBSTRUCTURE` :class:~`Mol2DataLine`.
        self.sub_dict = {}
        #: dictionary mapping a chain from a Mol2 record to the corresponding
        #: target :class:`~murdock.molstruct.Chain`
        self.chain_dict = {}
        #: dictionary mapping a residue from a Mol2 record to the corresponding
        #: target :class:`~murdock.molstruct.Residue`
        self.residue_dict = {}
        #: dictionary mapping molecule and atom serial to an
        #: :class:`~murdock.molstruct.Atom`
        self.atom_dict = {}

    def convert(self):
        """Convert a :class:`File` to a
        :class:`~murdock.molstruct.MolecularStructure`.

        So far the following Mol2 records are used:
            `@<TRIPOS>ATOM`, `@<TRIPOS>SUBSTRUCTURE`, `@<TRIPOS>BOND`
        """
        if '@<TRIPOS>ATOM' not in self.source.dataline_dict:
            log.fatal(
                'Can not convert file `%s` into a molecular structure. There '
                'are no atoms!', self.source.filepath)
            return False
        self.sub_dict = self._substructure_dict()
        model = self._add_model()
        for atom_dl in self.source.dataline_dict['@<TRIPOS>ATOM']:
            if not self._add_atom(atom_dl, model):
                return False
        if '@<TRIPOS>BOND' in self.source.dataline_dict:
            for bond_dl in self.source.dataline_dict['@<TRIPOS>BOND']:
                if not self._add_bond(bond_dl):
                    log.warning('Bond can not be added.')
        else:
            log.warning(
                'No bond records (@<TRIPOS>BOND) in file `%s`.',
                self.source.filepath)
        self.structure.name = (
            os.path.splitext(os.path.basename(self.source.filepath))[0])
        return self.structure

    def _add_atom(self, dataline, model):
        """Add a new :class:`~murdock.molstruct.Atom` to `model`.

        The `@<TRIPOS>ATOM `dataline` points to a `@<TRIPOS>SUBSTRUCTURE`
        :class:`Mol2DataLine` which is passed to :meth:`_set_chain` and
        :meth:`_set_residue` to set the target chain and residue. A new
        :class:`~murdock.molstruct.Atom` is created, retrieves some
        attributes from the :attr:`Mol2DataLine.data` in `dataline` and is
        added to the correct model, chain and residue of :attr:`structure`.

        """
        # If `dataline` does not provide any substructural information, the
        # atom from `dataline` is put into model.chains[-1].residues[-1].
        if len(dataline.data) < 7:
            chain = self._set_chain(Mol2DataLine(), model)
            residue = self._set_residue(Mol2DataLine(), chain)
        else:
            # Select the target chain in `model` using `dataline`
            chain = self._set_chain(
                self.sub_dict[(dataline.mol_serial, dataline.data[6])], model)
            # Select the target residue in `chain` using `dataline`
            residue = self._set_residue(
                self.sub_dict[(dataline.mol_serial, dataline.data[6])], chain)
        # Create a new atom using data from `dataline`
        atom = murdock.molstruct.Atom(source=dataline)
        atom.serial = dataline.data[0]
        atom.name = dataline.data[1]
        atom.coords[0] = dataline.data[2]
        atom.coords[1] = dataline.data[3]
        atom.coords[2] = dataline.data[4]
        atom.element = dataline.data[5].split('.')[0]
        try:
            atom.part_charge = dataline.data[8]
        except IndexError:
            raise
        # Add atom to the target residue
        if (dataline.mol_serial, atom.serial) in self.atom_dict:
            key = (dataline.mol_serial, atom.serial)
            log.error(
                'Two atoms (found in lines %d and %d of file `%s`) have the '
                'same serial (%d). Atom serials in MOL2 files need to be '
                'unique.', self.atom_dict[key].source.line_number,
                dataline.line_number, dataline.source.filepath, atom.serial)
            return False
        residue.add_atom(atom)
        self.atom_dict[(dataline.mol_serial, atom.serial)] = atom
        return True

    def _add_bond(self, dataline):
        """Add a new :class:`~murdock.molstruct.Bond` using `dataline`.
        """
        try:
            atom = self.atom_dict[(dataline.mol_serial, dataline.data[1])]
        except KeyError:
            log.error(
                'Wrong `@<TRIPOS>BOND` data in line %d of file `%s`. Atom '
                'serial %d does not point to any atom read from the '
                '`@<TRIPOS>ATOM` record!', dataline.line_number,
                dataline.source.filepath, dataline.data[1])
            return False
        try:
            batom = self.atom_dict[(dataline.mol_serial, dataline.data[2])]
        except KeyError:
            log.error(
                'Wrong `@<TRIPOS>BOND` data in line %d of file `%s`. Atom '
                'serial %d does not point to any atom read from the '
                '`@<TRIPOS>ATOM` record!', dataline.line_number,
                dataline.source.filepath, dataline.data[2])
            return False
        btype = dataline.data[3]
        bond = murdock.molstruct.Bond(btype=btype, atoms=[atom, batom])
        atom.add_bond(bond)
        batom.add_bond(bond)
        self.structure.models[0].bonds.append(bond)
        return True

    def _add_model(self, dataline=None):
        """Add a new :class:`~murdock.molstruct.Model` to :attr:`structure`.
        """
        model = murdock.molstruct.Model()
        if dataline:
            model.source = dataline
        if not self.structure.models:
            model.serial = 0
        else:
            model.serial = len(self.structure.models)
        self.structure.add_model(model)
        return model

    def _set_chain(self, dataline, model):
        """Interpret a `@<TRIPOS>SUBSTRUCTURE` dataline to identify a chain.

        If the data field providing the chain is empty, the last chain added to
        `model` is returned instead.

        If the chain serial retrieved from the `dataline` does not exist, the
        chain is created, added to the :attr:`structure` and referenced in
        :attr:`chain_dict`.

        :returns: the chain identified from the `dataline`

        """
        if len(dataline.data) < 6 or not dataline.data[5]:
            if not model.chains:
                model.add_chain(murdock.molstruct.Chain(
                    source=dataline, serial=1, name='1'))
            return model.chains[-1]
        ch_name = dataline.data[5]
        if ch_name not in self.chain_dict:
            chain = murdock.molstruct.Chain(
                source=dataline, serial=len(model.chains)+1,
                name=dataline.data[5])
            model.add_chain(chain)
            self.chain_dict[ch_name] = chain
            return chain
        return self.chain_dict[ch_name]

    def _set_residue(self, dataline, chain):
        """Interpret an `@<TRIPOS>SUBSTRUCTURE` dataline to identify a residue.

        It is not checked whether the substructure type is `RESIDUE`. Instead
        every substructure :class:`Mol2DataLine` is interpreted as a residue.

        If the residue serial retrieved from the `dataline` does not exist, the
        residue is created, added to the :attr:`structure` and referenced in
        :attr:`residue_dict`.

        :returns: the residue identified from the `dataline`

        """
        res_serial = dataline.data[0]
        name = dataline.data[1]
        if res_serial not in self.residue_dict:
            residue = murdock.molstruct.Residue(
                source=dataline, serial=res_serial, name=name)
            chain.add_residue(residue)
            self.residue_dict[res_serial] = residue
            return residue
        return self.residue_dict[res_serial]

    def _substructure_dict(self):
        """Return a dictionary mapping the molecule and substructure serial to
        the corresponding `SUBSTRUCTURE` :class:~`Mol2DataLine`.

        """
        subd = {}
        # Add regular substructure entries.
        if '@<TRIPOS>SUBSTRUCTURE' in self.source.dataline_dict:
            for dl in self.source.dataline_dict['@<TRIPOS>SUBSTRUCTURE']:
                serials = (dl.mol_serial, dl.data[0])
                if serials in subd:
                    log.error(
                        'Duplicate substructure serials found in '
                        '`@<TRIPOS>SUBSTRUCTURE`! Only the first substructure '
                        'of the same serial will be used.')
                    continue
                subd[serials] = dl
        else:
            log.info('No substructures defined in `%s`.', self.source.filepath)
        # Add missing substructures.
        for dl in self.source.dataline_dict['@<TRIPOS>ATOM']:
            serials = (dl.mol_serial, dl.data[6])
            if serials not in subd:
                log.info(
                    'Create missing substructure entry %d (`%s`) from '
                    'ATOM record.', dl.data[6], dl.data[7])
                subd[serials] = Mol2DataLine(
                    mol_serial=dl.mol_serial, rti=['@<TRIPOS>SUBSTRUCTURE'])
                subd[serials].data = [dl.data[6], dl.data[7], dl.data[0]]
        return subd


class Mol2RecordLibrary(object):
    """ Stores format specifications needed to interpret Mol2 records.

    Each data line in a Mol2 file belongs to a certain Record Type Indicator
    (RTI) and holds the corresponding data fields. Each data field has a
    specific type (string, integer, float)

    This class provides a library of those Mol2 record RTIs and data fields
    which are needed to create a
    :class:`~murdock.molstruct.MolecularStructure`. All specifications
    correspond to http://tripos.com/data/support/mol2.pdf.

    Input and output methods (:meth:`File.parse` and :meth:`File.write`)
    both use this library to set and verify type and format of data fields
    within a Mol2 file.

    """

    def __init__(self):
        #: stores data conversion functions (:func:`int`, :func:`float`, ...)
        self.types = {}
        #: stores typographic and numerical format (alignment, digits, ...)
        self.formatters = {}
        #: stores whether a field is required for a certain record
        self.required = {}
        self.types, self.formatters, self.required = self._fill_library()

    def _fill_library(self):
        """ Return the actual format specifications.

        For each RTI, there is an item in each of the dictionaries
        :attr:`types`, :attr:`formatters` and :attr:`required`.

        The dictionary :attr:`types` contains a tuple of function names. The
        parser applies these functions to the data string extracted from a
        field via slicing in order to validate the data. Invalid data is
        expected to raise a :exc:`ValueError` during parsing. Those data
        type verification functions are built-in functions like :func:`int`,
        :func:`float`. If needed, custom functions could be used as well.

        The dictionary :attr:`formatters` contains a tuple of Python format
        strings to be used in :func:`File.write`. Alignment, data type and
        numerical format have to be specified manually (i.e. ``>10.3f`` for a
        right-justified float with 3 digits precision and a field width of 10).
        Missing entries in `formatters` are set to left-justified string of
        width 10 (``<10s``).

        The dictionary :attr:`required` contians a tuple of bool variables
        specifying whether a field is required or not. If a required field is
        missing, :func:`File.parse` prints an error and skips the input
        line. Missing entries in :attr:`required` are set to `False` (not
        required).

        """
        ffloat = murdock.misc.finitefloat
        types = {}
        formatters = {}
        required = {}
        types['@<TRIPOS>ATOM'] = (
            int, str, ffloat, ffloat, ffloat, str, int, str, ffloat, str)
        formatters['@<TRIPOS>ATOM'] = (
            '>6d', '<4s', '>10.3f', '>10.3f', '>10.3f', '<5s', '>5d', '<5s',
            '>6.3f', '<8s')
        types['@<TRIPOS>BOND'] = (int, int, int, str, str)
        required['@<TRIPOS>BOND'] = (True, True, True, True, False)
        formatters['@<TRIPOS>BOND'] = ('>5d', '>5d', '>5d', '<s', '<s')
        types['@<TRIPOS>MOLECULE'] = [str for _ in range(100)]
        required['@<TRIPOS>MOLECULE'] = [True]
        required['@<TRIPOS>MOLECULE'].extend([False for _ in range(100)])
        types['@<TRIPOS>SET'] = (str, )
        types['@<TRIPOS>SUBSTRUCTURE'] = [
            int, str, int, str, int, str, str, int]
        types['@<TRIPOS>SUBSTRUCTURE'].extend([str for _ in range(100)])
        formatters['@<TRIPOS>SUBSTRUCTURE'] = [
            '>5d', '<6s', '>6d', '<7s', '<d', '<4s', '<s', '<d']
        formatters['@<TRIPOS>SUBSTRUCTURE'].extend(['<s' for _ in range(100)])
        required['@<TRIPOS>SUBSTRUCTURE'] = [
            True, True, True, False, False, False, False, False]
        required['@<TRIPOS>SUBSTRUCTURE'].extend([False for _ in range(100)])
        # Set all field to NOT required, unless manually set above.
        for key, dtype in types.items():
            if key not in required:
                required[key] = [False for _ in dtype]
        # Set all fields to left-justified strings, unless manually set above.
        for key, dtype in types.items():
            if key not in formatters:
                formatters[key] = ['<10s' for _ in dtype]
        return types, formatters, required


MOL2_RECORD_LIBRARY = Mol2RecordLibrary()
MOL2_RECORD_TYPES = MOL2_RECORD_LIBRARY.types
MOL2_RECORD_FORMATTERS = MOL2_RECORD_LIBRARY.formatters
MOL2_RECORD_REQUIRED = MOL2_RECORD_LIBRARY.required


def _reduce_long_residue_name(resname):
    if len(resname) <= 3:
        return resname
    if True in [_l.isdigit() for _l in resname[:3]]:
        return resname[:3]
    if resname[0] in ('N', 'C') and len(resname) > 3:
        return resname[1:4]
    return resname
