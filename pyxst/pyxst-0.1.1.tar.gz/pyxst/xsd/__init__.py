# -*- coding: utf-8 -*-
"""
Sub-package containing the code that can read an XML Schema and return
an :class:`~pyxst.xml_struct.xsd.root.XsdSchema` object that
contains the nodes (elements, attributes, types, etc.) extracted from this
XML Schema.

External programs should just call the
:func:`~pyxst.xml_struct.xsd.read_schema` method defined
at the top level of this package.

The other modules of this package contain all the classes and
functions necessary to read the XML Schema:

:mod:`~pyxst.xml_struct.xsd.parser`
    Definition of the function that can parse an XML Schema and return a 
    ``XsdSchema`` object
:mod:`~pyxst.xml_struct.xsd.root`
    Definition of the ``XsdSchema`` object that contains all the information 
    read in an XML Schema and numerous functions to extract this information
:mod:`~pyxst.xml_struct.xsd.elements`
    Definition of the element node that represents an element definition read
    in an XML Schema
:mod:`~pyxst.xml_struct.xsd.attributes`
    Definition of the attribute node and the attribute group node that 
    represent the corresponding definitions read in an XML Schema
:mod:`~pyxst.xml_struct.xsd.types`
    Definition of the type nodes that represent the definition of types read
    in an XML Schema
:mod:`~pyxst.xml_struct.xsd.constraints`
    Definition of the constraints that can be applied to the type nodes and 
    that represent the corresponding constraints read in an XML Schema
:mod:`~pyxst.xml_struct.xsd.groups`
    Definition of the group nodes that represent the definition of groups read
    in an XML Schema (a group is set of sub-elements that can occur in a type,
    typically a sequence, a choice or an all).
:mod:`~pyxst.xml_struct.xsd.utils`
    Definition of the several useful classes and functions.
:mod:`~pyxst.xml_struct.xsd.errors`
    Definition of a dedicated exception.

.. autofunction:: read_schema
"""
__docformat__ = "restructuredtext en"


from .parser import parse_schema


def read_schema(xsd_file):
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
    :returns:
        An XsdSchema object grouping all the nodes read from the XML Schema.
    :rtype:
        :class:`~pyxst.xml_struct.xsd.root.XsdSchema`
    """
    return parse_schema(xsd_file)
