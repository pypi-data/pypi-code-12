# -*- coding: utf-8 -*-
"""
This module defines the classes used to build the graph of the actual
structure that describes the XML documents.

These classes are the nodes that compose the graph defined with :class:`~pyxst.xml_struct.graph.XMLGraph` that will be returned by :mod:`~pyxst.xml_struct` module.

These nodes are mainly XML elements and XML attributes that are
connected with links that give the minimum and maximum numbers of
occurence of the child nodes inside their parent node.

The structure created with these nodes is simpler than the
structure read in the XML Schemas with the
:mod:`pyxst.xml_struct.xsd` module.

Utilitary classes
.................

.. autoclass:: XMLNode
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: Occurence
   :members:
   :undoc-members:
   :show-inheritance:

Groups of child nodes
.....................

.. autoclass:: Group
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: Sequence
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: Alternative
   :members:
   :undoc-members:
   :show-inheritance:

Actual XML nodes
................

.. autoclass:: XMLElement
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: XMLAttribute
   :members:
   :undoc-members:
   :show-inheritance:
"""
__docformat__ = "restructuredtext en"


import operator
from .utils import (split_qname, INFINITY, EMPTY, ELEMENTS_ONLY,
                              TEXT_ONLY, MIXED, UNKNOWN, ANY)


class XMLNode(object):
    """
    Abstract class that represents an XML node, ie either an element or an
    attribute.

    This class defines common attributes.

    .. attribute:: local_name

       Local name of the XML node (name without namespace). The
       namespace and the local name compose the qualified name.

       Type: :class:`unicode`

    .. attribute:: namespace

       Namespace of the XML node. The namespace and the local name compose the
       qualified name.

       Type: :class:`unicode`

    .. attribute:: parent_elts

       List of XML elements that can be parents of this XML node.

       The attributes have a single parent. The local elements also have
       a single parent. The high level elements can occur in several elements
       and therefore can have several possible parents.

       The order in the list of parents is not relevant.

       Type: list of :class:`~pyxst.xml_struct.graph_nodes.XMLElement`

    .. attribute:: textual_content_type

       Type of the textual content that can be found in this element. The
       types are basic types such as integer, float, date, datetime, duration,
       string.

       If the XML node is an element that have mixed content ie a content that
       mixes child elements and textual data, this type is set to ``MIXED``.

       If the XML node is an empty element or has only elements, this type is
       set to ``None``.

       Type: :class:`str`

    .. attribute:: textual_content_is_list

       Flag set to true if the textual content is a space-separated list of
       items whose type is given by ``textual_content_type`` attribute.

       Type: :class:`bool`

    .. attribute:: textual_content_values

       Set containing the possible values for the textual content
       (when this content is contrained). If this attribute contains ``None``,
       the value of the textual content is free.

       Type: :class:`set` of :class:`unicode`

    .. automethod:: __init__
    """
    parent = None

    def __init__(self, qname):
        """
        Initializes a new XML node.

        :param qname:
            Qualified name of the XML node (namespace + local name). The
            qualified name is expected to be in the ``{namespace}local-name``
            form.
        :type qname:
            :class:`unicode`
        """
        namespace, local_name = split_qname(qname)
        self.local_name = local_name
        self.namespace = namespace
        self.parent_elts = []
        self.textual_content_type = None
        self.textual_content_is_list = False
        self.textual_content_values = None
        if self.__class__ is XMLNode:
            raise NotImplementedError("Can't instantiate abstract classes")

    @property
    def qname(self):
        """
        Gives the qualified name of the XML node.

        :returns:
            The qualified name of the XML node in the
            ``{namespace}local-name`` form.
        :rtype:
            :class:`unicode`
        """
        if self.namespace is None:
            return self.local_name
        else:
            return "{%s}%s" % (self.namespace, self.local_name)

    def add_parent_elt(self, parent):
        """
        Adds a parent element for this node.

        **Abstract method that will be defined in derived classes.**

        :param parent:
            Parent element of this node (element that contains the node).
        :type parent:
            :class:`~pyxst.xml_struct.graph_nodes.XMLElement`
        """
        raise NotImplementedError("Can't call abstract mathod")

    def __repr__(self):
        return u"Node <{0}>".format(self.qname)

