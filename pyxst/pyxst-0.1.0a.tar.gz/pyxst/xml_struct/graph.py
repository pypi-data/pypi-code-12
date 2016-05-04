# -*- coding: utf-8 -*-
"""
This module contains the class that defines the structure of the XML documents
that will be returned by the :mod:`xml_struct` module.

This structure is a graph that contains different types of nodes,
mainly the XML elements and the XML attributes defined in
:mod:`xml_struct.graph_nodes` module.

.. autoclass:: XMLGraph
   :show-inheritance:

.. autofunction:: compute_textual_content

.. autodata:: TYPES_MAPPING
"""
__docformat__ = "restructuredtext en"


import operator

from ..xsd import types as xsdTypes
from ..xsd import utils as xsdUtils
from ..xsd.types import XsdSimpleListType, XsdSimpleUnionType, XsdComplexType
from ..xsd.groups import XsdGroup, XsdSequence, XsdAll
from ..dtd import constants as dtdConstants
from ..dtd.groups import DtdSequence, DtdGroup

from .utils import (
    MIXED, INFINITY, UNKNOWN, BOOLEAN, INTEGER, FLOAT, STRING, DATETIME,
    DURATION, BASE64, HEXA, ANY)
from .graph_nodes import XMLElement, XMLAttribute, Group, Sequence, Alternative
from .graph_target_relations import RELATION_CLASS


