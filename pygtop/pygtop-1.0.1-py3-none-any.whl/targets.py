"""Contains target-specific objects and functions."""

from .exceptions import *
from . import pdb
from . import gtop
from .shared import *
from . import interactions
import random


def get_target_by_id(target_id):
    """Returns a Target object of the target with the given ID.

    :param int target_id: The GtoP ID of the Target desired.
    :rtype: :py:class:`Target`
    :raises: :class:`.NoSuchTargetError`: if no such target exists in the database"""

    json_data = gtop.get_json_from_gtop("targets/%i" % target_id)
    if json_data:
        return Target(json_data)
    else:
        raise NoSuchTargetError


def get_random_target(target_type=None):
    """Returns a random target, with the option to specify the target type.
    This can take a few seconds as it must first request *all* targets.

    :param str target_type: If not None, the function will pick a target from\
     this category only.

    :rtype: :py:class:`Target`
    :raises: :class:`.NoSuchTypeError`: if a target type is supplied which doesn't exist"""
    if target_type:
        json_data = gtop.get_json_from_gtop("targets?type=%s" % target_type.lower())
        if not json_data:
            raise NoSuchTypeError("There are no targets of type %s" % target_type)
    else:
        json_data = gtop.get_json_from_gtop("targets")
    return Target(random.choice(json_data))


def get_all_targets():
    """Returns a list of all targets in the Guide to PHARMACOLOGY database. This
    can take a few seconds.

    :returns: list of :py:class:`Target` objects"""

    json_data = gtop.get_json_from_gtop("targets")
    return [Target(t) for t in json_data]


def get_targets_by(criteria):
    """Get all targets which specify the criteria dictionary.

    :param dict criteria: A dictionary of `field=value` pairs. See the\
     `GtoP target web services page <http://www.guidetopharmacology.org/\
     webServices.jsp#targets>`_ for key/value pairs which can be supplied.
    :returns: list of :py:class:`Target` objects."""

    search_string = "&".join(["%s=%s" % (key, criteria[key]) for key in criteria])
    json_data = gtop.get_json_from_gtop("targets?%s" % search_string)
    if json_data:
        return [Target(t) for t in json_data]
    else:
        return []


def get_target_by_name(name):
    """Returns the target which matches the name given.

    :param str name: The name of the target to search for. Note that synonyms \
    will not be searched.
    :rtype: :py:class:`Target`
    :raises:  :class:`.NoSuchTargetError`: if no such target exists in the database."""

    targets = get_targets_by({"name": name})
    if targets:
        return targets[0]
    else:
        raise NoSuchTargetError


def get_family_by_id(family_id):
    """Returns a TargetFamily object of the family with the given ID.

    :param int family_id: The GtoP ID of the TargetFamily desired.
    :rtype: :py:class:`TargetFamily`
    :raises: :class:`.NoSuchFamilyError`: if no such family exists in the database"""

    json_data = gtop.get_json_from_gtop("targets/families/%i" % family_id)
    if json_data:
        return TargetFamily(json_data)
    else:
        raise NoSuchFamilyError


def get_all_families():
    """Returns a list of all target families in the Guide to PHARMACOLOGY database.

    :returns: list of :py:class:`TargetFamily` objects"""

    json_data = gtop.get_json_from_gtop("targets/families")
    return [TargetFamily(f) for f in json_data]


def get_random_family():
    """Returns a random target, with the option to specify the target type.

    :rtype: :py:class:`TargetFamily`"""
    json_data = gtop.get_json_from_gtop("targets/families")
    return TargetFamily(random.choice(json_data))