class Occurence(object):
    """
    Class that describes a link between a parent node and its child node.

    This class gives the minimum and maximum occurence of the child node
    inside its parent node. It will appear in the attributes list of
    an element or in the children list of a group.

    .. attribute:: target

       Child node.

       Type: :class:`~pyxst.xml_struct.graph_nodes.XMLNode`

    .. attribute:: minimum

       Minimum occurence of the child node inside its parent node.

       Type: :class:`int`

    .. attribute:: maximum

       Maximum occurence of the child node inside its parent node.

       Can be ``INFINITY`` if there is no maximum.

       Type: :class:`int` or
       :data:`~pyxst.xml_struct.utils.INFINITY`

    .. automethod:: __init__
    """

    def __init__(self, target, min_occur, max_occur):
        """
        Initializes a new occurence.

        :param target:
            Child node that this occurence points to.
        :type target:
            :class:`~pyxst.xml_struct.graph_nodes.XMLNode`
        :param min_occur:
            Minimum occurence of the child node inside its parent.
        :type min_occur:
            :class:`int`
        :param max_occur:
            Maximum occurence of the child node inside its parent. Can be
            ``INFINITY``
        :type max_occur:
            :class:`int` or
            :data:`~pyxst.xml_struct.utils.INFINITY`
        """
        self.target = target
        target.parent = self
        self.minimum = min_occur
        self.maximum = max_occur

    @property
    def qname(self):
        return self.target.qname

    def add_parent_elt(self, parent):
        """
        Adds a parent element on the child referenced by this occurence object.

        :param parent:
            Parent element to be added to the child pointed by this occurence
        :type parent:
            :class:`~pyxst.xml_struct.graph_nodes.XMLElement`
        """
        self.target.add_parent_elt(parent)

    def simplify(self):
        return self.target.simplify(self.minimum, self.maximum)

    def __eq__(self, other):
        if not isinstance(other, Occurence):
            return NotImplemented
        if isinstance(self.target, XMLElement):
            if not isinstance(other.target, XMLElement):
                return False
            return (self.target.qname == other.target.qname
                    and self.minimum == other.minimum
                    and self.maximum == other.maximum)
        if isinstance(self.target, Group):
            if self.target.__class__ != other.target.__class__:
                return False
            return (self.minimum == other.minimum
                    and self.maximum == other.maximum)
        return (self.target == other.target
                and self.minimum == other.minimum
                and self.maximum == other.maximum)

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        if self.minimum == self.maximum:
            occurs = u"[{0}]".format(self.minimum)
        else:
            occurs = u"[{0},{1}]".format(self.minimum, self.maximum)
        return u"{0} {1}".format(self.target, occurs)


