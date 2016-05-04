# -*- coding: utf-8 -*-
"""
This module defines the constants and classes used to represent the nodes
read in an XML Schema.

Constants
.........

.. autodata:: ATTRIBUTE

.. autodata:: ATTRIBUTE_GROUP

.. autodata:: ELEMENT

.. autodata:: GROUP

.. autodata:: TYPE

.. autodata:: XSD_NS

Nodes
.....

.. autoclass:: XsdNode
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: XsdUsage
   :members:
   :undoc-members:
   :show-inheritance:
"""
__docformat__ = "restructuredtext en"


from .errors import XsdError


ATTRIBUTE = "Attribute"
"""
Constant containing the category of the attribute nodes

Type: :class:`str`
"""

ATTRIBUTE_GROUP = "Attribute Group"
"""
Constant containing the category of the attribute group nodes

Type: :class:`str`
"""

ELEMENT = "Element"
"""
Constant containing the category of the element nodes

Type: :class:`str`
"""

TYPE = "Type"
"""
Constant containing the category of the type nodes

Type: :class:`str`
"""

GROUP = "Group"
"""
Constant containing the category of the group nodes

Type: :class:`str`
"""

INFINITY = "infinity"
"""
Constant describing the infinity (for unbounded occurences).

Type: :class:`str`
"""

MIXED = "Mixed Content"
"""
Constant describing the type of the content that can occur inside an element
if this element can contain, at the same time, sub-elements and textual data.

Type: :class:`str`
"""

XSD_NS = u"http://www.w3.org/2001/XMLSchema"
"""
XSD namespace as defined in the XML Schema standard.

Type: :class:`unicode`
"""


def split_qname(qname):
    """
    Splits the XML qualified name in a tuple containing the namespace and the
    local name.

    A qualified name is composed with the namespace and the local name.
    In the XML nodes read with :mod:`xml.etree` module, the qualified name
    is built as follow: ``{namespace}local-name``.

    :param qname:
        XML qualified name as built by the :mod:`xml.etree` module.
    :type qname:
        :class:`unicode`
    :returns:
        The namespace and the local name extracted from ``qname``
    :rtype:
        tuple composed with :class:`unicode` and :class:`unicode`
    """
    if qname is None:
        return None, None
    name = str(qname)
    if name.find('}') == -1:
        return None, name
    return name[name.find('{')+1:name.find('}')], name[name.find('}')+1:]


def resolve_xml_qname(qname, ns_decl):
    """
    Resolves the XML qualified name and returns this qualified name as if it
    was read by the :mod:`xml.etree` module.

    A qualified name is composed with the namespace and the local name.
    In the XML document, the qualified name is built as follow:
    ``prefix:local-name`` and namespace declarations map the prefixes with
    the actual namespaces.

    :param qname:
        XML qualified name as read in the XML document.
    :type qname:
        :class:`unicode`
    :param ns_decl:
        Mapping between the prefixes used in the XML document and the
        namespaces.
    :type ns_decl:
        Dictionary of :class:`unicode` indexed with :class:`unicode`.
    :returns:
        The qualified name structured as built by the :mod:`xml.etree`
        module (``{namespace}local-name``)
    :rtype:
        :class:`unicode`
    """
    if qname is None:
        return None
    name = str(qname)
    if name.find(':') == -1:
        prefix = ""
        local_name = name
    else:
        prefix = name[:name.find(':')]
        local_name = name[name.find(':')+1:]
    if prefix == "" and "" in ns_decl:
        namespace = ns_decl[u""]
    elif prefix == "" and None in ns_decl:
        namespace = ns_decl[None]
    elif prefix == "":
        return local_name
    elif prefix == u"xml":
        namespace = "http://www.w3.org/XML/1998/namespace"
    else:
        try:
            namespace = ns_decl[prefix]
        except KeyError, exc:
            raise Exception("%s prefix is not bound to a namespace" % prefix)
    return "{%s}%s" % (namespace, local_name)

