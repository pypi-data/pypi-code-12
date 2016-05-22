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
Module :mod:`murdock.modata.pdb`
--------------------------------

This module handles PDB files.

The PDB file format is defined and maintained by the RCSB Protein Data Bank to
store and exchange structural molecular data. Detailed information and the
format definition can be retrieved at `<http://www.wwpdb.org/docs.html>`_. This
module is based on PDB file format 3.3.

The class :class:`File` holds all PDB data in a list of :class:`PDBRecord`
instances. It is used to parse and write data from and to PDB files. Most
format specific definitions (record names, columns, data types) are found in
:class:`PDBRecordLibrary`. The classes :class:`FileToMolecularStructure` and
:class:`MolecularStructureToFile` are used to convert data between
:class:`File` and :class:`~murdock.molstruct.MolecularStructure` instances.

.. seealso:: The easiest way to parse a PDB file and convert it to a
             :class:`~murdock.molstruct.MolecularStructure` is to use the
             :mod:`~murdock.moldata.moldata` API.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import codecs
import logging
import os

import murdock.molstruct
import murdock.misc


log = logging.getLogger('moldata.pdb')


class PDBError(Exception):
    pass


class PDBRecordLibraryError(Exception):
    pass


class PDBRecord(object):
    """A class to represent a single record (line) of a PDB file."""

    def __init__(self, name=None, source=None, lnumber=None):
        #: a reference to the source PDB :class:`File`
        self.source = source
        #: the line number in the source PDB file
        self.lnumber = lnumber
        #: the PDB record name (`REMARK`, `ATOM`, `CONECT`, ...)
        self.name = name
        #: a list to hold the PDB data, each entry corresponds to a data field
        self.data = []

    def __str__(self):
        d = ' '.join(['%s' % _d for _d in self.data])
        return (
            'Type: {ctype}\nSource file: `{filepath}` (pdb)\n'
            'Line number in source file: {lnumber}\n'
            'Data: `{data_str}`\n'.format(
                ctype=type(self), tag=self.name, filepath=self.source.filepath,
                lnumber=self.lnumber, data_str=d))


class File(object):
    """A class to represent the PDB file content on a high abstraction level.

    It includes functions to :meth:`parse` a PDB file to a :class:`File`
    instance and - vice versa - to :meth:`write` PDB files.

    """

    def __init__(self, filepath=None):
        #: file to be parsed
        self.filepath = filepath
        #: list of :class:`PDBRecord` instances
        self.records = []
        #: dictionary mapping a record :attr:`~PDBRecord.name` to a list of
        #: all corresponding :class:`PDBRecord` instances found in
        #: :attr:`records`.
        self.rec_dict = {}
        #: a string holding the full raw file content
        self.raw_lines = None

    def __str__(self):
        l = [
            '{0:>15s}: {1:>5d}\n'.format(_k, len(_r)) for _k, _r in
            self.rec_dict.items()]
        rec_list = ' '.join(l)
        return (
            'Type: {ctype}\nPDB filepath: `{filepath}`\n'
            'Record entries:\n{recs}'.format(
                ctype=type(self), filepath=self.filepath, recs=rec_list))

    def add_record(self, rec):
        """Add a :class:`PDBRecord` instance to :attr:`rec_dict`.
        """
        if rec.name not in self.rec_dict:
            self.rec_dict[rec.name] = []
        self.rec_dict[rec.name].append(rec)
        self.records.append(rec)
        return True

    def atoms_from_molstruct(self, atoms):
        """Call :meth:`MolecularStructureToFile.replace_atoms()`.
        """
        ms_to_pdb = MolecularStructureToFile(self)
        return ms_to_pdb.replace_atoms(atoms)

    def coords_from_molstruct(self, atoms):
        """Overwrite coordinates with the ones found in `atoms`.
        :attr:`~murdock.molstruct.Atom.coords`.
        """
        ms_to_pdb = MolecularStructureToFile(self)
        return ms_to_pdb.replace_coordinates(atoms)

    def from_molstruct(self, molstruct, **kwargs):
        """Create file from :class:`~murdock.molstruct.MolecularStructure`.
        """
        return MolecularStructureToFile(molstruct).convert(self, **kwargs)

    def parse(self):
        """Parse the PDB file.

        For each line in :attr:`filepath` a new :class:`PBDRecord` is added to
        the :class:`File` using the method :meth:`_parse_line`. The
        `lnumber + 1` is passed to :meth:`_parse_line` to make sure lines
        start at 1, not 0.

        """
        if not self.filepath:
            raise PDBError('`File` instance has no input filepath.')
        with codecs.open(self.filepath, 'r', encoding='utf-8') as f:
            self.raw_lines = f.readlines()
        for lnumber, line in enumerate(self.raw_lines):
            if not self._parse_line(line, lnumber + 1):
                log.info('Line %d skipped.', lnumber + 1)
        return True

    def residues_from_molstruct(self, residues):
        """Call :meth:`MolecularStructureToFile.replace_residues()`.
        """
        ms_to_pdb = MolecularStructureToFile(self)
        return ms_to_pdb.replace_residues(residues)

    def to_molstruct(self):
        """Convert into a :class:`~murdock.molstruct.MolecularStructure`.
        """
        return FileToMolecularStructure(self).convert()

    def write(self, filepath, overwrite=False,
              keep_records=None, drop_records=None):
        """Write a :class:`File` instance to `filepath`.

        :param str filepath: output filepath/filename
        :param bool overwrite: set `True` to overwrite existing file
        :param list keep_records: list of PDB record names to be written
        :param list drop_records: list of PDB record names NOT to be written

        If neither `keep_records` nor `drop_records` is given, all
        :attr:`records` are written to `filepath`. The arguments
        `keep_records` and `drop_records` are exclusive: To write only selected
        records, use `keep_records`. To keep all but selected records, use
        `drop_records`. Records are specified by their :attr:`~PDBRecord.name`.

        - Usage Example 1::

            pdb.write('path/to/filename.pdb',
                      keep_records=['ATOM', 'HETATM', 'CONECT', 'TER'])

        - Usage Example 2::

            pdb.write('path/to/filename.pdb',
                      drop_records=['AUTHOR', 'TITLE', 'MASTER']

        If `overwrite` is set to true, any existing file will be overwritten.

        """
        if keep_records and drop_records:
            raise PDBError(
                'Arguments `keep_records` and `drop_records are exclusive!')
        if os.path.isfile(filepath) and not overwrite:
            log.error(
                'File `%s` already exists. Set `overwrite=True` to delete '
                'existing file.', filepath)
            return False
        with codecs.open(filepath, 'w', encoding='utf-8') as f:
            for lnumber, rec in enumerate(self.records):
                if keep_records and rec.name not in keep_records:
                    continue
                elif drop_records and rec.name in drop_records:
                    continue
                columns = PDB_RECORD_COLUMNS[rec.name]
                formatters = PDB_RECORD_FORMATTERS[rec.name]
                line = [' ' for _ in xrange(81)]
                line[0:len(rec.name)] = rec.name
                for col, dat, form in zip(columns, rec.data, formatters):
                    if dat is not None:
                        out_col, out_form = _handle_continuation(
                            line, col, form)
                        field = '{0:%s}' % out_form
                        try:
                            line[out_col[0]:out_col[1]] = field.format(dat)
                        except ValueError:
                            log.error(
                                'Output error in file `%s`, record `%s` in '
                                'line `%d`. Field `%s` has type `%s`. '
                                'Required for PDB standard is format `%s`. '
                                'Field will be written as string and might '
                                'not correspond to PDB format.', filepath,
                                rec.name, lnumber, dat, type(dat), out_form)
                            line[out_col[0]:out_col[1]] = (
                                '{dat:>{w}s}'.format(
                                    dat=str(dat), w=out_col[1]-out_col[0]))
                line[-1:] = '\n'
                f.write(''.join(line))
        return True

    def _parse_line(self, line, lnumber):
        """Parse a line from a PDB file. If a valid record is identifies, add
        it to :attr:`records` and to :attr:`rec_dict`.

        :param line: a line (string) read from a (PDB) file
        :param lnumber: the line number
        :returns: True (valid PDB record and data detected) or False

        """
        rec_name = line[0:6].strip()
        if rec_name not in PDB_RECORD_TYPES:
            log.info('Unknown PDB record `%s` in line %s.', rec_name, lnumber)
            return False
        columns = PDB_RECORD_COLUMNS[rec_name]
        types = PDB_RECORD_TYPES[rec_name]
        required = PDB_RECORD_REQUIRED[rec_name]
        rec = PDBRecord(source=self, lnumber=lnumber, name=rec_name)
        for col, typ, req in zip(columns, types, required):
            field = line[col[0]:col[1]].strip()
            if not field:
                if req:
                    log.info(
                        'Missing required field for %s record in file '
                        '`%s`, line %d columns %d - %d. Expected %s. Field is '
                        'skipped.', self.filepath, rec_name, lnumber, col[0],
                        col[1], str(typ))
                rec.data.append(None)
                continue
            try:
                rec.data.append(typ(field))
            except ValueError:
                if rec_name != 'REMARK':
                    log.info(
                        'TypeError for %s record in file `%s`, line %d, '
                        'columns %d - %d. Expected %s but found `%s`. Field '
                        'can not be interpreted.', rec_name, self.filepath,
                        lnumber, col[0], col[1], str(typ), field)
                return False
        self.add_record(rec)
        return True