class Group(object):
    """
    Class describing a group of XML elements that are children of a parent
    element. This group is a non-ordered group (the child elements can occur
    in any order).

    A group can directly contain child elements or can contain other groups
    that contain child elements.

    .. attribute:: children

       Child elements or groups that occur inside this group. Whereas this
       attribute is a list, the order of the child elements is not constrained.
       This attribute contains ``Occurence`` instances that links towards the
       actual child (that can be an element or another group) and keeps its
       minimum occurence and its maximum occurence.

       Type: list of
       :class:`~pyxst.xml_struct.graph_nodes.Occurence`

    .. attribute:: parent_elt

       Parent element that contains this group.

       If this group is a sub-group that is contained in another group, the
       parent element is the parent element of the highest level group.

       A group is always dedicated to a single element and therefore has
       a single parent element.

       Type: :class:`~pyxst.xml_struct.graph_nodes.XMLElement`

    .. automethod:: __init__

    .. automethod:: __len__

    .. automethod:: __getitem__
    """
    def __init__(self, parent=None):
        """
        Initializes a new group.If this group is
            contained in another group, the parent element is the parent
            element of the highest level group.

        :param parent:
            Parent element that contains this group.
        :type parent:
            :class:`~pyxst.xml_struct.graph_nodes.XMLElement`
        """
        self.children = []
        self.parent_elt = parent

    def __len__(self):
        """
        Returns the length of the group ie the number of children.

        :returns:
            The number of children.
        :rtype:
            :class:`int`
        """
        return len(self.children)

    def __getitem__(self, idx):
        """
        Returns a tuple containing the occurence of the child in position
        number ``idx``.

        Even if the group is not ordered, it is possible to iterate over the
        children.

        :param idx:
            Index of the child to be returned.
        :param idx:
            :class:`int`
        :returns:
            The child in idx-th position and its minimum and maximum occurences
        :rtype: :class:`~pyxst.xml_struct.graph_nodes.Occurence
        """
        return self.children[idx]

    def add_child(self, child, min_occur=1, max_occur=1):
        """
        Adds a new child in this group.

        If the group is ordered, the child is appended after the existing
        children. This method automatically creates an ``Occurence`` instance
        to keep the minimum and maximum occurence inside the link towards the
        child.

        :param child:
            Child to be appended in the group.
        :type child:
            :class:`~pyxst.xml_struct.graph_nodes.XMLElement` or
            :class:`~pyxst.xml_struct.graph_nodes.Group`
        :param min_occur:
            Minimum occurence of the child inside this group.
        :type min_occur:
            :class:`int`
        :param max_occur:
            Maximum occurence of the child inside this group.
        :type max_occur:
            :class:`int`
        """
        self.children.append(Occurence(child, min_occur, max_occur))
        if self.parent_elt is not None:
            child.add_parent_elt(self.parent_elt)

    def add_parent_elt(self, parent):
        """
        Adds a parent element for this group and for all its children.

        :param parent:
            Parent element to be added to this group and all its children.
        :type parent:
            :class:`~pyxst.xml_struct.graph_nodes.XMLElement`
        """
        if self.parent_elt is not None and self.parent_elt != parent:
            raise Exception("Groups can't have two different parents")
        self.parent_elt = parent
        for child in self.children:
            child.add_parent_elt(parent)

    def simplify(self, min_occur=None, max_occur=None):
        """
        Simplifies the group and its sub-groups (if any).

        Before working on this group, this method recursively calls
        the ``simplify`` method of the sub-groups.

        If a child (element or sub-group) has a maximum occurence
        equaled to ``0``, this method deletes it.

        If a sub-group is empty, this method deletes it.

        If a sub-group has only one child, directly adds the child
        inside this group.

        If a sub-group has the same sort as this group (same class)
        and the maximum occurence of this sub-group is ``1`` and the
        minimum occurence of the children of this sub-group is never
        more than``1``, this method merges this sub-group into this
        group.
        """
        change = False
        for occur in self.children[:]:
            child = occur.target
            child_min = occur.minimum
            child_max = occur.maximum
            if child_max == 0:
                self.children.remove(occur)
                change = True
            elif isinstance(child, Group):
                change |= occur.simplify()
                if len(child) == 0:
                    self.children.remove(occur)
                    change = True
                elif len(child) == 1:
                    occ = child.children.pop()
                    occ.minimum = child_min * occ.minimum
                    if child_max == INFINITY or occ.maximum == INFINITY:
                        occ.maximum = INFINITY
                    else:
                        occ.maximum = child_max * occ.maximum
                    idx = self.children.index(occur) + 1
                    self.children.insert(idx, occ)
                    self.children.remove(occur)
                    change = True
                elif child.__class__ is self.__class__ and child_max == 1:
                    can_simplify = True
                    for occ in child:
                        sub_min = occ.minimum
                        can_simplify &= (sub_min <= 1)
                    if can_simplify:
                        idx = self.children.index(occur) + 1
                        for i in range(len(child.children)):
                            occ = child.children.pop()
                            occ.minimum *= child_min
                            self.children.insert(idx, occ)
                        self.children.remove(occur)
                        change = True
        return change

    def sort(self):
        """
        Sorts the group children and recursively calls the sort method of
        the sub-groups.
        """
        sub_groups = []
        sub_elts = []
        for occur in self.children:
            if isinstance(occur.target, Group):
                occur.target.sort()
                sub_groups.append(occur)
            else:
                sub_elts.append(occur)
        sub_elts.sort(key=operator.attrgetter("qname"))
        self.children = sub_elts + sub_groups

    def list_sub_elts(self, recursive):
        """
        Returns a list with all the XML elements that appear in this group
        and its sub-groups (if recursive is True).
        """
        result = []
        for occur in self.children:
            if isinstance(occur.target, XMLElement):
                result.append(occur.target)
            elif recursive and isinstance(occur.target, Group):
                result.extend(occur.target.list_sub_elts(recursive))
        return result

    def __repr__(self):
        results = []
        for occ in self.children:
            results.append(u"{0}".format(occ))
        return u"Group({0})".format(u", ".join(results))