class Target:
    """A Guide to PHARMACOLOGY target object.

    :param json_data: A dictionary obtained from the web services.

    .. py:attribute:: target_id:

        The target's GtoP ID.

    .. py:attribute:: name:

        The target's name.

    .. py:attribute:: abbreviation:

        The target's abbreviated name.

    .. py:attribute:: target_type:

        The target type.

    .. py:attribute:: systematic_name:

        The target's systematic name.
    """

    def __init__(self, json_data):
        self.json_data = json_data

        self.target_id = json_data["targetId"]
        self.name = json_data["name"].strip()
        self.abbreviation = json_data["abbreviation"]\
         if json_data["abbreviation"] else None
        self.systematic_name = json_data["systematicName"]\
         if json_data["systematicName"] else None
        self.target_type = json_data["type"]
        self._family_ids = json_data["familyIds"]
        self._subunit_ids = json_data["subunitIds"]
        self._complex_ids = json_data["complexIds"]


    def __getattr__(self, key):
        error_message = self._get_missing_attribute_error_message(key)
        if error_message:
            raise PropertyNotRequestedYetError(error_message)
        else:
            raise AttributeError("Target object has no attribute '%s'" % key)


    def __repr__(self):
        return "<'%s' Target (%s)>" % (self.name, self.target_type)


    def get_subunits(self):
        """Returns a list of all targets which are subunits of this target.

        :returns: list of :py:class:`Target` objects"""

        return [get_target_by_id(i) for i in self._subunit_ids]


    def get_complexes(self):
        """Returns a list of all targets of which this target is a subunit.

        :returns: list of :py:class:`Target` objects"""

        return [get_target_by_id(i) for i in self._complex_ids]


    def get_families(self):
        """Returns a list of all target families of which this target is a member.

        :returns: list of :py:class:`TargetFamily` objects"""

        return [get_family_by_id(i) for i in self._family_ids]


    def get_interactions(self):
        """Returns a list of all interactions which this target is involved in.

        :returns: list of :py:class:`.Interaction` objects"""

        from .interactions import Interaction
        interactions_json = gtop.get_json_from_gtop(
         "/targets/%i/interactions" % self.target_id
        )
        if interactions_json:
            return [Interaction(json) for json in interactions_json]
        else:
            return []


    get_interaction_by_id = interactions.get_interaction_by_id
    """Returns an Interaction object of a given ID belonging to the target.

    :param int interaction_id: The interactions's ID.
    :rtype: :py:class:`.Interaction`
    :raises: :class:`.NoSuchInteractionError`: if no such interaction exists in the database."""


    def get_ligands(self):
        """Returns a list of all ligands which this target interacts with.

        :returns: list of :py:class:`.Ligand` objects"""

        ligands = []
        for interaction in self.get_interactions():
            ligand = interaction.get_ligand()
            if ligand not in ligands:
                ligands.append(ligand)
        return ligands


    @pdb.ask_about_molecupy
    def get_gtop_pdbs(self):
        """Returns a list of PDBs which the Guide to PHARMACOLOGY says contain
        this target.

        :param bool as_molecupy: Returns the PDBs as \
        `molecuPy <http://molecupy.readthedocs.io>`_ PDB objects.
        :returns: list of ``str`` PDB codes"""

        json_data = gtop.get_json_from_gtop("targets/%i/pdbStructure" % self.target_id)
        if json_data:
            return [pdb["pdbCode"] for pdb in json_data if pdb["pdbCode"]]
        else:
            return []


    @pdb.ask_about_molecupy
    def find_pdbs_by_uniprot_accession(self):
        """Queries the RSCB PDB database with the targets's uniprot accessions.

        :param bool as_molecupy: Returns the PDBs as \
        `molecuPy <http://molecupy.readthedocs.io>`_ PDB objects.
        :returns: list of ``str`` PDB codes"""

        if "database_links" not in self.__dict__:
            self.request_database_properties()
        uniprot_accessions = [
         link.accession for link in self.database_links
          if link.database == "UniProtKB"
        ]
        if uniprot_accessions:
            results = pdb.query_rcsb_advanced("UpAccessionIdQuery", {
             "accessionIdList": ",".join(uniprot_accessions)
            })
            return [result.split(":")[0] for result in results] if results else []
        else:
            return []


    @pdb.ask_about_molecupy
    def find_all_pdbs(self):
        """Get a list of PDB codes using all means available - annotated and
        external.

        :param bool as_molecupy: Returns the PDBs as \
        `molecuPy <http://molecupy.readthedocs.io>`_ PDB objects.
        :returns: list of ``str`` PDB codes"""

        return list(set(
         self.get_gtop_pdbs() +
         self.find_pdbs_by_uniprot_accession()
        ))


    def request_database_properties(self):
        """Give target object database properties:

        .. py:attribute:: database_links:

            A list of  :class:`.DatabaseLink` objects."""

        json_data = gtop.get_json_from_gtop("targets/%i/%s" % (
         self.target_id, gtop.DATABASE_PROPERTIES))
        self.database_links = [
         DatabaseLink(link) for link in json_data] if json_data else []


    def request_synonym_properties(self):
        """Give target object synonym properties:

        .. py:attribute:: synonyms:

            A list of synonym :py:class:`str` objects."""

        json_data = gtop.get_json_from_gtop("ligands/%i/%s" % (
         self.target_id, gtop.SYNONYM_PROPERTIES))
        self.synonyms = [
         synonym["name"] for synonym in json_data] if json_data else []


    def request_all_properties(self):
        """Give target object all extra properties."""

        self.request_database_properties()
        self.request_synonym_properties()


    def _get_missing_attribute_error_message(self, attribute):
        message = "'%s' is a %s property and needs to be requested with %s()"
        values = []

        if attribute in self._database_properties:
            values = ["database", "request_database_properties"]
        elif attribute in self._synonym_properties:
            values = ["synonym", "request_synonym_properties"]

        if values:
            values = [attribute] + values
            return (message % tuple(values))
        else:
            return None


    _database_properties = [
     "database_links"
    ]

    _synonym_properties = [
     "synonyms"
    ]