class XMLGraph(object):
    """
    Class that contains the graph representing the XML structure.

    The graph only contains
    :class:`~pyxst.xml_struct.graph.XMLElement` objects
    that contain themselves all the other nodes (groups of child
    elements, attributes).

    .. attribute:: name

       Name of the graph.

       Type: :class:`unicode`

    .. attribute:: elements

       Dictionary containing the elements defined in the graph. The elements
       are indexed with their identifier.

       Type: :class:`dict` of
       :class:`~pyxst.xml_struct.graph.XMLElement`
       indexed with :class:`unicode`

    .. attribute:: target_relations

       List of the target relations that are defined between the nodes
       of the graph.

       Target relations describe relations that can be translated into some
       arKItect concepts.

       Type: :class:`list` of
       :class:`~pyxst.xml_struct.graph_target_relations.TargetRelation`

    .. attribute:: _high_level_elts

       Private attribute that contains the XSD elements returned by the schema
       reader that are high level elements (elements defined at the top level
       of the schema).

       This set is only used while building the graph from the schema.

       Type: :class:`set` of
       :class:`~pyxst.xml_struct.xsd.elements.XsdElement`

    .. automethod:: __init__

    .. automethod:: __iter__

    .. automethod:: __len__
    """
    def __init__(self, name, source=u"", source_type=None, type_mapper=None):
        """
        Initializes a new graph.

        :param name:
            Name of the graph.
        :type name:
            :class:`unicode`
        """
        self.name = name
        self.source = source
        self.source_type = source_type
        if type_mapper is None:
            type_mapper = DefaultTypeMapper()
        self.type_mapper = type_mapper
        self.elements = []
        self.elts_index = {} # {qname: [XMLElement]}
        self.target_relations = []
        self._high_level_elts = set()
        self._elts_def_index = {} # {qname: [(XMLElement, XsdElement.uid or DtdElement.uid, XsdType.uid or None)]}
        # These attributes are used to keep track of the parameters used to
        # build the graph from a DTD (the DTD parser might have added namespaces
        # to the elements)
        self.dtd_ns_mapping = {}
        self.dtd_qualif_local_elt = False
        self.dtd_qualif_local_attr = False
        # The following attribute is used for analyzing a library of XML
        # documents whose structure is given by the graph. It is used to
        # count the number of times an element is actually used as a root
        # element in all the XML documents of the library.
        # (Some elements might never be used in the documents)
        self.root_uses = {} # {XMLElement: {xml_filename: uses_count},]}

    def __iter__(self):
        """
        Returns an iterator over the elements contained in the graph.

        :returns:
            An iterator over all the elements defined in the graph.
        :rtype:
            :class:`listiterator`
        """
        return iter(self.elements)

    def __len__(self):
        """
        Returns the number of elements in the graph.

        :returns:
            The number of elements defined in the graph.
        :rtype:
            :class:`int`
        """
        return len(self.elements)

    def find_all_elts(self, qname):
        return self.elts_index.get(qname, [])

    def find_high_level_elts(self, qname):
        result = []
        for elt in self.elts_index.get(qname, []):
            if elt.is_high_level:
                result.append(elt)
        return result

    def add_target_relation(self, relation_name, start_node, end_node):
        """
        Adds a target relation between ``start_node`` and ``end_node``.

        The target relation describes some relations between the graph
        nodes that can be translated into some arKItect concepts.

        :param relation_name:
            Name of the relation. This name will be used to get the class
            of the target relation thanks to the ``RELATION_CLASS``
            dictionary.
        :type relation_name:
            :class:`str`
        :param start_node:
            XML node where the target relation starts from.
        :type node:
            :class:`~pyxst.xml_struct.graph_nodes.XMLNode`
        :param end_node:
            XML node where the target relation ends to.
        :type node:
            :class:`~pyxst.xml_struct.graph_nodes.XMLNode`
        """
        relation = RELATION_CLASS[relation_name](start_node, end_node)
        self.target_relations.append(relation)

    def build_from_schema(self, schema):
        """
        Builds the graph from the ``schema`` object.

        This method will create all the elements, attributes and sub-elements
        that are defined in the XML Schema. It starts with the high-level
        elements declared at the top level of the schema and then goes on with
        the hierarchy of sub-elements in each element.

        :param schema:
            Schema object returned by the schema parser.
        :type schema:
            :class:~pyxst.xml_struct.xsd.root.XsdSchema`
        """
        self._high_level_elts = set(schema.elements.values())
        for xsd_elt in schema.elements.values():
            self.build_xsd_element(xsd_elt)
        self._high_level_elts = set()
        self.finalize()

    def build_xsd_element(self, xsd_elt, parent_elt=None):
        """
        Builds an XML element from the information defined in the ``xsd_elt``
        extracted from the schema object.

        This method creates a new element or returns a previously declared
        element (element already created in the graph).

        When creating a new element, this method creates the XML element itself,
        its attributes and the group that contains its sub-elements.

        :param xsd_elt:
            Element definition extracted from the XML Schema.
        :type xsd_elt:
            :class:`~pyxst.xml_struct.xsd.elements.XsdElement`
        :param parent_elt:
            Xml element of the graph that will be the parent of the newly
            created XML element.
        :type parent_elt:
            :class:`~pyxst.xml_struct.graph_nodes.XMLElement`
        :returns:
            Xml element that corresponds to the ``xsd_elt`` definition in the
            XML Schema and that is created and filled inside this method.
        :rtype:
           :class:`~pyxst.xml_struct.graph_nodes.XMLElement`
        """
        exist_elts = self._elts_def_index.get(xsd_elt.name, [])
        for gr_elt, xsd_elt_uid, xsd_type_uid in exist_elts:
            # In the list of graph elements with the same name, is there
            # an element created from an xsd_elt with the same uid or an
            # element created with an xsd_elt whose xsd_type has the same uid
            # (in both cases, it is the same element as the one required here)
            if xsd_elt.uid == xsd_elt_uid:
                if parent_elt is not None:
                    gr_elt.add_parent_elt(parent_elt)
                return gr_elt
            elif xsd_elt.xsd_type.uid == xsd_type_uid:
                if parent_elt is not None:
                    gr_elt.add_parent_elt(parent_elt)
                return gr_elt
        # Creates the new graph element
        gr_elt = XMLElement(xsd_elt.name,
                            (xsd_elt in self._high_level_elts))
        if parent_elt is not None:
            gr_elt.add_parent_elt(parent_elt)
        # Adds the element in the list of elements and in the index
        self.elements.append(gr_elt)
        self._elts_def_index.setdefault(xsd_elt.name, [])
        self._elts_def_index[xsd_elt.name].append(
            (gr_elt, xsd_elt.uid, xsd_elt.xsd_type.uid) )
        # Sets the content type of the graph element
        typ, lst, vals = compute_xsd_textual_content(xsd_elt.xsd_type, self.type_mapper)
        gr_elt.textual_content_type = typ
        gr_elt.textual_content_is_list = lst
        gr_elt.textual_content_values = vals
        if isinstance(xsd_elt.xsd_type, XsdComplexType):
            # Creates and adds the attributes on the graph element
            for xsd_usg in xsd_elt.xsd_type.attributes:
                if xsd_usg.max_occur == 0:
                    continue
                xsd_att = xsd_usg.referenced_node
                gr_att = XMLAttribute(xsd_att.name)
                typ, lst, vals = compute_xsd_textual_content(xsd_att.xsd_type, self.type_mapper)
                gr_att.textual_content_type = typ
                gr_att.textual_content_is_list = lst
                gr_att.textual_content_values = vals
                gr_elt.add_attribute(gr_att,
                                     xsd_usg.min_occur, xsd_usg.max_occur)
            # Processes the content (sub-elements)
            if xsd_elt.xsd_type.sub_content is not None:
                xsd_grp = xsd_elt.xsd_type.sub_content.referenced_node
                xsd_min = xsd_elt.xsd_type.sub_content.min_occur
                xsd_max = xsd_elt.xsd_type.sub_content.max_occur
                if xsd_max == xsdUtils.INFINITY:
                    xsd_max = INFINITY
                gr_grp = self.build_sub_elements_xsd_group(xsd_grp, xsd_max,
                                                       parent_elt=gr_elt)
                gr_elt.set_content(gr_grp, xsd_min, xsd_max)
        return gr_elt

    def build_sub_elements_xsd_group(self, xsd_group, max_occur, parent_elt=None):
        """
        Builds a group of the graph that contains XML elements that are
        children of an Xml element (``parent_elt``) and that is defined in
        the XML Schema with ``xsd_group``.

        This method creates a new group and adds in this group the sub-elements
        declared in ``xsd_group``. Several types of group can exist depending on
        the ``xsd_group`` (sequence, all, choice) and on the maximum occurence
        of the group.

        Inside a group, we can find sub-groups or sub-elements. This method
        recursively calls the methods of the graph to build the sub-elements
        and the sub-groups.

        :param xsd_group:
            Group definition extracted from the XML Schema.
        :type xsd_group:
            :class:`~pyxst.xml_struct.xsd.groups.XsdGroup`
        :param max_occur:
            Maximum occurence of the ``xsd_group`` inside its parent. Can
            be ``INFINITY``.
        :type max_occur:
            :class:`int` or :data:`~pyxst.xml_struct.utils.INFINITY`
        :param parent_elt:
            Xml element of the graph that will be the parent of the newly
            created group and its children.
        :type parent_elt:
            :class:`~pyxst.xml_struct.graph_nodes.XMLElement`
        :returns:
            Group that corresponds to the ``xsd_group`` definition in the
            XML Schema and that is created and filled inside this method.
        :rtype:
           :class:`~pyxst.xml_struct.graph_nodes.Group`
        """
        # Builds the group object that will be inserted in the graph
        if len(xsd_group) == 1:
            # If there is only one child in the group, the group is always a
            # simple group without order.
            gr_grp = Group(parent_elt)
        elif isinstance(xsd_group, XsdSequence):
            gr_grp = Sequence(parent_elt)
        elif isinstance(xsd_group, XsdAll):
            gr_grp = Group(parent_elt)
        else:
            gr_grp = Alternative(parent_elt)
        # Creates the child elements of the group and adds them in the group
        # object to be inserted in the graph
        for xsd_usg in iter(xsd_group):
            if xsd_usg.max_occur == 0:
                continue
            max_occur =  xsd_usg.max_occur
            if max_occur == xsdUtils.INFINITY:
                max_occur = INFINITY
            if isinstance(xsd_usg.referenced_node, XsdGroup):
                gr_child = self.build_sub_elements_xsd_group(
                    xsd_usg.referenced_node, max_occur,
                    parent_elt=parent_elt)
            else:
                gr_child = self.build_xsd_element(xsd_usg.referenced_node,
                                                  parent_elt=parent_elt)
            gr_grp.add_child(gr_child, xsd_usg.min_occur, max_occur)
        return gr_grp

    def build_from_dtd(self, dtd_def):
        """
        Builds the graph from the ``dtd_def`` object.

        This method will create all the elements, attributes and sub-elements
        that are defined in the DTD.

        :param dtd_def:
            DTD definition object returned by the DTD parser.
        :type schema:
            :class:~dtd.root.DtdDefinition`
        """
        for dtd_elt in dtd_def.elements.values():
            self.build_dtd_element(dtd_elt)
        self.finalize()

    def build_dtd_element(self, dtd_elt, parent_elt=None):
        """
        Builds an XML element from the information defined in the ``dtd_elt``
        extracted from the DTD Definition object.

        This method creates a new element or returns a previously declared
        element (element already created in the graph).

        When creating a new element, this method creates the XML element itself,
        its attributes and the group that contains its sub-elements.

        :param dtd_elt:
            Element definition extracted from the XML Schema.
        :type dtd_elt:
            :class:`~dtd.elements.DtdElement`
        :param parent_elt:
            Xml element of the graph that will be the parent of the newly
            created XML element.
        :type parent_elt:
            :class:`~xml_struct.graph_nodes.XMLElement`
        :returns:
            Xml element that corresponds to the ``dtd_elt`` definition in the
            DTD and that is created and filled inside this method.
        :rtype:
           :class:`~xml_struct.graph_nodes.XMLElement`
        """
        exist_elts = self._elts_def_index.get(dtd_elt.name, [])
        for gr_elt, dtd_elt_uid, _ in exist_elts:
            # In the list of graph elements with the same name, is there
            # an element created from a dtd_elt with the same uid
            # (then, it is the same element as the one required here)
            if dtd_elt.uid == dtd_elt_uid:
                if parent_elt is not None:
                    gr_elt.add_parent_elt(parent_elt)
                return gr_elt
        # Creates the new graph element
        gr_elt = XMLElement(dtd_elt.name,
                            True) # All elements are high-level elements
        if parent_elt is not None:
            gr_elt.add_parent_elt(parent_elt)
        # Adds the element in the list of elements and in the index
        self.elements.append(gr_elt)
        self._elts_def_index.setdefault(dtd_elt.name, [])
        self._elts_def_index[dtd_elt.name].append(
            (gr_elt, dtd_elt.uid, None) )
        # Sets the content type of the graph element
        typ, lst = compute_dtd_textual_content(dtd_elt.content_type)
        gr_elt.textual_content_type = typ
        gr_elt.textual_content_is_list = lst
        # Creates and adds the attributes on the graph element
        for dtd_usg in dtd_elt.attributes.values():
            if dtd_usg.max_occur == 0:
                continue
            dtd_att = dtd_usg.referenced_node
            gr_att = XMLAttribute(dtd_att.name)
            typ, lst = compute_dtd_textual_content(dtd_att.dtd_type)
            gr_att.textual_content_type = typ
            gr_att.textual_content_is_list = lst
            if dtd_att.possible_values is not None:
                gr_att.textual_content_values = set(dtd_att.possible_values)
            gr_elt.add_attribute(gr_att, dtd_usg.min_occur, dtd_usg.max_occur)
        # Processes the content (sub-elements)
        if dtd_elt.sub_content is not None:
            dtd_grp = dtd_elt.sub_content.referenced_node
            dtd_min = dtd_elt.sub_content.min_occur
            dtd_max = dtd_elt.sub_content.max_occur
            if dtd_max == dtdConstants.INFINITY:
                dtd_max = INFINITY
            gr_grp = self.build_sub_elements_dtd_group(dtd_grp, dtd_max,
                                                       parent_elt=gr_elt)
            gr_elt.set_content(gr_grp, dtd_min, dtd_max)
        return gr_elt

    def build_sub_elements_dtd_group(self, dtd_group, max_occur,
                                     parent_elt=None):
        """
        Builds a group of the graph that contains XML elements that are
        children of an Xml element (``parent_elt``) and that is defined in
        the DTD with ``dtd_group``.

        This method creates a new group and adds in this group the sub-elements
        declared in ``dtd_group``. Several types of group can exist depending on
        the ``dtd_group`` (sequence, choice) and on the maximum occurence
        of the group.

        Inside a group, we can find sub-groups or sub-elements. This method
        recursively calls the methods of the graph to build the sub-elements
        and the sub-groups.

        :param dtd_group:
            Group definition extracted from the DTD.
        :type dtd_group:
            :class:`~dtd.groups.DtdGroup`
        :param max_occur:
            Maximum occurence of the ``dtd_group`` inside its parent. Can
            be ``INFINITY``.
        :type max_occur:
            :class:`int` or :data:`~xml_struct.utils.INFINITY`
        :param parent_elt:
            Xml element of the graph that will be the parent of the newly
            created group and its children.
        :type parent_elt:
            :class:`~xml_struct.graph_nodes.XMLElement`
        :returns:
            Group that corresponds to the ``dtd_group`` definition in the
            XML Schema and that is created and filled inside this method.
        :rtype:
           :class:`~xml_struct.graph_nodes.Group`
        """
        # Builds the group object that will be inserted in the graph
        if len(dtd_group) == 1:
            # If there is only one child in the group, the group is always a
            # simple group without order.
            gr_grp = Group(parent_elt)
        elif isinstance(dtd_group, DtdSequence):
            gr_grp = Sequence(parent_elt)
        else:
            gr_grp = Alternative(parent_elt)
        # Creates the child elements of the group and adds them in the group
        # object to be inserted in the graph
        for dtd_usg in iter(dtd_group):
            if dtd_usg.max_occur == 0:
                continue
            max_occur =  dtd_usg.max_occur
            if max_occur == dtdConstants.INFINITY:
                max_occur = INFINITY
            if isinstance(dtd_usg.referenced_node, DtdGroup):
                gr_child = self.build_sub_elements_dtd_group(
                    dtd_usg.referenced_node, max_occur,
                    parent_elt=parent_elt)
            else:
                gr_child = self.build_dtd_element(dtd_usg.referenced_node,
                                                  parent_elt=parent_elt)
            gr_grp.add_child(gr_child, dtd_usg.min_occur, max_occur)
        return gr_grp

    def finalize(self):
        # Builds the elements index
        self.elts_index = {}
        for elt in self.elements:
            self.elts_index.setdefault(elt.qname, [])
            self.elts_index[elt.qname].append(elt)
        # Sorts the elements in the graph itself
        self.elements.sort(key=operator.attrgetter("qname"))
        # Finalizes all the elements (simplify, compute_content_type, sort)
        for elt in self.elements:
            elt.finalize()
        # Builds the root elements dictionary for the analysis of the uses
        # inside a library of XML documents
        self.root_uses = {}
        for elt in self.elements:
            if elt.is_high_level:
                self.root_uses[elt] = {}

    def reset_uses(self):
        for elt in self.root_uses:
            self.root_uses[elt] = {}
        for elt in self.elements:
            elt.reset_uses()


