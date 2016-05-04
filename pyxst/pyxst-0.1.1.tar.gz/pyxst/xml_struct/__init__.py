# -*- coding: utf-8 -*-
"""This package contains classes and functions that
produce a graph representing the XML structure described in the schema.

The :mod:`~xml_struct.graph` defines the items used to build the
actual structure that will be returned by this package. This structure
is a graph describing the structure of the XML documents (XML elements
that contain XML attributes and XML sub-elements).

The function defined in this module can read a
schema and return a grah describing the XML structure.

.. autofunction:: build_xml_structure_from_schema

"""
__docformat__ = "restructuredtext en"

from ..xsd import read_schema
from ..dtd import read_dtd
from .utils import DTD, XML_SCHEMA
from .graph import XMLGraph
from .graph_target_relations import weave_target_relations


def build_xml_structure_from_schema(xsd_file, type_mapper=None):
    """
    Reads the ``xsd_file``, parses the XML Schema and builds a graph describing
    the structure of the XML data.

    The graph is an :class:`~xml_struct.graph.XMLGraph` that contains
    nodes describing the various elements, their attributes and their
    inner content (textual data or structure of sub-elements).

    :param xsd_file:
        Name of the file that contains the XML Schema.
    :type xsd_file:
        :class:`str`
    :returns:
        A graph describing the structure of the XML data.
    :rtype:
        :class:`~xml_struct.graph.XMLGraph`
    """
    try:
        name = splitext(split(xsd_file)[1])[0]
    except Exception:
        name = "anonymous"
    schema = read_schema(xsd_file)
    graph = XMLGraph(name, xsd_file, XML_SCHEMA, type_mapper)
    graph.build_from_schema(schema)
    weave_target_relations(graph)
    return graph


def build_xml_structure_from_dtd(dtd_file, ns_mapping=None,
                                 qualify_local_elements=False,
                                 qualify_local_attributes=False):
    """
    Reads the ``dtd_file``, parses the DTD and builds a graph describing
    the structure of the XML data.

    The graph is an :class:`~xml_struct.graph.XMLGraph` that contains
    nodes describing the various elements, their attributes and their
    inner content (textual data or structure of sub-elements).

    The DTD doesn't support namespaces. The elements and attributes have to
    be declared with their prefix (e.g. ``xlink:href``). The ``ns_mapping``
    parameter allows the building of qualified names (namespace plus local
    name) from the DTD declaration.

    :param dtd_file:
        Name of the file that contains the DTD.
    :type dtd_file:
        :class:`unicode`
    :param ns_mapping:
        Mapping of prefixes towards namespaces ``{prefix: namespace}``. It is
        possible to give a default namespace by associating a namespace with
        ``u""`` or ``None``.
    :type ns_mapping:
        dict {:class:`unicode`: :class:`unicode`}
    :param qualify_local_elements:
        Flag indicating that the elements without a prefix must be qualified
        with the default namespace given in ``ns_mapping`` (namespace
        indexed with ``u""``).
    :type qualify_local_elements:
        :class:`bool`
    :param qualify_local_attributes:
        Flag indicating that the attributes without a prefix must be qualified
        with the default namespace given in ``ns_mapping`` (namespace
        indexed with ``u""``).
    :type qualify_local_attributes:
        :class:`bool`
    :returns:
        A graph describing the structure of the XML data.
    :rtype:
        :class:`~pyxst.xml_struct.graph.XMLGraph`
    """
    try:
        name = splitext(split(dtd_file)[1])[0]
    except Exception:
        name = "anonymous"
    dtd_def = read_dtd(dtd_file, ns_mapping, qualify_local_elements,
                       qualify_local_attributes)
    graph = XMLGraph(name, dtd_file, DTD)
    graph.dtd_ns_mapping = ns_mapping or {}
    graph.dtd_qualif_local_elt = qualify_local_elements
    graph.dtd_qualif_local_attr = qualify_local_attributes
    graph.build_from_dtd(dtd_def)
    weave_target_relations(graph)
    return graph
