# -*- coding: utf-8 -*-
"""
This module defines the class where the data read from an XML Schema will
be stored.

Hence, the data read from an XML Schema is modeled as nodes deriving
from :class:`~pyxst.xml_struct.xsd.utils.XsdNode` and
these nodes are stored in a dedicated structure: the
:class:`~pyxst.xml_struct.xsd_reader.XsdSchema` class.

This class also has methods to build the nodes from the XML Schema data.

.. autodata:: XSD_BUILT_IN_TYPES

.. autodata:: CAT_MAPPING

.. autodata:: NODE_MAPPING

.. autoclass:: XsdSchema
   :members:
   :undoc-members:
   :show-inheritance:
"""
__docformat__ = "restructuredtext en"


from .errors import XsdError
from .utils import (
    ATTRIBUTE, ELEMENT, GROUP, ATTRIBUTE_GROUP, TYPE, XSD_NS, XsdUsage)
from .utils import (INFINITY, MIXED, split_qname, resolve_xml_qname)
from .elements import XsdElement
from .attributes import (XsdAttribute, XsdAttributeGroup)
from .types import (
    XsdComplexType, XsdSimpleType, XsdSimpleListType, XsdSimpleUnionType,
    XsdType, CONSTRAINT_MAPPING, RESTRICTION, EXTENSION)
from .groups import (XsdChoice, XsdAll, XsdSequence)
from traceback import format_exc


XSD_BUILT_IN_TYPES = set([
        u"anyType", u"anySimpleType", u"boolean", u"base64Binary", u"hexBinary",
        u"float", u"decimal", u"integer", u"nonPositiveInteger",
        u"negativeInteger", u"long", u"int", u"short", u"byte",
        u"nonNegativeInteger", u"unsignedLong", u"unsignedInt",
        u"unsignedShort", u"unsignedByte", u"positiveInteger", u"double",
        u"anyURI", u"QName", u"NOTATION", u"duration", u"dateTime", u"time",
        u"date", u"gYearMonth", u"gYear", u"gMonthDay", u"gDay", u"gMonth",
        u"string", u"normalizedString", u"token", u"language", u"Name",
        u"NCName", u"ID", u"IDREF", u"IDREFS", u"ENTITY", u"ENTITIES",
        u"NMTOKEN", u"NMTOKENS", ])
"""
Set containing the built-in types defined in the XSD standard.

Type: set of :class:`unicode`
"""

CAT_MAPPING = {u"element"                   : ELEMENT,
               u"attributeGroup"            : ATTRIBUTE_GROUP,
               u"attribute"                 : ATTRIBUTE,
               u"complexType"               : TYPE,
               u"simpleType"                : TYPE,
               u"simpleType/restriction"    : TYPE,
               u"simpleType/list"           : TYPE,
               u"simpleType/union"          : TYPE,
               u"group"                     : GROUP,
               u"all"                       : GROUP,
               u"choice"                    : GROUP,
               u"sequence"                  : GROUP,
               }
"""
Dictionary mapping the XML Schema item types (the name of the XML elements
inside the XML Schema) and the categories of nodes defined in
:mod:`~pyxst.xml_struct.xsd.utils` module.

Type: Dictionary of :class:`str` indexed with :class:`unicode`
"""

NODE_MAPPING = {u"element"                   : XsdElement,
                u"attributeGroup"            : XsdAttributeGroup,
                u"attribute"                 : XsdAttribute,
                u"complexType"               : XsdComplexType,
                u"simpleType"                : XsdSimpleType,
                u"simpleType/restriction"    : XsdSimpleType,
                u"simpleType/list"           : XsdSimpleListType,
                u"simpleType/union"          : XsdSimpleUnionType,
                u"all"                       : XsdAll,
                u"choice"                    : XsdChoice,
                u"sequence"                  : XsdSequence,
                }
"""
Dictionary mapping the XML Schema item types (the name of the XML elements
inside the XML Schema) and the classes of nodes defined in
:mod:`~pyxst.xml_struct.xsd.utils` module.

Type: Dictionary of :class:`class` indexed with :class:`unicode`
"""