TYPES_MAPPING = {
    u"anyType"           : ANY,
    u"anySimpleType"     : STRING,
    u"boolean"           : BOOLEAN,
    u"integer"           : INTEGER,
    u"nonPositiveInteger": INTEGER,
    u"negativeInteger"   : INTEGER,
    u"nonNegativeInteger": INTEGER,
    u"positiveInteger"   : INTEGER,
    u"long"              : INTEGER,
    u"int"               : INTEGER,
    u"short"             : INTEGER,
    u"byte"              : INTEGER,
    u"unsignedLong"      : INTEGER,
    u"unsignedInt"       : INTEGER,
    u"unsignedShort"     : INTEGER,
    u"unsignedByte"      : INTEGER,
    u"decimal"           : FLOAT,
    u"float"             : FLOAT,
    u"double"            : FLOAT,
    u"string"            : STRING,
    u"normalizedString"  : STRING,
    u"Name"              : STRING,
    u"NCName"            : STRING,
    u"QName"             : STRING,
    u"token"             : STRING,
    u"language"          : STRING,
    u"anyURI"            : STRING,
    u"ID"                : STRING,
    u"NOTATION"          : STRING,
    u"NMTOKEN"           : STRING,
    u"IDREF"             : STRING,
    u"ENTITY"            : STRING,
    u"NMTOKENS"          : STRING,
    u"IDREFS"            : STRING,
    u"ENTITIES"          : STRING,
    u"CDATA"             : STRING,
    u"date"              : DATETIME,
    u"time"              : DATETIME,
    u"dateTime"          : DATETIME,
    u"gYear"             : DATETIME,
    u"gYearMonth"        : DATETIME,
    u"gMonth"            : DATETIME,
    u"gMonthDay"         : DATETIME,
    u"gDay"              : DATETIME,
    u"duration"          : DURATION,
    u"base64Binary"      : BASE64,
    u"hexBinary"         : HEXA,
    }
