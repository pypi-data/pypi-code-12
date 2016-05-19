"""Contains ligand-specific objects and functions."""

import requests
import math
import json
import random
from collections import Counter
from . import gtop
from . import pdb
from .exceptions import *
from .shared import *
from . import interactions

def get_ligand_by_id(ligand_id):
    """Returns a Ligand object of the ligand with the given ID.

    :param int ligand_id: The GtoP ID of the Ligand desired.
    :rtype: :py:class:`Ligand`
    :raises: :class:`.NoSuchLigandError` if no such ligand exists in the database"""

    json_data = gtop.get_json_from_gtop("ligands/%i" % ligand_id)
    if json_data:
        return Ligand(json_data)
    else:
        raise NoSuchLigandError


def get_random_ligand(ligand_type=None):
    """Returns a random ligand, with the option to specify the ligand type.
    This can take a few seconds as it must first request *all* ligands.

    :param str ligand_type: If not None, the function will pick a ligand from\
     this category only.

    :rtype: :py:class:`Ligand`
    :raises: :class:`.NoSuchTypeError` if a ligand type is supplied which doesn't exist
    """

    if ligand_type:
        json_data = gtop.get_json_from_gtop("ligands?type=%s" % ligand_type.lower())
        if not json_data:
            raise NoSuchTypeError("There are no ligands of type %s" % ligand_type)
    else:
        json_data = gtop.get_json_from_gtop("ligands")
    return Ligand(random.choice(json_data))


def get_all_ligands():
    """Returns a list of all ligands in the Guide to PHARMACOLOGY database. This
    can take a few seconds.

    :returns: list of :py:class:`Ligand` objects"""

    json_data = gtop.get_json_from_gtop("ligands")
    return [Ligand(l) for l in json_data]


def get_ligands_by(criteria):
    """Get all ligands which specify the criteria dictionary.

    :param dict criteria: A dictionary of `field=value` pairs. See the\
     `GtoP ligand web services page <http://www.guidetopharmacology.org/\
     webServices.jsp#ligands>`_ for key/value pairs which can be supplied.
    :returns: list of :py:class:`Ligand` objects."""

    search_string = "&".join(["%s=%s" % (key, criteria[key]) for key in criteria])
    json_data = gtop.get_json_from_gtop("ligands?%s" % search_string)
    if json_data:
        return [Ligand(l) for l in json_data]
    else:
        return []


def get_ligand_by_name(name):
    """Returns the ligand which matches the name given.

    :param str name: The name of the ligand to search for. Note that synonyms \
    will not be searched.
    :rtype: :py:class:`Ligand`
    :raises:  :class:`.NoSuchLigandError` if no such ligand exists in the database."""

    ligands = get_ligands_by({"name": name})
    if ligands:
        return ligands[0]
    else:
        raise NoSuchLigandError


def get_ligands_by_smiles(smiles, search_type="exact", cutoff=0.8):
    """Search for ligands by SMILES string.

    :param str smiles: The SMILES string to search with.
    :param str search_type: The type of search. Viable options are ``"exact"``, \
    ``"substructure"`` or ``"similarity"``.
    :param float cutoff: If performing a similarity search, this is the cutoff \
    used for similarity. The default is 0.8 and the maximum is 1.
    :returns: list of :py:class:`Ligand` objects."""

    query = "ligands/%s/smiles?smiles=%s%s" % (
     search_type,
     smiles,
     "similarityGt=%f" % cutoff if search_type == "similarity" else ""
    )
    json_data = gtop.get_json_from_gtop(query)
    if json_data:
        return [Ligand(l) for l in json_data]
    else:
        return []