class Sequence(Group):
    """
    Class describing an ordered group of children. The children can be either
    elements or sub-groups.

    .. automethod:: __init__
    """
    def __init__(self, parent=None):
        """
        Initializes a new ordered group.
        """
        super(Sequence, self).__init__(parent)

    def sort(self):
        """
        Doesn't sort the group children but recursively calls the sort
        method on the sub-groups.
        """
        for occur in self.children:
            if isinstance(occur.target, Group):
                occur.target.sort()

    def __repr__(self):
        results = []
        for occ in self.children:
            results.append(u"{0}".format(occ))
        return u"Sequence({0})".format(u", ".join(results))

class Alternative(Group):
    """
    Class describing an alternative between several children. In the actual
    XML document, only one of the possible child will occur.

    The children can be either elements or sub-groups.

    .. automethod:: __init__
    """
    def __init__(self, parent=None):
        """
        Initializes a new alternative group.
        """
        super(Alternative, self).__init__(parent)

    def simplify(self, min_occur=None, max_occur=None):
        """
        Simplifies the alternative and its sub-groups (if any).

        First, calls the ``simplify`` method on the base class.

        If the maximum occurrence of this alternative (``max_occur``) is
        INFINITY, the maximum occurence of its children can be the same
        as their minimum occurence (1 if their minimum is 0).

        If the minimum occurrence of this alternative (``min_occur``) is
        0, the minimum occurence of its children can be 1 instead of 0.
        """
        change = super(Alternative, self).simplify(min_occur, max_occur)
        if max_occur == INFINITY:
            for occ in self.children:
                if occ.maximum == INFINITY or occ.maximum > occ.minimum:
                    if occ.minimum == 0:
                        occ.maximum = 1
                    else:
                        occ.maximum = occ.minimum
                    change = True
        if min_occur == 0:
            for occ in self.children:
                if occ.minimum == 0:
                    occ.minimum = 1
                    change = True
        return change

    def __repr__(self):
        results = []
        for occ in self.children:
            results.append(u"{0}".format(occ))
        return u"Alternative({0})".format(u" | ".join(results))