"""
Dictionary that maps the built-in types of XML Schema with elementary
types such as string, boolean, integer, float, datetime, duration,
base64 and hexadecimal.

Type: :class:`dict` of :class:`str` indexed with :class:`unicode`
"""


class MappingTypeMapper(object):
    """Map types according to types in TYPES_MAPPING. Combining returns a single type."""

    @staticmethod
    def map(content_type):
        try:
            return TYPES_MAPPING[content_type]
        except KeyError:
            return UNKNOWN

    @staticmethod
    def combine(type1, type2):
        """
        Tries to find a type that can describe both ``type1`` and ``type2``.

        This function is used when processing a union type (a type that can
        be any of several types) and returns a single type that can be used to
        describe all the types.

        For example, if the first type is a string and the second an integer,
        the function will return a string type. If the first type is an integer
        and the second a float, the function will return a float type, etc.
        In an XML document, all the data can be considered as string data, thus,
        at least, the combination of two different types can be a string type.

        This function uses the constants describing the types that are defined
        in this module.

        :param type1:
            Constant describing the  first type.
        :type type1:
            :class:`unicode`
        :param type2:
            Constant describing the  second type.
        :type type2:
            :class:`unicode`
        :returns:
            Constant describing a type that is combination of the two types
            given in parameter.
        :rtype:
            :class:`unicode`
        """
        if type1 == type2:
            return type1
        if type1 == UNKNOWN:
            return type2
        if type2 == UNKNOWN:
            return type1
        if (type1 == INTEGER and type2 == FLOAT) or \
                (type1 == FLOAT and type2 == INTEGER):
            return FLOAT
        if (type1 == ANY or type2 == ANY):
            return ANY
        return STRING