class Ligand:
    """A Guide to PHARMACOLOGY ligand object.

    :param json_data: A dictionary obtained from the web services.

    .. py:attribute:: ligand_id:

        The ligand's GtoP ID.

    .. py:attribute:: name:

        The ligand's name.

    .. py:attribute:: abbreviation:

        The ligand's abbreviated name.

    .. py:attribute:: inn:

        The ligand's INN name.

    .. py:attribute:: ligand_type:

        The ligand type.

    .. py:attribute:: species:

        The ligand's GtoP ID.

    .. py:attribute:: radioactive:

        Is the ligand radioactive?

    .. py:attribute:: labelled:

        Is the ligand labelled?.

    .. py:attribute:: approved:

        Has the ligand been approved?

    .. py:attribute:: withdrawn:

        Has the drug been withdrawn?

    .. py:attribute:: approval_source:

        The regulatory body which approved the drug.
    """

    def __init__(self, json_data):
        self.json_data = json_data

        self.ligand_id = json_data["ligandId"]
        self.name = json_data["name"]
        self.abbreviation = json_data["abbreviation"] if json_data["abbreviation"] else None
        self.inn = json_data["inn"]
        self.ligand_type = json_data["type"]
        self.species = json_data["species"]
        self.radioactive = json_data["radioactive"]
        self.labelled = json_data["labelled"]
        self.approved = json_data["approved"]
        self.withdrawn = json_data["withdrawn"]
        self.approval_source = json_data["approvalSource"]
        self._subunit_ids = json_data["subunitIds"]
        self._complex_ids = json_data["complexIds"]
        self._prodrug_ids = json_data["prodrugIds"]
        self._active_drug_ids = json_data["activeDrugIds"]


    def __getattr__(self, key):
        error_message = self._get_missing_attribute_error_message(key)
        if error_message:
            raise PropertyNotRequestedYetError(error_message)
        else:
            raise AttributeError("Ligand object has no attribute '%s'" % key)


    def __repr__(self):
        return "<'%s' Ligand (%s)>" % (self.name, self.ligand_type)


    def get_subunits(self):
        """Returns a list of all ligands which are subunits of this ligand.

        :returns: list of :py:class:`Ligand` objects"""

        return [get_ligand_by_id(i) for i in self._subunit_ids]


    def get_complexes(self):
        """Returns a list of all ligands of which this ligand is a subunit.

        :returns: list of :py:class:`Ligand` objects"""

        return [get_ligand_by_id(i) for i in self._complex_ids]


    def get_prodrugs(self):
        """Returns a list of all ligands which are prodrugs of this ligand.

        :returns: list of :py:class:`Ligand` objects"""

        return [get_ligand_by_id(i) for i in self._prodrug_ids]


    def get_active_drugs(self):
        """Returns a list of all ligands which are active equivalents of this ligand.

        :returns: list of :py:class:`Ligand` objects"""

        return [get_ligand_by_id(i) for i in self._active_drug_ids]


    def get_interactions(self):
        """Returns a list of all interactions which this ligand is involved in.

        :returns: list of :py:class:`.Interaction` objects"""

        from .interactions import Interaction
        interactions_json = gtop.get_json_from_gtop(
         "/ligands/%i/interactions" % self.ligand_id
        )
        if interactions_json:
            return [Interaction(json) for json in interactions_json]
        else:
            return []


    get_interaction_by_id = interactions.get_interaction_by_id
    """Returns an Interaction object of a given ID belonging to the ligand.

    :param int interaction_id: The interactions's ID.
    :rtype: :py:class:`.Interaction`
    :raises: :class:`.NoSuchInteractionError`: if no such interaction exists in the database."""


    def get_targets(self):
        """Returns a list of all targets which this ligand interacts with.

        :returns: list of :py:class:`.Target` objects"""

        targets = []
        for interaction in self.get_interactions():
            target = interaction.get_target()
            if target not in targets:
                targets.append(target)
        return targets


    def get_species_targets(self):
        """Returns a list of all species-specific targets which this ligand interacts with.

        :returns: list of :py:class:`.SpeciesTarget` objects"""

        species_targets = []
        for interaction in self.get_interactions():
            species_target = interaction.get_species_target()
            if species_target not in species_targets:
                species_targets.append(species_target)
        return species_targets


    @pdb.ask_about_molecupy
    def get_gtop_pdbs(self):
        """Returns a list of PDBs which the Guide to PHARMACOLOGY says contain
        this ligand.

        :param bool as_molecupy: Returns the PDBs as \
        `molecuPy <http://molecupy.readthedocs.io>`_ PDB objects.
        :returns: list of ``str`` PDB codes"""

        pdbs = []
        for interaction in self.get_interactions():
            for pdb in interaction.get_gtop_pdbs():
                if pdb not in pdbs:
                    pdbs.append(pdb)
        return pdbs


    @pdb.ask_about_molecupy
    def find_pdbs_by_smiles(self, search_type="exact"):
        """Queries the RSCB PDB database with the ligand's SMILES string.

        :param str search_type: The type of search to run - whether exact matches\
        only should be returned.
        :param bool as_molecupy: Returns the PDBs as \
        `molecuPy <http://molecupy.readthedocs.io>`_ PDB objects.
        :returns: list of ``str`` PDB codes"""

        if "smiles" not in self.__dict__:
            self.request_structural_properties()
        if self.smiles:
            xml = pdb.query_rcsb("smilesQuery", {
             "smiles": self.smiles,
             "search_type": search_type
            })
            if xml:
                ligand_elements = list(xml[0])
                return [element.attrib["structureId"] for element in ligand_elements]
            else:
                return []
        else:
            return []


    @pdb.ask_about_molecupy
    def find_pdbs_by_inchi(self):
        """Queries the RSCB PDB database with the ligand's InChI string.

        :param bool as_molecupy: Returns the PDBs as \
        `molecuPy <http://molecupy.readthedocs.io>`_ PDB objects.
        :returns: list of ``str`` PDB codes"""

        if "inchi" not in self.__dict__:
            self.request_structural_properties()
        if self.inchi:
            results = pdb.query_rcsb_advanced("ChemCompDescriptorQuery", {
             "descriptor": self.inchi,
             "descriptorType": "InChI"
            })
            return results if results else []
        else:
            return []


    @pdb.ask_about_molecupy
    def find_pdbs_by_name(self, comparator="equals"):
        """Queries the RSCB PDB database with the ligand's name.

        :param str comparator: The type of search to run - whether exact matches\
        only should be returned, or substrings etc.
        :param bool as_molecupy: Returns the PDBs as \
        `molecuPy <http://molecupy.readthedocs.io>`_ PDB objects.
        :returns: list of ``str`` PDB codes"""

        results = pdb.query_rcsb_advanced("ChemCompNameQuery", {
         "comparator": comparator.title(),
         "name": self.name,
         "polymericType": "Any"
        })
        return results if results else []


    @pdb.ask_about_molecupy
    def find_pdbs_by_sequence(self):
        """Queries the RSCB PDB database with the ligand's amino acid sequence,\
        if that ligand is a peptide.

        :param bool as_molecupy: Returns the PDBs as \
        `molecuPy <http://molecupy.readthedocs.io>`_ PDB objects.
        :returns: list of ``str`` PDB codes"""

        if "one_letter_sequence" not in self.__dict__:
            self.request_structural_properties()
        if self.one_letter_sequence:
            results = pdb.query_rcsb_advanced("SequenceQuery", {
             "sequence": self.one_letter_sequence,
             "eCutOff": "0.01",
             "searchTool": "blast",
             "sequenceIdentityCutoff": "100"
            })
            return results if results else []
        else:
            return []


    @pdb.ask_about_molecupy
    def find_all_external_pdbs(self):
        """Queries the RSCB PDB database by all parameters.

        :param bool as_molecupy: Returns the PDBs as \
        `molecuPy <http://molecupy.readthedocs.io>`_ PDB objects.
        :returns: list of ``str`` PDB codes"""

        return list(set(
         self.find_pdbs_by_smiles() +
         self.find_pdbs_by_inchi() +
         self.find_pdbs_by_name() +
         self.find_pdbs_by_sequence()
        ))


    @pdb.ask_about_molecupy
    def find_all_pdbs(self):
        """Get a list of PDB codes using all means available - annotated and
        external.

        :param bool as_molecupy: Returns the PDBs as \
        `molecuPy <http://molecupy.readthedocs.io>`_ PDB objects.
        :returns: list of ``str`` PDB codes"""

        return list(set(
         self.get_gtop_pdbs() +
         self.find_all_external_pdbs()
        ))


    def find_in_pdb_by_smiles(self, molecupy_pdb):
        self.request_structural_properties()
        if self.smiles:
            formula = Counter([char.upper() for char in self.smiles
             if char.isalpha() and char.upper() != "H"])
            for molecule in molecupy_pdb.model.small_molecules:
                if molecule.get_formula() == formula:
                    return molecule


    def find_in_pdb_by_name(self, molecupy_pdb):
        if self.name:
            for molecule in molecupy_pdb.model.small_molecules:
                molecule_name = molecupy_pdb.data_file.het_names.get(molecule.molecule_name)
                if molecule_name and self.name.lower() == molecule_name.lower():
                    return molecule


    def find_in_pdb_by_mass(self, molecupy_pdb):
        self.request_molecular_properties()
        if self.molecular_weight:
            molecules = sorted(
             list(molecupy_pdb.model.small_molecules),
             key=lambda k: abs(k.get_mass() - self.molecular_weight)
            )
            if molecules and -40 < (molecules[0].get_mass() - self.molecular_weight) < 40:
                return molecules[0]


    def find_in_pdb_by_peptide_string(self, molecupy_pdb):
        if "inchi" not in self.__dict__: self.request_structural_properties()
        if self.one_letter_sequence:
            for chain in molecupy_pdb.model.chains:
                if self.one_letter_sequence in chain.get_sequence_string() and 0.9 <= (
                 len(self.one_letter_sequence) / len(chain.get_sequence_string())
                ) <= 1:
                    return chain


    def request_structural_properties(self):
        """Give ligand object structural properties:

        .. py:attribute:: iupac_name:

            The ligand's full IUPAC name.

        .. py:attribute:: smiles:

            The ligand's SMILES string.

        .. py:attribute:: inchi:

            The ligand's InChI string.

        .. py:attribute:: inchi_key:

            The ligand's InChI key.

        .. py:attribute:: one_letter_sequence:

            If relevant, the single-code Amino Acid sequence.

        .. py:attribute:: three_letter_sequence:

            If relevant, the three-char-code Amino Acid sequence.

        .. py:attribute:: post_translational_modifications:

            Post-translational modifications, if any.

        .. py:attribute:: chemical_modifications:

            Chemical modifications, if any."""

        json_data = gtop.get_json_from_gtop("ligands/%i/%s" % (
         self.ligand_id, gtop.STRUCTURAL_PROPERTIES))
        self.iupac_name = json_data["iupacName"] if json_data else None
        self.smiles = json_data["smiles"] if json_data else None
        self.inchi = json_data["inchi"] if json_data else None
        self.inchi_key = json_data["inchiKey"] if json_data else None
        self.one_letter_sequence = json_data["oneLetterSeq"] if json_data else None
        self.three_letter_sequence = json_data["threeLetterSeq"] if json_data else None
        self.post_translational_modifications = json_data[
         "postTranslationalModifications"] if json_data else None
        self.chemical_modifications = json_data[
         "chemicalModifications"] if json_data else None


    def request_molecular_properties(self):
        """Give ligand object molecular properties:

        .. py:attribute:: hydrogen_bond_acceptors:

            Number of H-bond acceptor atoms.

        .. py:attribute:: hydrogen_bond_donors:

            Number of H-bond donor atoms.

        .. py:attribute:: rotatable_bonds:

            Number of rotatable bonds in the ligand.

        .. py:attribute:: topological_polar_surface_area:

            polar surface area, in Angstroms.

        .. py:attribute:: molecular_weight:

            Ligand's mass.

        .. py:attribute:: log_p:

            Log of partition coefficient - a measure of solubility.

        .. py:attribute:: lipinksi_rules_broken:

            Number of Lipinski's rules the ligand breaks (a measure of druglikeness)."""

        json_data = gtop.get_json_from_gtop("ligands/%i/%s" % (
         self.ligand_id, gtop.MOLECULAR_PROPERTIES))
        self.hydrogen_bond_acceptors = json_data[
         "hydrogenBondAcceptors"] if json_data else None
        self.hydrogen_bond_donors = json_data["hydrogenBondDonors"] if json_data else None
        self.rotatable_bonds = json_data["rotatableBonds"] if json_data else None
        self.topological_polar_surface_area = json_data[
         "topologicalPolarSurfaceArea"] if json_data else None
        self.molecular_weight = json_data["molecularWeight"] if json_data else None
        self.log_p = json_data["logP"] if json_data else None
        self.lipinksi_rules_broken = json_data[
         "lipinskisRuleOfFive"] if json_data else None


    def request_database_properties(self):
        """Give ligand object database properties:

        .. py:attribute:: database_links:

            A list of  :class:`.DatabaseLink` objects."""

        json_data = gtop.get_json_from_gtop("ligands/%i/%s" % (
         self.ligand_id, gtop.DATABASE_PROPERTIES))
        self.database_links = [
         DatabaseLink(link) for link in json_data] if json_data else []


    def request_synonym_properties(self):
        """Give ligand object synonym properties:

        .. py:attribute:: synonyms:

            A list of synonym :py:class:`str` objects."""

        json_data = gtop.get_json_from_gtop("ligands/%i/%s" % (
         self.ligand_id, gtop.SYNONYM_PROPERTIES))
        self.synonyms = [
         synonym["name"] for synonym in json_data] if json_data else []


    def request_comment_properties(self):
        """Give ligand object comment properties:

        .. py:attribute:: general_comments:

            General comments.

        .. py:attribute:: bioactivity_comments:

            Bioactivity comments.

        .. py:attribute:: clinical_use_comments:

            Clinical use comments.

        .. py:attribute:: mechanism_of_action_comments:

            Mechanism comments.

        .. py:attribute:: absorption_and_distribution_comments:

            Absorption and distribution comments.

        .. py:attribute:: metabolism_comments:

            Metabolism comments.

        .. py:attribute:: elimination_comments:

            Elimination comments.

        .. py:attribute:: population_pharmacokinetics_comments:

            Population kinetics comments.

        .. py:attribute:: organ_function_impairments_comments:

            Organ funciton impairment comments."""

        json_data = gtop.get_json_from_gtop(
         "ligands/%i/%s" % (self.ligand_id, gtop.COMMENT_PROPERTIES))
        self.general_comments = json_data[
         "comments"] if json_data else ""
        self.bioactivity_comments = json_data[
         "bioactivityComments"] if json_data else ""
        self.clinical_use_comments = json_data[
         "clinicalUse"] if json_data else ""
        self.mechanism_of_action_comments = json_data[
         "mechanismOfAction"] if json_data else ""
        self.absorption_and_distribution_comments = json_data[
         "absorptionAndDistribution"] if json_data else ""
        self.metabolism_comments = json_data["metabolism"] if json_data else ""
        self.elimination_comments = json_data["elimination"] if json_data else ""
        self.population_pharmacokinetics_comments = json_data[
         "populationPharmacokinetics"] if json_data else ""
        self.organ_function_impairments_comments = json_data[
         "organFunctionImpairment"] if json_data else ""
        self.mutations_and_pathophysiology_comments = json_data[
         "mutationsAndPathophysiology"] if json_data else ""


    def request_precursor_properties(self):
        """Give ligand object precursor properties:

        .. py:attribute:: precursors:

            A list of  :class:`.Precursor` objects"""

        json_data = gtop.get_json_from_gtop("ligands/%i/%s" % (
         self.ligand_id, gtop.PRECURSOR_PROPERTIES))
        self.precursors = [Precursor(p) for p in json_data] if json_data else []


    def request_all_properties(self):
        """Give ligand object all extra properties."""

        self.request_structural_properties()
        self.request_molecular_properties()
        self.request_database_properties()
        self.request_synonym_properties()
        self.request_comment_properties()
        self.request_precursor_properties()


    def _get_missing_attribute_error_message(self, attribute):
        message = "'%s' is a %s property and needs to be requested with %s()"
        values = []

        if attribute in self._structural_properties:
            values = ["structural", "request_structural_properties"]
        elif attribute in self._molecular_properties:
            values = ["molecular", "request_molecular_properties"]
        elif attribute in self._database_properties:
            values = ["database", "request_database_properties"]
        elif attribute in self._synonym_properties:
            values = ["synonym", "request_synonym_properties"]
        elif attribute in self._comment_properties:
            values = ["comment", "request_common_properties"]
        elif attribute in self._precursor_properties:
            values = ["precursor", "request_precursor_properties"]

        if values:
            values = [attribute] + values
            return (message % tuple(values))
        else:
            return None


    _structural_properties = [
     "iupac_name",
     "smiles",
     "inchi",
     "inchi_key",
     "one_letter_sequence",
     "three_letter_sequence",
     "post_translational_modifications",
     "chemical_modifications"
    ]

    _molecular_properties = [
     "hydrogen_bond_acceptors",
     "hydrogen_bond_donors",
     "rotatable_bonds",
     "topological_polar_surface_area",
     "molecular_weight",
     "log_p",
     "lipinksi_rules_broken"
    ]

    _database_properties = [
     "database_links"
    ]

    _synonym_properties = [
     "synonyms"
    ]

    _comment_properties = [
     "general_comments",
     "bioactivity_comments",
     "clinical_use_comments",
     "mechanism_of_action_comments",
     "absorption_and_distribution_comments",
     "metabolism_comments",
     "elimination_comments",
     "population_pharmacokinetics_comments",
     "organ_function_impairments_comments",
     "mutations_and_pathophysiology_comments"
    ]

    _precursor_properties = [
     "precursors"
    ]