class XsdNode(object):
    """
    Base class representing any node in an XML Schema.

    .. attribute:: category

       Class attribute representing the category of the node (element,
       attribute, type, group, etc.)

       Type: :class:`str`

    .. attribute:: name

       Name of the node. If the node in the XML Schema doesn't have an
       explicit name, an implicit name is created while parsing the schema.

       Type: :class:`unicode`

    .. attribute:: uid

       Unique identifier of the node in its category.

       Type: :class:`unicode`

    .. automethod:: __init__
    """
    category = ""

    def __init__(self, name, uid_prefix=u""):
        """
        Initializes a new node.

        :param name:
            Name of the node.
        :type name:
            :class:`unicode`
        """
        self.name = name
        self.uid_prefix = uid_prefix
        if self.__class__ is XsdNode:
            raise NotImplementedError("Can't instanciate abstract class")

    @property
    def uid(self):
        return u"{0}/{1}".format(self.uid_prefix, self.name)

    def __repr__(self):
        """
        Returns a string representation of the node.
        """
        return u"<{0} {1}>".format(self.category, self.name)


class XsdUsage(XsdNode):
    """
    Class representing in an XML Schema the usage of another node.

    Usages are typically inserted inside a group in a complex element to
    point sub-elements or sub-groups and indicate the minimum and maximum
    occurences (e.g. ``<xsd:element ref="sub-elt" minOccurs="0"/>``).

    If a sub-element (an attribute or a sub-group) is directly defined
    (```<xsd:element name="sub-elt" maxOccurs="4"/>``), a usage is
    nevertheless inserted between the group and the sub-element to
    indicate the minimum and maximum occurences of this sub-element.

    .. attribute:: category

       Category (element, attribute, group) of the referenced node.

       Type: :class:`str`

    .. attribute:: min_occur

       Minimum occurence of the referenced node in the context where the usage
       is inserted.

       Type: :class:`int`

    .. attribute:: max_occur

       Maximum occurence of the referenced node in the context where the usage
       is inserted.

       Type: :class:`int`

    .. attribute:: referenced_node

       Node referenced by this usage.

       Type: :class:`~pyxst.xml_struct.xsd.utils.XsdNode`

    .. automethod:: __init__
    """
    def __init__(self, ref_node, min_occur=1, max_occur=1):
        """
        Initializes a new usage for ``ref_node``.

        :param ref_node:
            Referenced node used by this usage.
        :type ref_node:
            :class:`~pyxst.xml_struct.xsd.elements.XsdElement` or
            :class:`~pyxst.xml_struct.xsd.attributes.nodes.XsdAttribute`
            or :class:`~pyxst.xml_struct.xsd.groups.XsdGroup`
        :param min_occur:
            Minimum occurence for the referenced node in the
            context of this usage.
        :type min_occur:
            :class:`int`
        :param max_occur:
            Maximum occurence for the referenced node in the
            context of this usage.
        :type max_occur:
            :class:`int` or
            :data:`~pyxst.xml_struct.utils.INFINITY`
        """
        if ref_node.category not in [ATTRIBUTE, ELEMENT, GROUP]:
            raise XsdError("%s cannot be referenced in group or complex type "
                           "(only attributes, elements or groups can)"
                           % ref_node)
        if min_occur < 0:
            raise XsdError("Minimum occurence for %s must be positive or null"
                           % ref_node)
        if not max_occur is INFINITY and max_occur < min_occur:
            raise XsdError("Maximum occurence for %s must be greater than "
                           "minimum occurence" % ref_node)
        super(XsdUsage, self).__init__(ref_node.name)
        self.min_occur = min_occur
        self.max_occur = max_occur
        self.referenced_node = ref_node

    @property
    def category(self):
        return self.referenced_node.category

    @property
    def uid(self):
        return self.referenced_node.uid

    def __repr__(self):
        return ("<Usage (%s,%s) of %s %s>"
                % (self.min_occur, self.max_occur, self.category, self.name))