class NoTypeMapper(object):
    """Alternate type mapper that do no transformation. Combining types may return a set of possible
    types.
    """
    @staticmethod
    def map(content_type):
        return content_type

    @staticmethod
    def combine(type1, type2):
        if not isinstance(type1, set):
            type1 = set([type1])
        if not isinstance(type2, set):
            type2 = set([type2])
        types = type1 | type2
        if len(types) == 1:
            return types.pop()
        return types


DefaultTypeMapper = NoTypeMapper


def compute_xsd_textual_content(xsd_type, type_mapper=DefaultTypeMapper()):
    """
    Extracts information about the textual content of an element or an
    attribute thanks to the ``xsd_type`` object.

    The information consists of the type of the textual content
    converted to an elementary type thanks to
    :data:`~pyxst.xml_struct.graph.TYPES_MAPPING`, a flag
    indicating if the textual content is a space-separated list, and a
    set of predefined values if the textual content can only take
    specified values.

    :param xsd_type:
        XSD type object returns by the schema reader from which the
        information about the textual content will be extracted.
    :type xsd_type:
        :class:`~pyxst.xml_struct.xsd.types.XsdType`
    :returns:
        A tuple composed with the type of the textual content, a flag
        indicating if the textual content is a space-separated list,
        and a set of possible values if the textual content is
        constrained and can only take specified values.
    :rtype:
        Tuple composed with :class:`str`, :class:`bool`, :class:`set`
        of :class:`unicode`
    """
    # Complex type
    if isinstance(xsd_type, XsdComplexType):
        if ( xsd_type.content_type == xsdTypes.ELEMENTS_ONLY
             or xsd_type.content_type == xsdTypes.EMPTY):
            return None, False, None
        if xsd_type.content_type == xsdUtils.MIXED:
            return MIXED, False, None
    # Simple list type
    if xsd_type.content_type == xsdTypes.LIST:
        if isinstance(xsd_type, XsdSimpleListType):
            it_typ, it_lst, it_vals = \
                compute_xsd_textual_content(xsd_type.listitem_type, type_mapper)
            return it_typ, True, it_vals
        else:
            return compute_xsd_textual_content(xsd_type._base_type, type_mapper)
    # Simple union type
    if xsd_type.content_type == xsdTypes.UNION:
        if isinstance(xsd_type, XsdSimpleUnionType):
            typ = UNKNOWN
            lst = True
            vals = set()
            for xsd_sub_type in xsd_type.possible_types:
                sub_typ, sub_lst, sub_vals = \
                    compute_xsd_textual_content(xsd_sub_type, type_mapper)
                typ = type_mapper.combine(typ, sub_typ)
                lst = sub_lst and lst
                if sub_vals is not None and vals is not None:
                    vals = vals.union(sub_vals)
                else:
                    vals = None
            return typ, lst, vals
        else:
            bs_typ, bs_lst, bs_vals = \
                compute_xsd_textual_content(xsd_type._base_type, type_mapper)
            try:
                vals = xsd_type.constraints["enumeration"].value.copy()
                if bs_vals is not None:
                    vals = vals.union(bs_vals)
            except KeyError:
                vals = bs_vals
            return bs_typ, bs_lst, vals
    # Simple type
    typ = type_mapper.map(xsd_type.content_type)
    if xsd_type.content_type in [u"IDREFS", u"ENTITIES", u"NMTOKENS"]:
        lst = True
    else:
        lst = False
    try:
        vals = xsd_type.constraints["enumeration"].value.copy()
    except KeyError:
        vals = None
    return typ, lst, vals


def compute_dtd_textual_content(dtd_content_type):
    """
    Extracts information about the textual content of an element or an
    attribute thanks to the ``dtd_content_type`` value.

    The information consists of the type of the textual content
    converted to an elementary type thanks to
    :data:`~xml_struct.graph.TYPES_MAPPING`, a flag
    indicating if the textual content is a space-separated list.

    :returns:
        A tuple composed with the type of the textual content, a flag
        indicating if the textual content is a space-separated list.
    :rtype:
        Tuple composed with :class:`str`, :class:`bool`
    """
    if ( dtd_content_type == dtdConstants.ELEMENTS_ONLY
         or dtd_content_type == dtdConstants.EMPTY):
        return None, False
    if dtd_content_type == dtdConstants.MIXED:
        return MIXED, False
    if dtd_content_type == dtdConstants.TEXT_ONLY:
        return TYPES_MAPPING[u"string"], False
    try:
        typ = TYPES_MAPPING[dtd_content_type]
    except KeyError:
        typ = UNKNOWN
    if dtd_content_type in [u"IDREFS", u"ENTITIES", u"NMTOKENS"]:
        lst = True
    else:
        lst = False
    return typ, lst

