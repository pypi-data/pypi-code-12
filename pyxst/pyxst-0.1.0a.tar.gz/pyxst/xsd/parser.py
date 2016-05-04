# -*- coding: utf-8 -*-
"""
Module containing the parser function that can read an XML Schema file and
return an :class:`~pyxst.xml_struct.xsd.root.XsdSchema` object.

.. autofunction:: parse_schema
"""

from .errors import XsdError
from xml.parsers.expat import ExpatError
from traceback import format_exc
from os.path import abspath, dirname, join
from lxml.etree import parse
from .root import (XsdSchema, NODE_MAPPING, CAT_MAPPING)
from .types import XsdComplexType
from .utils import XSD_NS
from .utils import split_qname


def parse_schema(xsd_file, sch_obj=None, target_ns=None, 
                 ns_strict_equality=False):
    """
    Reads the ``xsd_file`` and returns an XsdSchema object containing
    the nodes (cf. nodes derived from
    :class:`~pyxst.xml_struct.xsd.utils.XsdNode`) read in
    the XML Schema.

    These nodes represent all the information read inside the XSD Schema
    (definition of XML elements and XML attributes, declaration of types,
    groups and attribute groups).

    :param xsd_file:
        Name of the file that contains the XML Schema.
    :type xsd_file:
        :class:`str`
    :param sch_obj:
        Schema object where the nodes read from the XML Schema will be stored.
        If no schema object is provided, a new one is created.
    :type sch_obj:
        :class:`~pyxst.xml_struct.xsd.root.XsdSchema`
    :param target_ns:
        Target namespace used to qualify the names of the nodes read in the
        XML Schema. If a namespace is specified in the XML Schema, it should
        be equal to the namespace specified in this parameter.
    :type target_ns:
        :class:`unicode`
    :param ns_strict_equality:
        If set to ``True``, the namespace specified in the XML Schema
        and the namespace specified in ``target_ns`` parameter must be
        strictly equals: either they are both ``None`` or they both
        have the same value. If set to ``False``, if the namespace
        specified in ``target_ns`` parameter is ``None``, it will be
        replaced by the namespace specified in the XML Schema (but if
        they both have a value, these values must be the same).
    :type ns_strict_equality:
        :class:`boolean`
    :returns:
        An XsdSchema object grouping all the nodes read from the XML Schema.
    :rtype:
        :class:`~pyxst.xml_struct.xsd.root.XsdSchema`
    """
    # Opens the XML Schema file
    try:
        xsd_file = abspath(xsd_file)
    except Exception:
        pass
    try:
        xml_tree = parse(xsd_file)
    except IOError, exc:
        raise XsdError("Can't open the %s XML Schema file\n%s" 
                       % (xsd_file, format_exc()))
    except ExpatError, exc:
        raise XsdError("Found a syntax error while reading the %s XML "
                       "Schema file\n%s" % (xsd_file, format_exc()))
    xml_root = xml_tree.getroot()
    if xml_root.tag != u"{%s}schema" % XSD_NS:
        raise XsdError("%s XML file doesn't contain an XML Schema" 
                       % xsd_file)
    if sch_obj is None:
        sch_obj = XsdSchema()
        sch_obj.loaded_files = set([xsd_file])
    else:
        sch_obj.loaded_files.add(xsd_file)
    # Checks target namespace
    if not ns_strict_equality:
        if target_ns is None:
            target_ns = xml_root.get(u"targetNamespace")
        elif xml_root.get(u"targetNamespace") is not None and \
                target_ns != xml_root.get(u"targetNamespace"):
            raise XsdError("Target namespace of %s should be %s instead of %s"
                           % (xsd_file, target_ns, 
                              xml_root.get(u"targetNamespace")))
    elif target_ns != xml_root.get(u"targetNamespace"):
        raise XsdError("Target namespace of %s should be %s instead of %s"
                       % (xsd_file, target_ns, 
                          xml_root.get(u"targetNamespace")))
    # Processes inclusions or imports of external XML Schemas
    for xml_obj in xml_root.findall(u"{%s}include" % XSD_NS):
        ext_file = xml_obj.get(u"schemaLocation")
        ext_file = abspath(join(dirname(xsd_file), ext_file))
        if not ext_file in sch_obj.loaded_files:
            parse_schema(ext_file, sch_obj, target_ns)
    for xml_obj in xml_root.findall(u"{%s}import" % XSD_NS):
        ext_file = xml_obj.get(u"schemaLocation")
        ext_file = abspath(join(dirname(xsd_file), ext_file))
        if not ext_file in sch_obj.loaded_files:
            ext_ns = xml_obj.get(u"namespace")
            parse_schema(ext_file, sch_obj, ext_ns, ns_strict_equality=True)
    # Processes redefinitions from external XML Schemas
    for xml_obj in xml_root.findall(u"{%s}redefine" % XSD_NS):
        ext_file = xml_obj.get(u"schemaLocation")
        ext_file = join(dirname(xsd_file), ext_file)
        raise XsdError("<redefine> objects are not yet supported "
                       "(%s XML Schema)" % xsd_file)
    # Sets global properties in the schema object
    sch_obj._xsd_file = xsd_file
    sch_obj._target_ns = target_ns
    sch_obj._qualified_elts = (xml_root.get(u"elementFormDefault") == 
                               u"qualified")
    sch_obj._qualified_attrs = (xml_root.get(u"attributeFormDefault") == 
                                u"qualified")
    # Firstly, creates the high level nodes defined in the XML Schema
    for xml_obj in xml_root:
        ns, obj_sort = split_qname(xml_obj.tag)
        if ns == XSD_NS and obj_sort in CAT_MAPPING:
            node = sch_obj.create_node(xml_obj)
            sch_obj.store_definition_node(node)
    # Then, fills the nodes with the information defined in the XML Schema
    # (starts with high level nodes and goes down in hierarchy)
    filling_function = {u"element"       : sch_obj.fill_element_node,
                        u"attributeGroup": sch_obj.fill_attribute_group_node,
                        u"attribute"     : sch_obj.fill_attribute_node,
                        u"complexType"   : sch_obj.fill_complex_type_node,
                        u"simpleType"    : sch_obj.fill_simple_type_node,
                        u"group"         : sch_obj.fill_group_node,
                        u"all"           : sch_obj.fill_group_node,
                        u"choice"        : sch_obj.fill_group_node,
                        u"sequence"      : sch_obj.fill_group_node,
                        }
    for xml_obj in xml_root:
        ns, obj_sort = split_qname(xml_obj.tag)
        if ns == XSD_NS and obj_sort in CAT_MAPPING:
            name = sch_obj.get_node_name(xml_obj)
            node = sch_obj.get_definition_node(CAT_MAPPING[obj_sort], name)
            filling_function[obj_sort](node, xml_obj)
    # Resolves the attribute groups and the derivation in the types
    for typ in sch_obj.all_types:
        typ.resolve_derivation()
        if isinstance(typ, XsdComplexType):
            typ.resolve_attribute_groups()
    # Unsets the global properties from the schema object as reading is finished
    sch_obj._xsd_file = ""
    sch_obj._target_ns = None
    sch_obj._qualified_elts = False
    sch_obj._qualified_attrs = False
    return sch_obj
