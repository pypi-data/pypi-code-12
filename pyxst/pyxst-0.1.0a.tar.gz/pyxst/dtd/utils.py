# -*- coding: utf-8 -*-


from .errors import DtdError
from .constants import INFINITY, ATTRIBUTE, ELEMENT, GROUP


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


class DtdNode(object):
    """
    Base class representing any node in a DTD.

    .. attribute:: category

       Class attribute representing the category of the node (element,
       attribute, type, group, etc.)

       Type: :class:`unicode`

    .. attribute:: name

       Name of the node. If the node in the DTD doesn't have an
       explicit name, an implicit name is created while parsing the DTD.

       Type: :class:`unicode`

    .. attribute:: uid

       Unique identifier of the node in its category.

       Type: :class:`unicode`
    """
    category = u""

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
        if self.__class__ is DtdNode:
            raise NotImplementedError("Can't instanciate abstract class")

    @property
    def uid(self):
        return u"{0}/{1}".format(self.uid_prefix, self.name)

    def __repr__(self):
        """
        Returns a string representation of the node.
        """
        return u"<{0} {1}>".format(self.category, self.name)


class DtdUsage(DtdNode):
    """
    Class representing in a DTD the usage of another node

    Usages are typically inserted inside a group in the sub-content of an
    element to point sub-elements or sub-groups and indicate the minimum and
    maximum occurences (e.g. ``(sub-elt)+``).

    .. attribute:: category

       Category (element, attribute, group) of the referenced node.

       Type: :class:`unicode`

    .. attribute:: min_occur

       Minimum occurence of the referenced node in the context where the usage
       is inserted.

       Type: :class:`int`

    .. attribute:: max_occur

       Maximum occurence of the referenced node in the context where the usage
       is inserted. Can be ``INFINITE``.

       Type: :class:`int`

    .. attribute:: referenced_node

       Node referenced by this usage.

       Type: :class:`~dtd.utils.DtdNode`

    .. automethod:: __init__
    """
    def __init__(self, ref_node, min_occur=1, max_occur=1):
        """
        Initializes a new usage for ``ref_node``.
        """
        if ref_node.category not in [ATTRIBUTE, ELEMENT, GROUP]:
            raise DtdError("%s cannot be referenced in group or complex type "
                           "(only attributes, elements or groups can)"
                           % ref_node)
        if min_occur < 0:
            raise XsdError("Minimum occurence for %s must be positive or null"
                           % ref_node)
        if not max_occur is INFINITY and max_occur < min_occur:
            raise XsdError("Maximum occurence for %s must be greater than "
                           "minimum occurence" % ref_node)
        super(DtdUsage, self).__init__(ref_node.name)
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