class XMLElement(XMLNode):
    """
    Class defining an XML element.

    .. attribute:: is_high_level

       Flag set to true if the element is a high level element.

       High level elements are elements that might be the root element
       of the XML document. When the XML structure is read from an XML
       Schema, all the elements defined at the top level of the schema
       are high level elements. When the XML structure is read from a
       DTD, all the elements are high level elements.

       Type: :class:`bool`

    .. attribute:: content

       Occurence towards the group that contains the child elements of this
       element.

       This content can be ``None`` if this element is empty.

       Type: :class:`~pyxst.xml_struct.graph_nodes.Occurence`

    .. attribute:: attributes

       Dictionary grouping the occurences towards the attributes of
       this element. The attributes are indexed with their qualified
       names.

       Type: dictionary of
       :class:`~pyxst.xml_struct.graph_nodes.Occurence` indexed
       with :class:`unicode`.

    .. automethod:: __init__
    """
    def __init__(self, qname, is_high_level=False):
        """
        Initializes a new XML element.

        :param qname:
            Qualified name of the XML node (namespace + local
            name). The qualified name is expected to be in the
            ``{namespace}local-name`` form.
        :type qname:
            :class:`unicode`
        :param is_high_level:
            Flag indicating if the element is a high level element.
        :type is_high_level:
            :class:`bool`
        """
        super(XMLElement, self).__init__(qname)
        self.is_high_level = is_high_level
        self.content_type = UNKNOWN
        self.content = None
        self.attributes = {}
        # The two following attributes are used for analyzing a library of XML
        # documents whose structure is given by the graph. They are used to
        # count the number of times an attribute or a sub-element is actually
        # used in all the XML documents of the library.
        # (Some elements or attributes might never be used in the documents)
        self.actual_uses = {} # {xml_filename: uses_count,}
        self.attr_uses = {} # {XMLAttribute: {xml_filename: uses_count,}}
        self.sub_elt_uses = {} # {XMLElement: {xml_filename: uses_count,}}

    def get(self, attr_qname):
        """
        Returns a tuple containing the attribute named ``attr_qname``,
        its minimum occurence and its maximum occurence.

        :param attr_qname:
            Qualified name of the attribute to be returned.
        :param idx:
            :class:`unicode`
        :returns:
            The attribute whose name is ``attr_qname`` and its minimum and
            maximum occurences
        :rtype:
            Tuple composed with
            :class:`~pyxst.xml_struct.graph_nodes.XMLAttribute`,
            :class:`int`, :class:`int`
        """
        occ = self.attributes[attr_qname]
        return occ.target, occ.minimum, occ.maximum

    def iter_attrs(self):
        return sorted(self.attributes.values(),
                      key=operator.attrgetter("qname"))

    def add_attribute(self, attr, min_occur=1, max_occur=1):
        """
        Adds a new attribute in this element.

        This method automatically creates an ``Occurence`` instance to
        keep the minimum and maximum occurence inside the link towards
        the attribute.

        :param attr:
            Attribute to be added in the element.
        :type attr:
            :class:`~pyxst.xml_struct.graph_nodes.XMLAttribute`
        :param min_occur:
            Minimum occurence of the attribute inside this element (0 or 1).
        :type min_occur:
            :class:`int`
        :param max_occur:
            Maximum occurence of the attribute inside this element (1).
        :type max_occur:
            :class:`int`
        """
        self.attributes[attr.qname] = \
            Occurence(attr, min_occur, max_occur)
        attr.add_parent_elt(self)

    def set_content(self, group, min_occur=1, max_occur=1):
        """
        Sets ``group`` as the content that describes the child elements of this
        element.

        :param group:
            Group that describes the child elements that can occur inside this
            element.
        :type group:
            :class:`~pyxst.xml_struct.graph_nodes.Group`
        :param min_occur:
            Minimum occurence of the attribute inside this element (0 or 1).
        :type min_occur:
            :class:`int`
        :param max_occur:
            Maximum occurence of the attribute inside this element (1).
        :type max_occur:
            :class:`int`
        """
        self.content = Occurence(group, min_occur, max_occur)
        group.add_parent_elt(self)

    def add_parent_elt(self, parent):
        """
        Adds a parent element for this element.

        :param parent:
            Parent element of this element (element that can contain this
            element).
        :type parent:
            :class:`~pyxst.xml_struct.graph_nodes.XMLElement`
        """
        if parent not in self.parent_elts:
            self.parent_elts.append(parent)

    def compute_content_type(self):
        if self.textual_content_type is None and self.content is None:
            self.content_type = EMPTY
        elif self.textual_content_type is None:
            self.content_type = ELEMENTS_ONLY
        elif self.textual_content_type in (MIXED, UNKNOWN, ANY):
            self.content_type = self.textual_content_type
        else:
            self.content_type = TEXT_ONLY

    def simplify(self):
        """
        Calls the ``simplify`` method on the group that describes the content
        of the element (if any).

        The ``simplify`` method erases empty sub_groups, merges
        sub-groups with their parent group when possible and corrects
        the occurences inside the alternative groups when applicable.

        If the top-level group in this element is empty, this
        method deletes it. It also deletes the attributes whose
        maximum occurence is ``0``.
        """
        change = True
        while self.content is not None and change:
            change = self.content.simplify()
            if self.content.maximum == 0 or len(self.content.target) == 0:
                self.content = None
            elif (len(self.content.target) == 1 and
                  isinstance(self.content.target.children[0].target, Group)):
                occur = self.content.target.children.pop()
                occur.minimum *= self.content.minimum
                if ( occur.maximum == INFINITY
                     or self.content.maximum == INFINITY):
                    occur.maximum = INFINITY
                else:
                    occur.maximum *= self.content.maximum
                self.content = occur
                change = True
        for att_uid, occur in self.attributes.items():
            if occur.maximum == 0:
                del(self.attributes[att_uid])

    def sort(self):
        """
        Calls the ``sort`` method on the group that describes the content
        of the element (if any) and its sub-groups. Also sorts the parents
        list.
        """
        self.parent_elts.sort(key=operator.attrgetter("qname"))
        if self.content is not None:
            self.content.target.sort()

    def finalize(self):
        self.simplify()
        self.compute_content_type()
        self.sort()
        # Builds the attributes and sub-elements dictionaries for the
        # analysis of the uses inside a library of XML documents
        self.actual_uses = {}
        self.attr_uses = {}
        for occ in self.iter_attrs():
            self.attr_uses[occ.target] = {}
        self.sub_elt_uses = {}
        if self.content is not None:
            for sub_elt in self.content.target.list_sub_elts(True):
                self.sub_elt_uses[sub_elt] = {}

    def reset_uses(self):
        self.actual_uses = {}
        for attr in self.attr_uses:
            self.attr_uses[attr] = {}
        for sub_elt in self.sub_elt_uses:
            self.sub_elt_uses[sub_elt] = {}

    def find_attributes(self, qname):
        """
        Finds and returns all the attributes with this qname.
        """
        occ = self.attributes.get(qname)
        if occ is not None:
            return [occ.target]
        else:
            return []

    def find_children(self, qname):
        """
        Finds and returns all the children with this qname.

        Only works after element has been finalized
        """
        return [sub_elt for sub_elt in self.sub_elt_uses
                if sub_elt.qname == qname]

    def find_parents(self, qname):
        """
        Finds and returns all the parents with this qname.
        """
        return [par_elt for par_elt in self.parent_elts
                if par_elt.qname == qname]

    def __repr__(self):
        return u"Element <{0}>".format(self.qname)