class SpeciesTarget(Target):
    """Base class: :py:class:`Target`

    A species-specific variant of a Target. This object behaves much like a
    Target object (from which it inherits), but it is species-aware, and will
    only collect properties which are applicable to this species.

    For example, when requesting database links, only those links which apply
    to this species will be returned.

    :param target_id: The base Target's GtoP ID.
    :param species: The species of this target.

    .. py:attribute:: target_id:

        The GtoP ID of the target.

    .. py:attribute:: target:

        The Target object of this variant.

    .. py:attribute:: species:

        The variant's species.
    """

    def __init__(self, target_id, species):
        self.target_id = target_id
        self.target = get_target_by_id(target_id)
        self.species = species.lower()


    def __repr__(self):
        return "<%s %s>" % (self.species, self.target.name)


    def get_interactions(self):
        """Returns a list of all interactions which this target is involved in for this species.

        :returns: list of :py:class:`.Interaction` objects"""

        interactions = Target.get_interactions(self)
        return [
         i for i in interactions if i.species.lower() == self.species.lower()
        ]


    def get_gtop_pdbs(self):
        """Returns a list of PDBs which the Guide to PHARMACOLOGY says contain
        this target and in this species.

        :returns: list of ``str`` PDB codes"""

        json_data = gtop.get_json_from_gtop("targets/%i/pdbStructure" % self.target_id)
        if json_data:
            return [
             pdb["pdbCode"] for pdb in json_data if pdb["pdbCode"]
              and pdb["species"].lower() == self.species.lower()
            ]
        else:
            return []


    def request_database_properties(self):
        """Get database properties relevant to this species:

        .. py:attribute:: database_links:

            A list of  :class:`.DatabaseLink` objects for this species."""

        Target.request_database_properties(self)
        self.database_links = [
         link for link in self.database_links
          if link.species.lower() == self.species.lower()
        ]


class TargetFamily:
    """A Guide to PHARMACOLOGY target family object.

    :param json_data: A dictionary obtained from the web services.

    .. py:attribute:: family_id:

        The family's GtoP ID.

    .. py:attribute:: name:

        The family's name.
    """

    def __init__(self, json_data):
        self.json_data = json_data

        self.family_id = json_data["familyId"]
        self.name = json_data["name"]
        self._target_ids = json_data["targetIds"]
        self._parent_family_ids = json_data["parentFamilyIds"]
        self._sub_family_ids = json_data["subFamilyIds"]


    def __repr__(self):
        return "<'%s' TargetFamily>" % self.name


    def get_targets(self):
        """Returns a list of all targets in this family. Note that only
        immediate children are shown - if a family has subfamilies then it will
        not return any targets here - you must look in the sub-families.

        :returns: list of :py:class:`Target` objects"""

        return [get_target_by_id(i) for i in self._target_ids]


    def get_parent_families(self):
        """Returns a list of all target families of which this family is a member.

        :returns: list of :py:class:`TargetFamily` objects"""

        return [get_family_by_id(i) for i in self._parent_family_ids]


    def get_subfamilies(self):
        """Returns a list of all target families which are a member of this family.

        :returns: list of :py:class:`TargetFamily` objects"""

        return [get_family_by_id(i) for i in self._sub_family_ids]