class XsdSchema(object):
    """
    Class representing an XML Schema.

    This class stores the group nodes, the type nodes, the attribute
    group nodes, the attribute nodes and the element nodes defined at
    the highest level of the XML Schema.

    This class also has a factory method to build new nodes from XML objects
    read in the XML Schema.

    .. attribute:: groups

       Dictionary of the high level group nodes indexed with their name.

       Type: dictionary of
       :class:`~pyxst.xml_struct.xsd.groups.XsdGroup` indexed with
       :class:`unicode`

    .. attribute:: types

       Dictionary of the high level type nodes indexed with their name.

       Type: dictionary of
       :class:`~pyxst.xml_struct.xsd.types.XsdType` indexed with
       :class:`unicode`

    .. attribute:: attr_groups

       Dictionary of the high level attribute group nodes indexed with
       their name.

       Type: dictionary of
       :class:`~pyxst.xml_struct.xsd.attributes.XsdAttributeGroup`
       indexed with :class:`unicode`

    .. attribute:: attributes

       Dictionary of the high level attribute nodes indexed with their name.

       Type: dictionary of
       :class:`~pyxst.xml_struct.xsd.attributes.XsdAttribute`
       indexed with :class:`unicode`

    .. attribute:: elements

       Dictionary of the high level element nodes indexed with their name.

       Type: dictionary of
       :class:`~pyxst.xml_struct.xsd.elements.XsdElement` indexed
       with :class:`unicode`

    .. attribute:: storages

       Dictionary indexing the previous attributes with the category of the
       nodes they will contain. For example, the ``elements`` attribute is
       indexed with the ``ELEMENT`` constant.

       Type: dictionary of :class:`dict` indexed with :class:`str`

    .. attribute:: all_types

       List containing all the types that exist in this schema object. The
       types include the high-level types (stored in ``types`` attribute)
       and the local types defined into other nodes.

       Type: List of
       :class:`~pyxst.xml_struct.xsd.types.XsdType`

    .. attribute:: _target_ns

       Private attribute containing the target namespace used to qualify
       the names of the items defined in the XML Schema that is currently
       read. If None, the names are left unqualified.

       This namespace changes when reading included XML Schemas.

       Type: :class:`unicode`

    .. attribute:: _qualified_attrs

       Private flag set to ``True`` if the names of the attributes in the
       schema are qualified names (namespace + local name). However, each
       attribute definition can locally change this behaviour.

       The value of this flag changes when reading included XML Schemas.

       Type: :class:`boolean`

    .. attribute:: _qualified_elts

       Private flag set to ``True`` if the names of the elements in the schema
       are qualified names (namespace + local name). However, each
       element definition can locally change this behaviour.

       The value of this flag changes when reading included XML Schemas.

       Type: :class:`boolean`

    .. attribute:: _xsd_file

       Private attribute containing the file name of the XML Schema that is
       currently read. It is mainly use when raising exceptions.

       This name changes when reading included XML Schemas.

       Type: :class:`str`

    .. automethod:: __init__
    """
    def __init__(self):
        """
        Initializes a new XsdSchema root node.
        """
        self.groups = {}
        self.types = {}
        self.attr_groups = {}
        self.attributes = {}
        self.elements = {}
        self.storages = {ATTRIBUTE: self.attributes,
                         ATTRIBUTE_GROUP: self.attr_groups,
                         ELEMENT: self.elements,
                         TYPE: self.types,
                         GROUP: self.groups, }
        self.all_types = []
        self._target_ns = None
        self._qualified_attrs = False
        self._qualified_elts = False
        self._xsd_file = ""
        # Initializes the most basic built-in types (anyType and anySimpleType)
        for local_name in (u"anyType", u"anySimpleType"):
            type_name = u"{{{0}}}{1}".format(XSD_NS, local_name)
            type_node = XsdType(type_name)
            self.store_definition_node(type_node)

    def store_definition_node(self, node):
        """
        Stores a new high level node in this object.

        Checks there is not already a node with the same name in the
        corresponding storage.

        :param node:
            Node to be stored in this object.
        :type item_type:
            :class:`~pyxst.xml_struct.xsd.utils.XsdNode`
        """
        stor = self.storages[node.category]
        if node.name in stor:
            raise XsdError("Found a second definition for %s %s in the %s XML "
                           "Schema"
                           % (node.category, node.name, self._xsd_file))
        stor[node.name] = node
        if node.category is TYPE:
            self.all_types.append(node)

    def get_definition_node(self, category, name):
        """
        Returns the high level definition node with the ``name`` name
        extracted from the storage corresponding to ``category``.

        This node has been previously stored in one of the storages of this
        class. If it can't be found, raises an error.

        :param category:
            Category (element, attribute, attribute group, type, group) of
            the node to be found.
        :type item_type:
            :class:`str`
        :param name:
            Name of the node to be found.
        :type name:
            :class:`unicode`
        :returns:
            The definition node.
        :rtype:
            :class:`~pyxst.xml_struct.xsd.utils.XsdNode`
        """
        try:
            stor = self.storages[category]
        except KeyError:
            raise XsdError("Can't find node of unknown category (%s)"
                           % category)
        if name not in stor:
            raise XsdError("Can't find the definition node for %s %s declared "
                           "in the %s XML Schema"
                           % (category, name, self._xsd_file))
        return stor[name]

    def create_node(self, xml_obj, name=None, uid_prefix=u""):
        """
        Creates a new node from the information extracted from ``xml_obj``
        XML element read in an XML Schema.

        The created node is empty: it is just an object of the correct class
        with its name set.

        The created node is not added to the storages where only high level
        nodes are kept. If the node must be kept in such a storage, the
        ``store_definition_node`` must be called.

        :param xml_obj:
            XML element defining a node (element, attribute, type, etc.) in
            an XML Schema.
        :type xml_obj:
            :class:`~lxml.etree.Element`
        :param name:
            Name specified for the new node. If left to ``None``, the name is
            extracted from ``xml_obj``. In this case, if no name is defined in
            ``xml_obj`` (in ``name`` attribute), an exception is raised.
        :type name:
            :class:`unicode`
        :returns:
            A new node corresponding to ``xml_obj``
        :rtype:
            :class:`~pyxst.xml_struct.xsd.utils.XsdNode`
        """
        # Extracts the name of the node
        if name is None:
            name = self.get_node_name(xml_obj)
        if name is None:
            raise XsdError("Found an object (%s) without a name in %s XML "
                           "Schema" % (xml_obj, self._xsd_file))
        obj_ns, obj_sort = split_qname(xml_obj.tag)
        # Deals with specific sorts of XML Schema objects
        if obj_sort == u"group":
            # Finds the child node that is not an annotation to know what
            # kind of item this will be (choice, sequence or all)
            for obj_child in xml_obj:
                ns, obj_child_sort = split_qname(obj_child.tag)
                if ns != XSD_NS or obj_child_sort == u"annotation":
                    continue
                obj_sort = obj_child_sort
        if obj_sort == u"simpleType":
            # Finds the child node that is not an annotation to know what
            # kind of simple type this will be (simple type, simple list type
            # or simple union type)
            for obj_child in xml_obj:
                ns, obj_child_sort = split_qname(obj_child.tag)
                if ns != XSD_NS or obj_child_sort == u"annotation":
                    continue
                obj_sort = u"simpleType/" + obj_child_sort
        if obj_ns != XSD_NS or obj_sort not in NODE_MAPPING:
            raise XsdError("Can't create a node from %s object in %s XML "
                           "Schema" % (xml_obj, self._xsd_file))
        return NODE_MAPPING[obj_sort](name, uid_prefix=uid_prefix)

    def get_node_name(self, xml_obj):
        """
        Gets the name of the node that corresponds to the ``xml_obj``
        XML element read in an XML Schema.

        Basically, this name is the name defined in the ``name`` attribute of
        ``xml_obj`` but it is sometimes necessary to add a namespace before
        this local name.

        If ``xml_obj`` has no ``name`` attribute (anonymous object), ``None``
        is returned.

        :param xml_obj:
            XML element defining a node (element, attribute, type, etc.) in
            an XML Schema.
        :type xml_obj:
            :class:`~lxml.etree.Element`
        :returns:
            The name of the node that corresponds to ``xml_obj``
        :rtype:
            :class:`unicode`
        """
        _, def_categ = split_qname(xml_obj.tag)
        name = xml_obj.get(u"name")
        # No name specified, returns ``None``
        if name is None:
            return None
        # A namespace is specified, returns the qualified name
        if name.find(u":") != -1:
            return resolv_xml_qname(name, xml_obj.nsmap)
        # No namespace is specified, adds the target namespace if necessary
        add_target_ns = False
        if self._target_ns is not None:
            if xml_obj.getparent().tag != u"{{{0}}}schema".format(XSD_NS):
                # This is not a top-level definition
                if CAT_MAPPING[def_categ] is ATTRIBUTE:
                    if xml_obj.get(u"form") is None:
                        add_target_ns = self._qualified_attrs
                    else:
                        add_target_ns = (xml_obj.get(u"form") == u"qualified")
                elif CAT_MAPPING[def_categ] is ELEMENT:
                    if xml_obj.get(u"form") is None:
                        add_target_ns = self._qualified_elts
                    else:
                        add_target_ns = (xml_obj.get(u"form") == u"qualified")
            else:
                # Always adds target namespace to top-level definition and
                # definition that are neither elements nor attributes.
                add_target_ns = True
        if add_target_ns:
            return u"{{{0}}}{1}".format(self._target_ns, name)
        else:
            return name

    def get_type_nodes_from_xml(self, xml_obj, ref_attr_name, uid_prefix=u""):
        """
        Gets the type nodes that are referenced or contained into
        the ``xml_obj`` XML element read in an XML Schema.

        The type nodes can either be high level types referenced in
        the ``ref_attr_name`` attribute of ``xml_obj`` or new local types
        directly defined in children of ``xml_obj``. These children are
        ``simpleType`` or ``complexType`` XML elements.

        Most of the times, only one type node is referenced or
        defined but in the case of an ``union`` XML element, several
        type nodes are referenced or defined.

        :param xml_obj:
            XML element containing or referencing a type in the XML
            Schema (typically, ``xsd:attribute``, ``xsd:simpleContent``,
            ``xsd:restriction``, ``xsd:element``, etc.)
        :type xml_obj:
            :class:`~lxml.etree.Element`
        :param ref_attr_name:
            Name of the attribute of ``xml_obj`` that might contain
            references towards the types.
        :type ref_attr_name:
            :class:`unicode`
        :param name_prefix:
            Prefix added before the name created for anonymous types defined
            in the children of ``xml_obj``.
        :type name_prefix:
            :class:`unicode`
        :returns:
            The list of type nodes referenced or defined into ``xml_obj``
        :rtype:
            List of
            :class:`~pyxst.xml_struct.xsd.types.XsdType`
        """
        nodes = []
        ref_names = xml_obj.get(ref_attr_name, "")
        # First, gets the types specified with a reference
        for type_name in ref_names.split():
            type_name = resolve_xml_qname(type_name, xml_obj.nsmap)
            try:
                nodes.append(self.get_definition_node(TYPE, type_name))
            except XsdError:
                # If the referenced type is an unknown built-in type, adds
                # it as a high level type
                ns, type_local_name = split_qname(type_name)
                if ns == XSD_NS and type_local_name in XSD_BUILT_IN_TYPES:
                    type_node = XsdSimpleType(type_name)
                    self.store_definition_node(type_node)
                    nodes.append(type_node)
                else:
                    raise
        # Secondly, builds types defined in children of xml_obj
        s_num = c_num = 0
        for child_obj in xml_obj:
            ns, child_name = split_qname(child_obj.tag)
            if ns == XSD_NS and child_name == u"simpleType":
                type_name = "simpleType%d" % s_num
                type_node = self.create_node(child_obj, name=type_name,
                                             uid_prefix=uid_prefix)
                self.fill_simple_type_node(type_node, child_obj)
                s_num += 1
                self.all_types.append(type_node)
                nodes.append(type_node)
            if ns == XSD_NS and child_name == u"complexType":
                type_name = "complexType%d" % c_num
                type_node = self.create_node(child_obj, name=type_name,
                                             uid_prefix=uid_prefix)
                self.fill_complex_type_node(type_node, child_obj)
                c_num += 1
                self.all_types.append(type_node)
                nodes.append(type_node)
        # Thirdly, if no type has been found and xml_obj is an element or
        # an attribute, uses "anyType" or "anySimpleType" as its type
        ns, loc_name = split_qname(xml_obj.tag)
        if len(nodes) == 0 and loc_name == "element":
            nodes.append(self.get_definition_node(
                TYPE, u"{{{0}}}anyType".format(XSD_NS)))
        elif len(nodes) == 0 and loc_name == "attribute":
            nodes.append(self.get_definition_node(
                TYPE, u"{{{0}}}anySimpleType".format(XSD_NS)))
        return nodes

    def get_group_node_from_xml(self, xml_obj, name="", uid_prefix=u""):
        """
        Gets the group node that corresponds to the ``xml_obj``
        XML element read in an XML Schema.

        The group node can either be a high level group referenced in
        the ``ref`` attribute of ``xml_obj`` if this element is a
        ``group`` XML element or a local group defined in ``xml_obj``
        if this element is a ``all``, a ``choice`` or a ``sequence``
        XML elements

        :param xml_obj:
            XML element corresponding to a group in the XML
            Schema (typically, ``xsd:group``, ``xsd:all``, etc.)
        :type xml_obj:
            :class:`~lxml.etree.Element`
        :param name:
            Name of the group if the group is defined in ``xml_obj``.
        :type name:
            :class:`unicode`
        :returns:
            The group node that corresponds to ``xml_obj``
        :rtype:
            :class:`~pyxst.xml_struct.xsd.groups.XsdGroup`
        """
        if xml_obj.tag == "{%s}group" % XSD_NS:
            # Group is specified with a reference
            ref_name = resolve_xml_qname(xml_obj.get(u"ref"), xml_obj.nsmap)
            if ref_name is None:
                raise XsdError("Group %s should have a ref attribute to point "
                               "towards a defined group in %s XML Schema"
                               % (xml_obj, self._xsd_file))
            node = self.get_definition_node(GROUP, ref_name)
        else:
            node = self.create_node(xml_obj, name=name, uid_prefix=uid_prefix)
            self.fill_group_node(node, xml_obj)
        return node

    def get_element_node_from_xml(self, xml_obj, uid_prefix=u""):
        """
        Gets the element node that corresponds to the ``xml_obj``
        XML element read in an XML Schema.

        The element node can either be a high level element referenced with
        a ``ref`` attribute in ``xml_obj`` or a new local element directly
        defined by ``xml_obj``.

        :param xml_obj:
            XML element defining an element use in the XML Schema (typically,
            ``xsd:element``).
        :type xml_obj:
            :class:`~lxml.etree.Element`
        :returns:
            The element node that corresponds to ``xml_obj``
        :rtype:
            :class:`~pyxst.xml_struct.xsd.attributes.XsdElement`
        """
        ref_name = resolve_xml_qname(xml_obj.get(u"ref"), xml_obj.nsmap)
        if ref_name is not None:
            # Element is specified with a reference
            node = self.get_definition_node(ELEMENT, ref_name)
        else:
            # Element is defined in xml_obj
            node = self.create_node(xml_obj, uid_prefix=uid_prefix)
            self.fill_element_node(node, xml_obj)
        return node

    def get_attribute_node_from_xml(self, xml_obj, uid_prefix=u""):
        """
        Gets the attribute node that corresponds to the ``xml_obj``
        XML element read in an XML Schema.

        The attribute node can either be a high level attribute referenced with
        a ``ref`` attribute in ``xml_obj`` or a new local attribute directly
        defined by ``xml_obj``.

        :param xml_obj:
            XML element defining an attribute use in the XML Schema (typically,
            ``xsd:attribute``).
        :type xml_obj:
            :class:`~lxml.etree.Element`
        :returns:
            The attribute node that corresponds to ``xml_obj``
        :rtype:
            :class:`~pyxst.xml_struct.xsd.attributes.XsdAttribute`
        """
        ref_name = resolve_xml_qname(xml_obj.get(u"ref"), xml_obj.nsmap)
        if ref_name is not None:
            # Attribute is specified with a reference
            node = self.get_definition_node(ATTRIBUTE, ref_name)
        else:
            # Attribute is defined in xml_obj
            node = self.create_node(xml_obj, uid_prefix=uid_prefix)
            self.fill_attribute_node(node, xml_obj)
        return node

    def get_min_max_occur_from_xml(self, xml_obj, item_node):
        """
        Returns the minimum and maximum occurences specified on ``xml_obj``
        for ``item_node``.

        If they are not specified, the default value (``1``) is returned.

        Minimum and maximum occurences will be used to insert the ``item_node``
        inside its parent node.

        :param xml_obj:
            XML element defining the use of an element or a group in the XML
            Schema (typically, ``xsd:element``, ``xsd:group``, ``xsd:sequence``,
            etc.)
        :type xml_obj:
            :class:`~lxml.etree.Element`
        :param item_node:
            Node corresponding to ``xml_obj``. This node is just used to
            display context information in case of error.
        :type item_node:
            :class:`~pyxst.xml_struct.xsd.utils.XsdNode`
        :returns:
            Tuple composed with the minimum occurence and the maximum occurence
            of ``item_node``. The maximum occurence can be either an integer
            or ``INFINITY``.
        :rtype:
            tuple composed with :class:`int`, (:class:`int` or
            :data:`~pyxst.xml_struct.utils.INFINITY`)
        """
        if xml_obj.get(u"maxOccurs") == u"unbounded":
            max_occur = INFINITY
        else:
            try:
                max_occur = int(xml_obj.get(u"maxOccurs", 1))
            except ValueError, exc:
                raise XsdError("Can't read maximum occurence for %s "
                               "(should be an integer) in %s XML Schema:\n%s"
                               % (item_node, self._xsd_file, format_exc()))
        try:
            min_occur = int(xml_obj.get(u"minOccurs", 1))
        except ValueError:
            raise XsdError("Can't read minimum occurence for %s "
                           "(should be an integer) in %s XML Schema:\n%s"
                           % (item_node, self._xsd_file, format_exc()))
        return min_occur, max_occur

    def add_attributes_to_node(self, node, xml_obj):
        """
        Adds into the ``node`` object the attributes and attribute groups
        found in the ``xml_obj`` XML element read in an XML Schema.

        :param node:
            Attribute group node or Complex type node where attributes and
            attribute sub-groups must be added.
        :param node:
            :class:`~pyxst.xml_struct.xsd.attributes.XsdAttributeGroup`
            or :class:`~pyxst.xml_struct.xsd.type.XsdComplexType`
        :param xml_obj:
            XML element containing definitions of attributes and attribute
            groups in the XML Schema (typically, ``xsd:attributeGroup``,
            ``xsd:complexType``, ``xsd:complexContent``, ``xsd:simpleContent``).
        :type xml_obj:
            :class:`~lxml.etree.Element`
        :returns:
            ``node`` after the attributes and attribute groups have been added.
        :rtype:
            :class:`~pyxst.xml_struct.xsd.attributes.XsdAttributeGroup`
            or :class:`~pyxst.xml_struct.xsd.type.XsdComplexType`
        """
        for child_obj in xml_obj:
            ns, child_name = split_qname(child_obj.tag)
            if ns == XSD_NS and child_name == u"attributeGroup":
                ref_name = resolve_xml_qname(child_obj.get(u"ref"),
                                             child_obj.nsmap)
                grp_node = self.get_definition_node(ATTRIBUTE_GROUP,
                                                    ref_name)
                node.add_attribute_group(grp_node)
            elif ns == XSD_NS and child_name == u"attribute":
                attr_node = self.get_attribute_node_from_xml(
                    child_obj, uid_prefix=node.uid)
                attr_use = child_obj.get(u"use")
                if attr_use == u"prohibited":
                    min_occur = 0
                    max_occur = 0
                elif attr_use == u"required":
                    min_occur = 1
                    max_occur = 1
                else: # u"optional" is the default value
                    min_occur = 0
                    max_occur = 1
                node.add_attribute(attr_node, min_occur, max_occur)
        return node

    def fill_element_node(self, node, xml_obj):
        """
        Fills the ``node`` object with the information found in the ``xml_obj``
        XML element read in an XML Schema.

        :param node:
            Element node that must be filled with the information
            available in ``xml_obj``.
        :param node:
            :class:`~pyxst.xml_struct.xsd.elements.XsdElement`
        :param xml_obj:
            XML element defining an element in the XML Schema
            (typically, ``xsd:element``).
        :type xml_obj:
            :class:`~lxml.etree.Element`
        :returns:
            ``node`` after it has been filled.
        :rtype:
            :class:`~pyxst.xml_struct.xsd.elements.XsdElement`
        """
        type_nodes = self.get_type_nodes_from_xml(xml_obj, u"type",
                                                  uid_prefix=node.uid)
        if len(type_nodes) == 0:
            # Tries to get the type from the substitution group
            subs_name = xml_obj.get("substitutionGroup")
            if subs_name is not None:
                subs_node = self.get_definition_node(ELEMENT, subs_name)
                if subs_node.xsd_type is not None:
                    node.xsd_type = subs_node.xsd_type
                else:
                    subs_node._elts_with_same_type.append(node)
            else:
                raise XsdError("%s should contain either a reference or an "
                               "inner definition of type in %s XML Schema"
                               % (node, self._xsd_file))
        node.xsd_type = type_nodes[0]
        return node

    def fill_attribute_group_node(self, node, xml_obj):
        """
        Fills the ``node`` object with the information found in the ``xml_obj``
        XML element read in an XML Schema.

        :param node:
            Attribute group node that must be filled with the information
            available in ``xml_obj``.
        :param node:
            :class:`~pyxst.xml_struct.xsd.attributes.XsdAttributeGroup`
        :param xml_obj:
            XML element defining an attribute group in the XML Schema
            (typically, ``xsd:attributeGroup``).
        :type xml_obj:
            :class:`~lxml.etree.Element`
        :returns:
            ``node`` after it has been filled.
        :rtype:
            :class:`~pyxst.xml_struct.xsd.attributes.XsdAttributeGroup`
        """
        self.add_attributes_to_node(node, xml_obj)
        return node

    def fill_attribute_node(self, node, xml_obj):
        """
        Fills the ``node`` object with the information found in the ``xml_obj``
        XML element read in an XML Schema.

        Filling an attribute only consists in linking it to its type node.

        :param node:
            Attribute node that must be filled with the information available
            in ``xml_obj``.
        :param node:
            :class:`~pyxst.xml_struct.xsd.attributes.XsdAttribute`
        :param xml_obj:
            XML element defining an attribute in the XML Schema (typically,
            ``xsd:attribute``).
        :type xml_obj:
            :class:`~lxml.etree.Element`
        :returns:
            ``node`` after it has been filled.
        :rtype:
            :class:`~pyxst.xml_struct.xsd.attributes.XsdAttribute`
        """
        type_nodes = self.get_type_nodes_from_xml(xml_obj, u"type",
                                                  uid_prefix=node.uid)
        if len(type_nodes) == 0:
            raise XsdError("%s should contain either a reference or an inner "
                           "definition of type in %s XML Schema"
                           % (node, self._xsd_file))
        node.xsd_type = type_nodes[0]
        return node

    def fill_simple_type_node(self, node, xml_obj):
        """
        Fills the ``node`` object with the information found in the ``xml_obj``
        XML element read in an XML Schema.

        :param node:
            Simple type node that must be filled with the information available
            in ``xml_obj``.
        :param node:
            :class:`~pyxst.xml_struct.xsd.types.XsdSimpleType`
        :param xml_obj:
            XML element defining a simple type in the XML Schema (typically,
            ``xsd:simpleType``).
        :type xml_obj:
            :class:`~lxml.etree.Element`
        :returns:
            ``node`` after it has been filled.
        :rtype:
            :class:`~pyxst.xml_struct.xsd.types.XsdSimpleType`
        """
        if xml_obj.find(u"{%s}restriction" % XSD_NS) is not None:
            # Restriction of a base simple type
            rst_obj = xml_obj.find(u"{%s}restriction" % XSD_NS)
            type_nodes = self.get_type_nodes_from_xml(
                rst_obj, u"base", uid_prefix=node.uid+u"/restriction")
            if len(type_nodes) == 0:
                raise XsdError("Restriction in %s should contain either a "
                               "reference or an inner definition of type in "
                               "%s XML Schema" % (node, self._xsd_file))
            node._base_type = type_nodes[0]
            node._deriv_method = RESTRICTION
            for child_obj in rst_obj:
                ns, child_name = split_qname(child_obj.tag)
                if ns != XSD_NS or child_name not in CONSTRAINT_MAPPING:
                    continue
                node.add_constraint(child_name, child_obj.get(u"value"))
        elif xml_obj.find(u"{%s}list" % XSD_NS) is not None:
            # List of several items (space separated) whose type is simple type
            lst_obj = xml_obj.find(u"{%s}list" % XSD_NS)
            type_nodes = self.get_type_nodes_from_xml(
                lst_obj, u"itemType", uid_prefix=node.uid+u"/list")
            if len(type_nodes) == 0:
                raise XsdError("List in %s should contain either a reference "
                               "or an inner definition of type in %s XML "
                               "Schema" % (node, self._xsd_file))
            node.listitem_type = type_nodes[0]
        elif xml_obj.find(u"{%s}union" % XSD_NS) is not None:
            # Union of several possible simple types
            uni_obj = xml_obj.find(u"{%s}union" % XSD_NS)
            type_nodes = self.get_type_nodes_from_xml(
                uni_obj, u"memberTypes", uid_prefix=node.uid+u"/union")
            if len(type_nodes) == 0:
                raise XsdError("Union in %s should contain references or "
                               "inner definitions of type in %s XML Schema"
                               % (node, self._xsd_file))
            for typ in type_nodes:
                node.possible_types.add(typ)
        else:
            raise XsdError("%s should contain either a <restriction> or a "
                           "<list> or an <union> child in the %s XML Schema"
                           % (node, self._xsd_file))
        return node

    def fill_complex_type_node(self, node, xml_obj):
        """
        Fills the ``node`` object with the information found in the ``xml_obj``
        XML element read in an XML Schema.

        :param node:
            Complex type node that must be filled with the information
            available in ``xml_obj``.
        :param node:
            :class:`~pyxst.xml_struct.xsd.types.XsdComplexType`
        :param xml_obj:
            XML element defining a complex type in the XML Schema (typically,
            ``xsd:complexType``).
        :type xml_obj:
            :class:`~lxml.etree.Element`
        :returns:
            ``node`` after it has been filled.
        :rtype:
            :class:`~pyxst.xml_struct.xsd.types.XsdComplexType`
        """
        if xml_obj.find(u"{%s}simpleContent" % XSD_NS) is not None:
            self.fill_node_from_simple_content(node,
                                  xml_obj.find(u"{%s}simpleContent" % XSD_NS))
        elif xml_obj.find(u"{%s}complexContent" % XSD_NS) is not None:
            if xml_obj.get(u"mixed", u"false") == u"true":
                node.content_type = MIXED
            self.fill_node_from_complex_content(node,
                                 xml_obj.find(u"{%s}complexContent" % XSD_NS))
        else:
            if xml_obj.get(u"mixed", u"false") == u"true":
                node.content_type = MIXED
            grp_node = None
            for child_obj in xml_obj:
                ns, child_sort = split_qname(child_obj.tag)
                if ns == XSD_NS and child_sort == u"group":
                    grp_node = self.get_group_node_from_xml(child_obj,
                                                            uid_prefix=node.uid)
                    break
                if ns == XSD_NS and child_sort in [u"all", u"choice",
                                                   u"sequence"]:
                    name = "%s/%s" % (node.name, child_sort)
                    grp_node = self.get_group_node_from_xml(child_obj, name,
                                                            uid_prefix=node.uid)
                    break
            if grp_node is not None:
                min_occur, max_occur = self.get_min_max_occur_from_xml(
                    child_obj, grp_node)
                node.sub_content = XsdUsage(grp_node, min_occur, max_occur)
            self.add_attributes_to_node(node, xml_obj)
        return node

    def fill_node_from_simple_content(self, node, xml_obj):
        """
        Fills the ``node`` object with the information found in the ``xml_obj``
        XML element read in an XML Schema.

        :param node:
            Complex type with simple content node that must be filled with
            the information available in ``xml_obj``.
        :param node:
            :class:`~pyxst.xml_struct.xsd.types.XsdComplexType`
        :param xml_obj:
            XML element defining a simple content in a complex type in the
            XML Schema (typically, ``xsd:simpleContent``).
        :type xml_obj:
            :class:`~lxml.etree.Element`
        :returns:
            ``node`` after it has been filled.
        :rtype:
            :class:`~pyxst.xml_struct.xsd.types.XsdComplexType`
        """
        if xml_obj.find(u"{%s}restriction" % XSD_NS) is not None:
            der_obj = xml_obj.find(u"{%s}restriction" % XSD_NS)
            der_meth = RESTRICTION
            for child_obj in der_obj:
                ns, child_name = split_qname(child_obj.tag)
                if ns != XSD_NS or child_name not in CONSTRAINT_MAPPING:
                    continue
                node.add_constraint(child_name, child_obj.get(u"value"))
        elif xml_obj.find(u"{%s}extension" % XSD_NS) is not None:
            der_obj = xml_obj.find(u"{%s}extension" % XSD_NS)
            der_meth = EXTENSION
        else:
            raise XsdError("Simple Content in %s should contain either a "
                           "<restriction> or an <extension> child in the "
                           "%s XML Schema" % (node, self._xsd_file))
        type_nodes = self.get_type_nodes_from_xml(
            der_obj, u"base",
            uid_prefix=node.uid+u"/simpleContent/%s/%s" % (node.name, der_meth.lower()))
        if len(type_nodes) == 0:
            raise XsdError("%s in Simple Content in %s should contain either a"
                           "reference or an inner definition of type in %s XML"
                           "Schema" % (der_meth, node, self._xsd_file))
        node._base_type = type_nodes[0]
        node._deriv_method = der_meth
        self.add_attributes_to_node(node, der_obj)
        return node

    def fill_node_from_complex_content(self, node, xml_obj):
        """
        Fills the ``node`` object with the information found in the ``xml_obj``
        XML element read in an XML Schema.

        :param node:
            Complex type with complex content node that must be filled with
            the information available in ``xml_obj``.
        :param node:
            :class:`~pyxst.xml_struct.xsd.types.XsdComplexType`
        :param xml_obj:
            XML element defining a complex content in a complex type in the
            XML Schema (typically, ``xsd:complexContent``).
        :type xml_obj:
            :class:`~lxml.etree.Element`
        :returns:
            ``node`` after it has been filled.
        :rtype:
            :class:`~pyxst.xml_struct.xsd.types.XsdComplexType`
        """
        if xml_obj.get(u"mixed", u"false") == u"true":
            node.content_type = MIXED
        if xml_obj.find(u"{%s}restriction" % XSD_NS) is not None:
            der_obj = xml_obj.find(u"{%s}restriction" % XSD_NS)
            der_meth = RESTRICTION
        elif xml_obj.find(u"{%s}extension" % XSD_NS) is not None:
            der_obj = xml_obj.find(u"{%s}extension" % XSD_NS)
            der_meth = EXTENSION
        else:
            raise XsdError("Complex Content in %s should contain either a "
                           "<restriction> or an <extension> child in the "
                           "%s XML Schema" % (node, self._xsd_file))
        type_nodes = self.get_type_nodes_from_xml(
            der_obj, u"base",
            uid_prefix=node.uid+u"/complexContent/%s/%s" % (node.name, der_meth.lower()))
        if len(type_nodes) == 0:
            raise XsdError("%s in Complex Content in %s should contain either "
                           "a reference or an inner definition of type in %s "
                           "XML Schema" % (der_meth, node, self._xsd_file))
        node._base_type = type_nodes[0]
        node._deriv_method = der_meth
        grp_node = None
        for child_obj in der_obj:
            ns, child_sort = split_qname(child_obj.tag)
            if ns == XSD_NS and child_sort == u"group":
                grp_node = self.get_group_node_from_xml(child_obj,
                                                        uid_prefix=node.uid)
                break
            if ns == XSD_NS and child_sort in [u"all", u"choice", u"sequence"]:
                name = "%s/complexContent/%s" % (node.name, child_sort)
                grp_node = self.get_group_node_from_xml(child_obj, name,
                                                        uid_prefix=node.uid)
                break
        if grp_node is not None:
            min_occur, max_occur = self.get_min_max_occur_from_xml(child_obj,
                                                                   grp_node)
            node.sub_content = XsdUsage(grp_node, min_occur, max_occur)
        self.add_attributes_to_node(node, der_obj)
        return node

    def fill_group_node(self, node, xml_obj):
        """
        Fills the ``node`` object with the information found in the ``xml_obj``
        XML element read in an XML Schema.

        :param node:
            Group node that must be filled with the information
            available in ``xml_obj``.
        :param node:
            :class:`~pyxst.xml_struct.xsd.groups.XsdGroup`
        :param xml_obj:
            XML element defining a group in the XML Schema (typically,
            ``xsd:group``, ``xsd:all``, ``xsd:sequence``, ``xsd:choice``).
        :type xml_obj:
            :class:`~lxml.etree.Element`
        :returns:
            ``node`` after it has been filled.
        :rtype:
            :class:`~pyxst.xml_struct.xsd.groups.XsdGroup`
        """
        if xml_obj.tag == "{%s}group" % XSD_NS:
            # Finds the all, choice or sequence inside the group and uses it
            for child_obj in xml_obj:
                ns, child_sort = split_qname(child_obj.tag)
                if ns == XSD_NS and child_sort in [u"choice", u"all",
                                                   u"sequence"]:
                    xml_obj = child_obj
                    break
            else:
                return node
        grp_num = {u"all": 0, u"choice": 0, u"sequence": 0}
        for child_obj in xml_obj:
            ns, child_sort = split_qname(child_obj.tag)
            if ns == XSD_NS and child_sort == u"group":
                item_node = self.get_group_node_from_xml(child_obj,
                                                         uid_prefix=node.uid)
            elif ns == XSD_NS and child_sort in [u"all", u"choice",
                                                 u"sequence"]:
                name = u"%s/%s%d" % (node.name, child_sort, grp_num[child_sort])
                grp_num[child_sort] += 1
                item_node = self.get_group_node_from_xml(child_obj, name,
                                                         uid_prefix=node.uid)
            elif ns == XSD_NS and child_sort == u"element":
                item_node = self.get_element_node_from_xml(child_obj,
                                                           uid_prefix=node.uid)
            else:
                continue
            min_occur, max_occur = self.get_min_max_occur_from_xml(child_obj,
                                                                   item_node)
            node.add_item(item_node, min_occur, max_occur)
        return node