class XMLAttribute(XMLNode):
    """
    Class describing an XML attribute. Attributes occur inside elements.

    .. automethod:: __init__
    """
    def __init__(self, qname):
        """
        Initializes a new XML attribute.

        :param qname:
            Qualified name of the XML attribute (namespace + local name). The
            qualified name is expected to be in the ``{namespace}local-name``
            form.
        :type qname:
            :class:`unicode`
        """
        super(XMLAttribute, self).__init__(qname)

    def add_parent_elt(self, parent):
        """
        Adds a parent element for this attribute.

        :param parent:
            Parent element of this attribute (element that contains the
            attribute).
        :type parent:
            :class:`~pyxst.xml_struct.graph_nodes.XMLElement`
        """
        if parent not in self.parent_elts:
            if len(self.parent_elts) > 0:
                raise Exception("Attribute %s can't have two different parents"
                                % self.qname)
            self.parent_elts.append(parent)

    def __eq__(self, other):
        if not isinstance(other, XMLAttribute):
            return NotImplemented
        return (
            self.namespace == other.namespace
            and self.textual_content_type == other.textual_content_type
            and self.textual_content_is_list == other.textual_content_is_list
            and self.textual_content_values == other.textual_content_values)

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        return u"Attribute @{0}".format(self.qname)