class MolecularStructureToFile(object):
    """Convert data from a :class:`~murdock.molstruct.MolecularStructure`
       to a :class:`File`.

       So far this class contains functions to
       :meth:`replace_coordinates` or :meth:`replace_atoms` in all `ATOM` and
       `HETATM` records within a :class:`File` instance with coordinates/
       properties from the corresponding atoms in a
       :class:`~murdock.molstruct.MolecularStructure`.

    """

    def __init__(self, source):
        #: :class:`murdock.molstruct.MolecularStructure` instance
        self.source = source

    def convert(self, pdbfile, renumber_atoms=False, renumber_residues=False,
                renumber_chains=False, sort_atom_serials=True,
                sort_residue_serials=True, sort_chain_serials=True):
        """Convert `molstruct` to a :class:`File`.
        """
        molstruct = self.source
        ALPHABET = (
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z')
        for mod_num, model in enumerate(molstruct.models):
            if len(molstruct.models) > 1:
                rec = PDBRecord(
                    name='MODEL', source=model,
                    lnumber=len(pdbfile.records)+1)
                rec.data.append(mod_num + 1)
                pdbfile.add_record(rec)
            if not renumber_chains:
                serials = [_chain.serial for _chain in model.chains]
                if len(serials) != len(set(serials)):
                    log.warning(
                        'There are duplicate chain serials in the molecular '
                        'structure.')
            if sort_chain_serials:
                chains = sorted(model.chains, key=lambda ch: ch.serial)
            else:
                chains = model.chains
            chain_serial = -1
            residue_serial = 0
            atom_serial = 0
            new_chain_serials = {}
            new_residue_serials = {}
            new_atom_serials = {}
            for chain in chains:
                if renumber_chains:
                    chain_serial += 1
                    chain_ident = ALPHABET[chain_serial]
                elif isinstance(chain.serial, int):
                    chain_ident = ALPHABET[chain.serial]
                else:
                    chain_ident = chain.serial
                if not renumber_residues:
                    serials = [_res.serial for _res in chain.residues]
                    if len(serials) != len(set(serials)):
                        raise PDBError(
                            'Can not convert MolecularStructure to PDB file '
                            'because there are duplicate residue serials. Set '
                            'parameter `renumber_residues=True`.')
                if sort_residue_serials:
                    residues = sorted(
                        chain.residues, key=lambda res: res.serial)
                else:
                    residues = chain.residues
                if not renumber_atoms:
                    serials = [_atom.serial for _atom in chain.atoms()]
                    if len(serials) != len(set(serials)):
                        log.fatal(
                            'Can not convert MolecularStructure to PDB file '
                            'because there are duplicate atom serials.')
                        return False
                residue_name = None
                residue_serial = 0
                for residue in residues:
                    if renumber_residues:
                        residue_serial += 1
                    else:
                        residue_serial = residue.serial
                    if len(residue.name) > 3:
                        residue_name = _shorten_residue_name(residue.name)
                        log.info(
                            'Residue name `%s` is shortened to `%s` to '
                            'conform PDB format.', residue.name, residue_name)
                    else:
                        residue_name = residue.name
                    if sort_atom_serials:
                        atoms = sorted(residue.atoms, key=lambda at: at.serial)
                    else:
                        atoms = residue.atoms
                    for atom in atoms:
                        if renumber_atoms:
                            atom_serial += 1
                        name = 'ATOM'
                        # Check source for `ATOM` or `HETATM`
                        src = murdock.misc.get_source(atom, src_type=PDBRecord)
                        if src and src.name == 'HETATM':
                            name = 'HETATM'
                        # Create atom record.
                        rec = PDBRecord(
                            name=name, source=atom,
                            lnumber=len(pdbfile.records)+1)
                        if not renumber_atoms:
                            atom_serial = atom.serial
                        rec.data = [
                            atom_serial, atom.name, None, residue_name,
                            chain_ident, residue_serial, None, atom.coords[0],
                            atom.coords[1], atom.coords[2], None, None,
                            atom.element, atom.form_charge]
                        pdbfile.add_record(rec)
                        new_atom_serials[atom] = atom_serial
                    new_residue_serials[residue] = residue_serial
                new_chain_serials[chain] = chain_serial
                rec = PDBRecord(
                    name='TER', source=chain,
                    lnumber=len(pdbfile.records)+1)
                atom_serial += 1
                rec.data = [
                    atom_serial, residue_name, chain_ident, residue_serial,
                    None]
                pdbfile.add_record(rec)
        # Write connect records.
        atoms = sorted(
            molstruct.models[-1].atoms(), key=lambda at: new_atom_serials[at])
        for atom in atoms:
            batoms = [_at for _at in atom.bonded if _at in new_atom_serials]
            batoms = sorted(batoms, key=lambda at: new_atom_serials[at])
            if len(batoms) == 0:
                continue
            rec = PDBRecord(
                name='CONECT', source=atom,
                lnumber=len(pdbfile.records)+1)
            rec.data.append(new_atom_serials[atom])
            rec.data.extend([new_atom_serials[_batom] for _batom in batoms])
            pdbfile.add_record(rec)
        rec = PDBRecord(name='END', lnumber=len(pdbfile.records)+1)
        pdbfile.add_record(rec)
        return True

    def replace_atoms(self, atoms):
        """Change atom attributes in the PDB file.

        Relevant data in all records of the PDB :class:`File` (atom names,
        serials, ...) are overwritten with attributes found in `atoms`.

        For all `atoms`, the :attr:`~murdock.molstruct.Atom.source` attribute
        must reference the corresponding `ATOM` / `HETATM`
        :class:`~murdock.moldata.pdb.PDBRecord` in the :attr:`source` file.

        .. warning:: `LINK` records are not updated.

        """
        atoms = [_a for _a in atoms if _a.source in self.source.records]
        if 'CONECT' in self.source.rec_dict:
            for rec in self.source.rec_dict['CONECT']:
                for i, field in enumerate(rec.data):
                    for atom in atoms:
                        if field == atom.source.data[0]:
                            rec.data[i] = atom.serial
        if 'ANISOU' in self.source.rec_dict:
            for atom in atoms:
                for rec in self.source.rec_dict['ANISOU']:
                    if rec.data[0] == atom.source.data[0]:
                        rec.data[0] = atom.serial
                        rec.data[1] = atom.name
                        rec.data[13] = atom.element
                        rec.data[14] = atom.form_charge
        for atom in atoms:
            atom.source.data[0] = atom.serial
            atom.source.data[1] = atom.name
            for x in atom.coords:
                if not -99.999 < x < 999.999:
                    log.error(
                        'Coordinate values must have values between -99.999 '
                        'and 999.999 to be written into PDB format. The '
                        'coordinate %f will cause problems in the output PDB '
                        'file!', x)
                    return False
            atom.source.data[7:10] = atom.coords[0:3]
            atom.source.data[12] = atom.element
            atom.source.data[13] = atom.form_charge
        return True

    def replace_coordinates(self, atoms):
        """Replace coordinates in all `ATOM` and `HETATM` records.

        For all atoms in :attr:`structure` the
        :attr:`~murdock.molstruct.Atom.source` attribute must reference the
        corresponding `ATOM`/`HETATM`
        :class:`~murdock.moldata.pdb.PDBRecord` in the :attr:`source`.

        """
        for atom in atoms:
            if atom.source_atom.source in self.source.records:
                atom.source.data[7:10] = atom.coords[0:3]
        return True

    def replace_residues(self, residues):
        """Change residue attributes in the PDB file.

        Relevant data in all records of the PDB :class:`File` (residue names,
        serials, ...) are overwritten with attributes found in `residues`.

        For all `residues`, the :attr:`~murdock.molstruct.Residue.source`
        attribute must reference one of the corresponding `ATOM` / `HETATM`
        :class:`~murdock.moldata.pdb.PDBRecord` entries in the
        :attr:`source` file, so that each residue can be matched based on its
        original name and serial.

        .. warning:: So far only `ATOM`, `HETATM` and `SSBOND` records are
                     changed!

        """
        replaced_serials = {}
        replaced_names = {}
        for res in residues:
            for atom in res.atoms:
                replaced_serials[atom.source.data[5]] = res.serial
                atom.source.data[5] = res.serial
                replaced_names[atom.source.data[3]] = res.name
                atom.source.data[3] = res.name
        if 'SSBOND' in self.source.rec_dict:
            for rec in self.source.rec_dict['SSBOND']:
                if rec.data[1] in replaced_names:
                    rec.data[1] = replaced_names[rec.data[1]]
                if rec.data[5] in replaced_names:
                    rec.data[5] = replaced_names[rec.data[5]]
                if rec.data[3] in replaced_serials:
                    rec.data[3] = replaced_serials[rec.data[3]]
                if rec.data[7] in replaced_serials:
                    rec.data[7] = replaced_serials[rec.data[7]]
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
        #: dictionary mapping a chain from a PDB record to the corresponding
        #: target :class:`~murdock.molstruct.Chain`
        self.chain_dict = {}
        #: dictionary mapping a residue from a PDB record to the corresponding
        #: target :class:`~murdock.molstruct.Residue`
        self.residue_dict = {}
        #: dictionary mapping an atom serial number to an
        #: :class:`~murdock.molstruct.Atom`
        self.atom_dict = {}

    def convert(self):
        """Convert a :class:`File` to a
        :class:`~murdock.molstruct.MolecularStructure`.

        So far, the following PDB records are used: `ATOM`, `HETATM`, `MODEL`,
        `TER`, `CONECT`.

        """
        if 'MODEL' not in self.source.rec_dict:
            model = self._add_model()
        for rec in self.source.records:
            if rec.name == 'MODEL':
                model = self._add_model(record=rec)
            elif rec.name == 'ATOM' or rec.name == 'HETATM':
                self._add_atom(rec, model)
            elif rec.name == 'TER':
                # Reset chain- and residue directories for new chain
                self.chain_dict.clear()
                self.residue_dict.clear()
            elif rec.name == 'CONECT':
                self._add_bonds(rec)
        self.structure.name = (
            os.path.splitext(os.path.basename(self.source.filepath))[0])
        return self.structure

    def _add_atom(self, record, model):
        """Add a new :class:`~murdock.molstruct.Atom` to `model`.

        The PDB `record` is passed to :meth:`_set_chain` and
        :meth:`_set_residue` to set the target chain and residue. A new
        :class:`~murdock.molstruct.Atom` is created, retrieves some
        attributes from :attr:`PDBRecord.data` and is added to the correct
        model, chain and residue of :attr:`structure`.
        """
        # Select the target chain in `model` using `record`
        chain = self._set_chain(record, model)
        # Select the target residue in `chain` using `record`
        residue = self._set_residue(record, chain)
        # Create a new atom using data from `record`
        atom = murdock.molstruct.Atom(source=record)
        atom.serial = record.data[0]
        atom.name = record.data[1]
        atom.coords[0] = record.data[7]
        atom.coords[1] = record.data[8]
        atom.coords[2] = record.data[9]
        atom.element = record.data[12]
        atom.form_charge = record.data[13]
        # Add atom to the target residue
        if atom.serial in self.atom_dict[model]:
            log.warning(
                'Two atoms (found in lines %d and %d of file `%s`) have the '
                'same serial (%d). Functions relying on the atom serials will '
                'not work properly!',
                self.atom_dict[model][atom.serial].source.lnumber,
                record.lnumber, atom.source.source.filepath, atom.serial)
        residue.add_atom(atom)
        self.atom_dict[model][atom.serial] = atom
        return True

    def _add_bonds(self, record):
        """Add a new :class:`~murdock.molstruct.Bond` using `record`.
        """
        for model in self.structure.models:
            try:
                atom = self.atom_dict[model][record.data[0]]
            except KeyError:
                log.error(
                    'Wrong `CONECT` record in line %d of file `%s`. Atom '
                    'serial number %d not found in any `ATOM` or `HETATM` '
                    'record!', record.lnumber, record.source.filepath,
                    record.data[0])
                return False
            for atom_serial in record.data[1:]:
                if atom_serial is None:
                    continue
                try:
                    batom = self.atom_dict[model][atom_serial]
                except KeyError:
                    log.error(
                        'Wrong `CONECT` record in line %d of file `%s`. Atom '
                        'serial number %d not found in any `ATOM` or `HETATM` '
                        'record!', record.lnumber, record.source.filepath,
                        atom_serial)
                    continue
                if batom in atom.bonded:
                    continue
                bond = murdock.molstruct.Bond(
                    name='covalent', atoms=[atom, batom])
                bond.source = record
                atom.add_bond(bond)
                batom.add_bond(bond)
                model.bonds.append(bond)
        return True

    def _add_model(self, record=None):
        """Add a new :class:`~murdock.molstruct.Model` to
        :attr:`structure`.
        """
        model = murdock.molstruct.Model()
        if record:
            model.source = record
        if not self.structure.models:
            model.serial = 1
        else:
            model.serial = len(self.structure.models) + 1
        self.structure.add_model(model)
        # Reset chain- and residue directories for new model.
        self.chain_dict.clear()
        self.residue_dict.clear()
        self.atom_dict[model] = {}
        return model

    def _set_chain(self, record, model):
        """Interpret an `ATOM`, `HETATM` or `TER` record to identify a chain.

        A combination of the record :attr:`~PDBRecord.name` and
        the chain identifier (from :attr:`PDBRecord.data`) is used as a key
        (i.e. `ATOM_A` or `HETATM_C`) to unambiguously identify the chain
        within the model.

        If the key retrieved from the `record` does not exist, the chain is
        created, added to the :attr:`structure` and referenced in
        :attr:`chain_dict`.

        :returns: the chain identified from the `record`

        """
        if record.data[4] is not None:
            chain_key = '_'.join([record.name, record.data[4]])
        else:
            chain_key = record.name
        serial = record.data[4]
        name = record.data[4]
        if chain_key not in self.chain_dict:
            chain = murdock.molstruct.Chain(
                source=record, serial=serial, name=name)
            model.add_chain(chain)
            self.chain_dict[chain_key] = chain
            return chain
        return self.chain_dict[chain_key]

    def _set_residue(self, record, chain):
        """Interpret an `ATOM`, `HETATM` or `TER` record to identify a residue.

        A combination of the record :attr:`~PDBRecord.name`, the residue name
        and the residue sequence number (both from :attr:`PDBRecord.data`) is
        used as a key (i.e. `ATOM_ARG_13` or `HETATM_THR_24`) to unambiguously
        identify the residue within the model.

        If the key retrieved from the `record` does not exist, the residue is
        created, added to the :attr:`structure` and referenced in
        :attr:`residue_dict`.

        :returns: the residue identified from the `record`
        """
        res_key = '_'.join([
            record.name, str(record.data[3]), str(record.data[5])])
        name = record.data[3]
        serial = record.data[5]
        if res_key not in self.residue_dict:
            residue = murdock.molstruct.Residue(
                serial=serial, name=name, source=record)
            chain.add_residue(residue)
            self.residue_dict[res_key] = residue
            return residue
        return self.residue_dict[res_key]

    def _validate_master(self):
        """Use `MASTER` record from the PDB to validate a
        :class:`~murdock.molstruct.MolecularStructure`.

        The `MASTER` record holds the number of some records, which is expected
        in the PDB file. It can be used to check whether a :class:`File`
        instance has been correctly parsed all records in a file and
        successfully converted them into the
        :class:`~murdock.molstruct.MolecularStructure` instance.
        Unfortunately - by definition - it describes only the first model in a
        PDB file.

        So far only the `ATOM` and `HETATM` records are checked.

        """
        error = False
        if 'MASTER' not in self.source.rec_dict:
            return False
        elif len(self.source.rec_dict['MASTER']) > 1:
            log.info(
                'The pdb format allows only one `MASTER` record. Instead %d '
                'have been found in `%s`. Verification skipped.',
                len(self.source.rec_dict['MASTER']), self.source.filepath)
            return False
        mast_data = self.source.rec_dict['MASTER'][0].data
        # Compare ATOM+HETATM records to self.atoms
        expected = mast_data[8]     # ATOM & HETATM
        found = len(self.structure.models[0].atoms())
        if expected != found:
            log.warn(
                'Number of atoms expected from the `MASTER` record is %d. '
                'Instead, %d atoms have been added to the '
                '`MolecularStructure`.', expected, found)
            error = True
        # Compare TER records to self.model[0].chains.
        # To be implemented.

        # Compare CONECT records somehow to bonds
        # To be implemented.
        if error:
            log.warning('Check using `MASTER` record not successfull.')
        return not error


class PDBRecordLibrary(object):
    """ Stores most format specifications needed to interpret PDB records.

    A PDB record corresponds to a line in a PDB file. It has a name and data
    fields. For each record (name) certain data fields are specified by the PDB
    file standard. Each data field has a defined position and width in the
    record line. This class provides a library of valid PDB record types and
    data fields according to
    http://www.wwpdb.org/documentation/format33/v3.3.html.

    Input and output methods (:meth:`File.parse` and :meth:`File.write`)
    both use this library to set and verify position, type and format of data
    fields within a PDB file.

    """

    def __init__(self):
        #: stores data field start- and end-positions
        self.columns = {}
        #: stores data conversion functions (:func:`int`, :func:`float`, ...)
        self.types = {}
        #: stores typographic and numerical format (alignment, digits, ...)
        self.formatters = {}
        #: stores whether a field is required for a certain record
        self.required = {}
        self.columns, self.types, self.formatters, self.required = (
            self._fill_library())

    def _fill_library(self):
        """ Return the actual format specifications.

        For each record (name), there is an item in each of the dictionaries
        :attr:`columns`, :attr:`types`, :attr:`formatters` and
        :attr:`required`. The record name is used as key.

        The dictionary :attr:`columns` contains a tuple of tuples of the form
        ``(START - 1, END)`` for each data field of the record. Hence, it
        defines position and length of each data field. START and END are the
        numbers written in the PDB file standard. String slicing by means of
        ``[START - 1:END]`` applied to a PDB record line exactly extracts the
        data from the field.

        The dictionary :attr:`types` contains a tuple of function names. The
        parser applies these functions to the data string extracted from a
        field via slicing in order to validate the data. Invalid data is
        expected to raise a :exc:`ValueError` during parsing. Those data
        type verification functions are built-in functions like :func:`int`,
        :func:`float`. If needed, custom functions could be used as well.

        The dictionary :attr:`formatters` contains a tuple of Python format
        strings to be used in :func:`File.write`. Alignment, data type and
        numerical format have to be specified manually (i.e. ``>.3f`` for a
        right-justified float with 3 digits precision). The field width is
        inserted automatically. For `Continuation` fields (see PDB format
        definition), the field after the `Continuation` integer must me marked
        with a trailing `c`. This marker is found by
        :func:`_handle_continuation` and all continuation lines are
        intended by one char. Missing entries in `formatters` are set to
        left-justified string (``<s``).

        The dictionary :attr:`required` contains a tuple of bool variables
        specifying whether a field is required or not. If a required field is
        missing, :func:`File.parse` prints an error and skips the input
        line. Missing entries in :attr:`required` are set to `False` (not
        required).

        """
        ffloat = murdock.misc.finitefloat
        columns = {}
        types = {}
        formatters = {}
        required = {}
        columns['ANISOU'] = (
            (7, 11), (12, 16), (16, 17), (17, 20), (21, 22), (22, 26),
            (26, 27), (28, 35), (35, 42), (42, 49), (49, 56), (56, 63),
            (63, 70), (76, 78), (78, 80))
        types['ANISOU'] = (
            int, str, str, str, str, int, str, int, int, int, int, int, int,
            str, str)
        formatters['ANISOU'] = [
            '>d', '<s', '<s', '>s', '<s', '>d', '<s', '>d', '>d', '>d', '>d',
            '>d', '>d', '<s', '<s']
        columns['ATOM'] = (
            (6, 11), (12, 16), (16, 17), (17, 20), (21, 22), (22, 26),
            (26, 27), (30, 38), (38, 46), (46, 54), (54, 60), (60, 66),
            (76, 78), (78, 80))
        types['ATOM'] = (
            int, str, str, str, str, int, str, ffloat, ffloat, ffloat, ffloat,
            ffloat, str, str)
        formatters['ATOM'] = [
            '>d', '<s', '<s', '>s', '<s', '>d', '<s', '>.3f', '>.3f', '>.3f',
            '>.2f', '>.2f', '>s', '<s']
        columns['AUTHOR'] = ((8, 10), (10, 79))
        types['AUTHOR'] = (int, str)
        formatters['AUTHOR'] = ['>d', '<sc']
        columns['CAVEAT'] = ((8, 10), (11, 15), (19, 79))
        types['CAVEAT'] = (int, str, str)
        formatters['CAVEAT'] = ['>d', '<sc', '<s']
        columns['CISPEP'] = (
            (7, 10), (11, 14), (15, 16), (17, 21), (21, 22), (25, 28),
            (29, 30), (31, 35), (35, 36), (43, 46), (53, 59))
        types['CISPEP'] = (
            int, str, str, int, str, str, str, int, str, int, ffloat)
        formatters['CISPEP'] = [
            '>d', '<s', '<s', '>d', '<s', '<s', '<s', '>d', '<s', '>d', '>.2f']
        columns['COMPND'] = ((7, 10), (10, 80))
        types['COMPND'] = (int, str)
        formatters['COMPND'] = ['>d', '<sc']
        columns['CONECT'] = ((6, 11), (11, 16), (16, 21), (21, 26), (27, 31))
        types['CONECT'] = (int, int, int, int, int)
        formatters['CONECT'] = ['>d', '>d', '>d', '>d', '>d']
        columns['CRYST1'] = (
            (6, 15), (15, 24), (24, 33), (33, 40), (40, 47), (47, 54),
            (55, 66), (66, 70))
        types['CRYST1'] = (
            ffloat, ffloat, ffloat, ffloat, ffloat, ffloat, str, int)
        formatters['CRYST1'] = [
            '>.3f', '>.3f', '>.3f', '>.2f', '>.2f', '>.2f', '<s', '>d']
        columns['DBREF'] = (
            (7, 11), (12, 13), (14, 18), (18, 19), (20, 24), (24, 25),
            (26, 32), (33, 41), (42, 54), (55, 60), (60, 61), (62, 67),
            (67, 68))
        types['DBREF'] = (
            str, str, int, str, int, str, str, str, str, int, str, int, str)
        formatters['DBREF'] = [
            '<s', '<s', '>d', '<s', '>d', '<s', '<s', '<s', '<s', '>d', '<s',
            '>d', '<s']
        columns['DBREF1'] = (
            (7, 11), (12, 13), (14, 18), (18, 19), (20, 24), (24, 25),
            (26, 32), (27, 67))
        types['DBREF1'] = (str, str, int, str, int, str, str, str)
        formatters['DBREF1'] = ['<s', '<s', '>d', '<s', '>d', '<s', '<s', '<s']
        columns['DBREF2'] = ((7, 11), (12, 13), (18, 40), (45, 55), (57, 67))
        types['DBREF2'] = (str, str, str, int, int)
        formatters['DBREF2'] = ['<s', '<s', '<s', '>d', '>d']
        columns['END'] = (())
        types['END'] = ()
        columns['ENDMDL'] = (())
        types['ENDMDL'] = ()
        columns['EXPDTA'] = ((8, 10), (10, 79))
        types['EXPDTA'] = (int, str)
        formatters['EXPDTA'] = ['>d', '<sc']
        columns['FORMUL'] = ((8, 10), (12, 15), (16, 18), (18, 19), (19, 70))
        types['FORMUL'] = (int, str, int, str, str)
        formatters['FORMUL'] = ['>d', '<s', '>d', '<s', '<s']
        columns['HEADER'] = ((10, 50), (50, 59), (62, 66))
        types['HEADER'] = (str, str, str)
        columns['HELIX'] = (
            (7, 10), (11, 14), (15, 18), (19, 20), (21, 25), (25, 26),
            (27, 30), (31, 32), (33, 37), (37, 38), (38, 40), (40, 70),
            (71, 76))
        types['HELIX'] = (
            int, str, str, str, int, str, str, str, int, str, int, str, int)
        formatters['HELIX'] = [
            '>d', '<s', '>s', '<s', '>d', '<s', '>s', '<s', '>d', '<s', '>d',
            '<s', '>d']
        columns['HET'] = (
            (7, 10), (12, 13), (13, 17), (17, 18), (20, 25), (30, 70))
        types['HET'] = (str, str, int, str, int, str)
        formatters['HET'] = ['>s', '<s', '>d', '<s', '>d', '<s']
        columns['HETATM'] = columns['ATOM'][:]
        types['HETATM'] = types['ATOM'][:]
        formatters['HETATM'] = formatters['ATOM'][:]
        columns['HETNAM'] = ((8, 10), (11, 14), (15, 70))
        types['HETNAM'] = (int, str, str)
        formatters['HETNAM'] = ['>d', '>s', '<s']
        columns['HETSYN'] = ((8, 10), (11, 14), (15, 70))
        types['HETSYN'] = (int, str, str)
        formatters['HETSYN'] = ['>d', '>s', '<s']
        columns['JRNL'] = ((12, 79), )
        types['JRNL'] = (str, )
        columns['KEYWDS'] = ((8, 10), (10, 79))
        types['KEYWDS'] = (int, str)
        formatters['KEYWDS'] = ['>d', '<sc']
        columns['LINK'] = (
            (12, 16), (16, 17), (17, 20), (21, 22), (22, 26), (26, 27),
            (42, 46), (46, 47), (47, 50), (51, 52), (52, 56), (56, 57),
            (59, 65), (66, 72), (73, 78))
        types['LINK'] = (
            str, str, str, str, int, str, str, str, str, str, int, str, int,
            int, ffloat)
        formatters['LINK'] = [
            '<s', '<s', '>s', '<s', '>d', '<s', '<s', '<s', '>s', '<s', '>d',
            '<s', '>d', '>d', '>.2f']
        columns['MASTER'] = (
            (10, 15), (15, 20), (20, 25), (25, 30), (30, 35), (35, 40),
            (40, 45), (45, 50), (50, 55), (55, 60), (60, 65), (65, 70))
        types['MASTER'] = (
            int, int, int, int, int, int, int, int, int, int, int, int)
        required['MASTER'] = (
            True, False, True, True, True, False, True, True, True, True, True,
            True)
        formatters['MASTER'] = [
            '>d', '>d', '>d', '>d', '>d', '>d', '>d', '>d', '>d', '>d', '>d',
            '>d']
        columns['MDLTYP'] = ((8, 10), (10, 80))
        types['MDLTYP'] = (int, str)
        formatters['MDLTYP'] = ['>d', '<sc']
        columns['MODEL'] = ((10, 14), )
        types['MODEL'] = (int, )
        required['MODEL'] = (True, )
        formatters['MODEL'] = ['>d']
        columns['MODRES'] = (
            (7, 11), (12, 15), (16, 17), (18, 22), (22, 23), (24, 27),
            (29, 70))
        types['MODRES'] = (str, str, str, int, str, str, str)
        formatters['MODRES'] = ['<s', '>s', '<s', '>d', '<s', '>s', '<s']
        columns['NUMMDL'] = ((10, 14), )
        types['NUMMDL'] = (int, )
        formatters['NUMMDL'] = ['>d']
        columns['OBSLTE'] = (
            (8, 10), (11, 20), (21, 25), (31, 35), (36, 40), (41, 45),
            (46, 50), (51, 55), (56, 60), (61, 65), (66, 70), (71, 75))
        types['OBSLTE'] = (
            int, str, str, str, str, str, str, str, str, str, str, str)
        formatters['OBSLTE'] = [
            '>d', '<sc', '<s', '<s', '<s', '<s', '<s', '<s', '<s', '<s', '<s',
            '<s']
        columns['REMARK'] = ((7, 10), (11, 79))
        types['REMARK'] = (int, str)
        formatters['REMARK'] = ['>d', '<s']
        columns['REVDAT'] = (
            (7, 10), (10, 12), (13, 22), (23, 27), (31, 32), (39, 45),
            (46, 52), (53, 59), (60, 66))
        types['REVDAT'] = (int, int, str, str, int, str, str, str, str)
        formatters['REVDAT'] = [
            '>d', '>d', '<sc', '<s', '>d', '<s', '<s', '<s', '<s']
        columns['SEQADV'] = (
            (7, 11), (12, 15), (16, 17), (18, 22), (22, 23), (24, 28),
            (29, 38), (39, 42), (43, 48), (49, 70))
        types['SEQADV'] = (str, str, str, int, str, str, str, str, int, str)
        formatters['SEQADV'] = [
            '<s', '>s', '<s', '>d', '<s', '<s', '<s', '>s', '>d', '<s']
        columns['SEQRES'] = (
            (7, 10), (11, 12), (13, 17), (19, 22), (23, 26), (27, 30),
            (31, 34), (35, 38), (39, 42), (43, 46), (47, 50), (51, 54),
            (55, 58), (59, 62), (63, 66), (67, 70))
        types['SEQRES'] = (
            int, str, int, str, str, str, str, str, str, str, str, str, str,
            str, str, str)
        formatters['SEQRES'] = [
            '>d', '<s', '>d', '>s', '>s', '>s', '>s', '>s', '>s', '>s', '>s',
            '>s', '>s', '>s', '>s', '>s']
        columns['SHEET'] = (
            (7, 10), (11, 14), (14, 16), (17, 20), (21, 22), (22, 26),
            (26, 27), (28, 31), (32, 33), (33, 37), (37, 38), (38, 40),
            (41, 45), (45, 48), (49, 50), (50, 54), (54, 55), (56, 60),
            (60, 63), (64, 65), (65, 69), (69, 70))
        types['SHEET'] = (
            int, str, int, str, str, int, str, str, str, int, str, int, str,
            str, str, int, str, str, str, str, int, str)
        formatters['SHEET'] = [
            '>d', '<s', '>d', '>s', '<s', '>d', '<s', '>s', '<s', '>d', '<s',
            '>d', '<s', '>s', '<s', '>d', '<s', '<s', '>s', '<s', '>d', '<s']
        columns['SITE'] = (
            (7, 10), (11, 14), (15, 17), (18, 21), (22, 23), (23, 27),
            (27, 28), (29, 32), (33, 34), (34, 38), (38, 39), (40, 43),
            (44, 45), (45, 49), (40, 50), (51, 54), (55, 56), (56, 60),
            (60, 61))
        types['SITE'] = (
            int, str, int, str, str, int, str, str, str, int, str, str, str,
            int, str, str, str, int, str)
        formatters['SITE'] = [
            '>d', '<s', '>d', '>s', '<s', '>d', '<s', '>s', '<s', '>d', '<s',
            '>s', '<s', '>d', '<s', '>s', '<s', '>d', '<s']
        columns['SOURCE'] = ((7, 10), (10, 79))
        types['SOURCE'] = (int, str)
        formatters['SOURCE'] = ['>d', '<sc']
        columns['SPLIT'] = (
            (8, 10), (11, 15), (16, 20), (21, 25), (26, 30), (31, 35),
            (36, 40), (41, 45), (46, 50), (51, 55), (56, 60), (61, 65),
            (66, 70), (71, 75), (76, 80))
        types['SPLIT'] = (
            int, str, str, str, str, str, str, str, str, str, str, str, str,
            str, str)
        formatters['SPLIT'] = [
            '>d', '<sc', '<s', '<s', '<s', '<s', '<s', '<s', '<s', '<s', '<s',
            '<s', '<s', '<s', '<s']
        columns['SPRSDE'] = (
            (8, 10), (11, 20), (21, 25), (31, 35), (36, 40), (41, 45),
            (46, 50), (51, 55), (56, 60), (61, 65), (66, 70), (71, 75))
        types['SPRSDE'] = (
            int, str, str, str, str, str, str, str, str, str, str, str)
        formatters['SPRSDE'] = [
            '>d', '<sc', '<s', '<s', '<s', '<s', '<s', '<s', '<s', '<s', '<s',
            '<s']
        columns['SSBOND'] = (
            (7, 10), (11, 14), (15, 16), (17, 21), (21, 22), (25, 28),
            (29, 30), (31, 35), (35, 36), (59, 65), (66, 72), (73, 78))
        types['SSBOND'] = (
            int, str, str, int, str, str, str, int, str, int, int, ffloat)
        formatters['SSBOND'] = [
            '>d', '<s', '<s', '>d', '<s', '<s', '<s', '>d', '<s', '>d', '>d',
            '>.2f']
        columns['TER'] = ((6, 11), (17, 20), (21, 22), (22, 26), (26, 27))
        types['TER'] = (int, str, str, int, str)
        formatters['TER'] = ['>d', '>s', '<s', '>d', '<s']
        columns['TITLE'] = ((8, 10), (10, 80))
        types['TITLE'] = (int, str)
        formatters['TITLE'] = ['>d', '<sc']
        for i in xrange(1, 4):
            columns['MTRIX%d' % i] = (
                (7, 10), (10, 20), (20, 30), (30, 40), (45, 55), (59, 60))
            types['MTRIX%d' % i] = (int, ffloat, ffloat, ffloat, ffloat, int)
            formatters['MTRIX%d' % i] = [
                '>d', '>.6f', '>.6f', '>.6f', '>.5f', '>d']
            columns['ORIGX%d' % i] = ((10, 20), (20, 30), (30, 40), (45, 55))
            types['ORIGX%d' % i] = (ffloat, ffloat, ffloat, ffloat)
            formatters['ORIGX%d' % i] = ['>.6f', '>.6f', '>.6f', '>.5f']
            columns['SCALE%d' % i] = ((10, 20), (20, 30), (30, 40), (45, 55))
            types['SCALE%d' % i] = (ffloat, ffloat, ffloat, ffloat)
            formatters['SCALE%d' % i] = ['>.6f', '>.6f', '>.6f', '>.5f']
        # Set all field to NOT required, unless manually set above.
        for key, col in columns.iteritems():
            if key not in required:
                required[key] = [False for _ in col]
        # Set all fields to left-justified strings, unless manually set above.
        for key, col in columns.iteritems():
            if key not in formatters:
                formatters[key] = ['<s' for _ in col]
        # Insert column width to all `formatters`.
        # Example 1: `<.3f` --> `<8.3f`; Example 2: `>s` --> `>8s`
        for key, formatter in formatters.iteritems():
            for i, col in enumerate(columns[key]):
                formatter[i] = '{width}'.join(
                    (formatter[i][0], formatter[i][1:])).format(
                        width=col[1]-col[0])
            formatter = tuple(formatter)
        # Check for self-consistency.
        for rec_name in types:
            if rec_name not in columns:
                raise PDBRecordLibraryError(
                    'Type conversion functions defined for PDB record `%s`, '
                    'but no columns.' % rec_name)
        for rec_name, col in columns.iteritems():
            if rec_name not in types:
                raise PDBRecordLibraryError(
                    'Columns defined for PDB record `%s`, but no type '
                    'conversion functions.' % rec_name)
            if len(col) != len(types[rec_name]):
                raise PDBRecordLibraryError(
                    'Wrong entry in PDB record library. For record name `%s` '
                    'the lists `columns` and `types` have a different length.'
                    % rec_name)
        return columns, types, formatters, required


PDB_RECORD_LIBRARY = PDBRecordLibrary()
PDB_RECORD_COLUMNS = PDB_RECORD_LIBRARY.columns
PDB_RECORD_TYPES = PDB_RECORD_LIBRARY.types
PDB_RECORD_FORMATTERS = PDB_RECORD_LIBRARY.formatters
PDB_RECORD_REQUIRED = PDB_RECORD_LIBRARY.required


def _handle_continuation(line, col, form):
    """Modify column and format string to account for a continuation block.

    The PDB format specifies, that `Continuation` fields are intended by
    one char, which (in :class:`PDBRecordLibrary`) is marked by a trailing
    `c` in the format string. Example: ``<{10}s`` <--> ``<{10}sc``.
    If the `c` is present and if there is a continuation number in the
    preceeding column, the data field is moved by one char to the right.
    In any case, the trailing `c` is removed from the format string.

    """
    out_col = list(col)
    if form.endswith('c'):
        # Get rid of the trailing `c`
        out_form = form[:-1]
        # Check the preceeding field for data. If not empty, it is assumed
        # to be a `Continuation` number.
        if line[col[0]-1].strip():
            out_col[0] += 1
            out_col[1] += 1
    else:
        out_form = form
    return out_col, out_form


def _shorten_residue_name(name):
    while len(name) > 3:
        try:
            int(name[-1])
        except ValueError:
            break
        else:
            name = name[:-1]
    if (len(name) > 3 and
            name[0] in ('N', 'C')):
        name = name[1:]
    if len(name) > 3:
        name = name[:3]
    return name
