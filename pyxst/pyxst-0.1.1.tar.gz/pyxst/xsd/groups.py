# -*- coding: utf-8 -*-
"""
This module defines the classes that represent the groups read in an XML
Schema. The groups can be sequences, alls or choices.

The groups are defined as a specific node derived from
:class:`~pyxst.xml_struct.xsd.utils.XsdNode`.

.. autoclass:: XsdGroup
   :members:
   :undoc-members:
   :show-inheritance: 

.. autoclass:: XsdChoice
   :members:
   :undoc-members:
   :show-inheritance: 

.. autoclass:: XsdAll
   :members:
   :undoc-members:
   :show-inheritance: 

.. autoclass:: XsdSequence
   :members:
   :undoc-members:
   :show-inheritance: 
"""
__docformat__ = "restructuredtext en"


from .errors import XsdError
from .utils import XsdNode, XsdUsage
from .utils import GROUP, ELEMENT


class XsdGroup(XsdNode):
    """
    Abstract class representing a group defined in an XML Schema.

    Three different groups can be defined: *choices*, *alls* and *sequences*.
    A choice group defines several options from where one item must be chosen,
    an all group defines a set of items that can occur at most one time but in
    any order and a sequence group defines a sequence of items where the order
    matters.

    If a group is directly defined inside another group or inside a complex
    type, a name is nevertheless automatically created for this group.

    For this class, the ``category`` class attribute is set to ``GROUP``.

    .. automethod:: __init__
    """
    category = GROUP

    def __init__(self, name, uid_prefix=u""):
        """
        Initializes a new group.

        :param name:
            Name of the group.
        :type name:
            :class:`unicode`
        """
        super(XsdGroup, self).__init__(name, uid_prefix=uid_prefix)
        if self.__class__ is XsdGroup:
            raise NotImplementedError("Can't instantiate an abstract class")


class XsdChoice(XsdGroup):
    """
    Class representing a *choice* group defined in an XML Schema.

    A choice group defines several options from where one item must be chosen.

    .. attribute:: options 

       List of all the options defined in this *choice* group. Only one of 
       these options must be chosen in the XML document.

       The uniqueness of each option is checked thanks to the ``option_ids``
       attribute of this class.

       Type: list of 
       :class:`~pyxst.xml_struct.xsd.element.XsdElement` or
       :class:`~pyxst.xml_struct.xsd.groups.XsdGroup`

    .. attribute:: option_ids

       Set containing the identifiers of the options of this group. Hence, 
       this group can't contain two items with the same name.

       This attribute is only used to check that new options added
       to this group don't collide with already defined options with the same 
       name.

       Type: set of :class:`str`

    .. automethod:: __init__
    .. automethod:: __len__
    .. automethod:: __iter__
    """
    def __init__(self, name, uid_prefix=u""):
        """
        Initializes a new *choice* group.

        A *choice* group is a group where only one sub-item can occur chosen
        among the items defined in the *choice* group.

        :param name:
            Name of the group.
        :type name:
            :class:`unicode`
        """
        super(XsdChoice, self).__init__(name, uid_prefix=uid_prefix)
        self.options = []
        self.option_ids = set()

    def add_item(self, item, min_occur=1, max_occur=1):
        """
        Adds the ``item`` item as one option into the *choice* group.

        This method checks that ``item`` category is ``ELEMENT`` or ``GROUP``,
        and that no other item with the same identifier exists in the group.

        :param item:
            Item node to be added in this group.
        :type attr:
            :class:`~pyxst.xml_struct.xsd.elements.XsdElement` or
            :class:`~pyxst.xml_struct.xsd.groups.XsdGroup`
        :param min_occur:
            Minimum occurence for the item
        :type min_occur:
            :class:`int`
        :param max_occur:
            Maximum occurence for the item
        :type max_occur:
            :class:`int` or 
            :data:`~pyxst.xml_struct.utils.INFINITY`
        """
        item_id = item.uid
        if item.category not in [ELEMENT, GROUP]:
            raise XsdError("Can't add %s to %s (should be an element or a "
                           "group)" % (item, self))
        if item_id in self.option_ids:
            raise XsdError("%s already declared in %s" % (item, self))
        self.option_ids.add(item_id)
        self.options.append(XsdUsage(item, min_occur, max_occur))

    def __len__(self):
        """
        Returns the number of options defined in this group.

        :return:
            The number of different options that can occur in the group.
        :rtype:
            :class:`int`
        """
        return len(self.options)

    def __iter__(self):
        """
        Returns an iterator over the different options that can occur in this 
        group.

        :return:
            An iterator over the various options defined in the group.
        :rtype:
            :class:`listiterator` over 
            :class:`~pyxst.xml_struct.xsd.utils.XsdUsage`
        """
        return iter(self.options)


class XsdAll(XsdGroup):
    """
    Class representing an *all* group defined in an XML Schema.

    An all group defines a set of items that can occur at most one time but in
    any order.

    .. attribute:: children 

       List of all the children defined in this *all* group. At most
       one occurence of each child can be inserted in the XML
       document, but in any order.

       The uniqueness of each child is checked thanks to the ``child_ids``
       attribute of this class.

       Type: list of 
       :class:`~pyxst.xml_struct.xsd.elements.XsdElement` or
       :class:`~pyxst.xml_struct.xsd.groups.XsdGroup`

    .. attribute:: child_ids

       Set containing the identifiers of the children of this group. Hence, 
       this group can't contain two items with the same name.

       This attribute is only used to check that new children added
       to this group don't collide with already defined children with the same 
       name.

       Type: set of :class:`str`

    .. automethod:: __init__
    .. automethod:: __len__
    .. automethod:: __iter__
    """
    def __init__(self, name, uid_prefix=u""):
        """
        Initializes a new *all* group.

        An *all* group is a group where the sub-items can occur in any order 
        but at most one time.

        :param name:
            Name of the group.
        :type name:
            :class:`unicode`
        """
        super(XsdAll, self).__init__(name, uid_prefix=uid_prefix)
        self.children = []
        self.child_ids = set()

    def add_item(self, item, min_occur=1, max_occur=1):
        """
        Adds the ``item`` item as one sub-item of the *all* group.

        This method checks that ``item`` category is ``ELEMENT`` or ``GROUP``,
        that no other item with the same identifier exists in the group, and
        that the maximum occurence is not greater than 1.

        :param item:
            Item node to be added in this group.
        :type attr:
            :class:`~pyxst.xml_struct.xsd.elements.XsdElement` or
            :class:`~pyxst.xml_struct.xsd.groups.XsdGroup`
        :param min_occur:
            Minimum occurence for the item (0 or 1)
        :type min_occur:
            :class:`int`
        :param max_occur:
            Maximum occurence for the item (0 or 1)
        :type max_occur:
            :class:`int`
        """
        item_id = item.uid
        if item.category not in [ELEMENT, GROUP]:
            raise XsdError("Can't add %s to %s (should be an element or a "
                           "group)" % (item, self))
        if item_id in self.child_ids:
            raise XsdError("%s already declared in %s" % (item, self))
        if max_occur > 1:
            raise XsdError("%s can't occur more than one time in %s" 
                           % (item, self))
        self.child_ids.add(item_id)
        self.children.append(XsdUsage(item, min_occur, max_occur))

    def __len__(self):
        """
        Returns the number of children defined in this all.

        :return:
            The number of different children that can occur in the all.
        :rtype:
            :class:`int`
        """
        return len(self.children)

    def __iter__(self):
        """
        Returns an iterator over the children that can occur in this 
        group.

        :return:
            An iterator over the children defined in the group.
        :rtype:
            :class:`listiterator` over 
            :class:`~pyxst.xml_struct.xsd.utils.XsdUsage`
        """
        return iter(self.children)


class XsdSequence(XsdGroup):
    """
    Class representing a *choice* group defined in an XML Schema.

    A sequence group defines a sequence of items where the order
    matters.

    .. attribute:: children 

       List of all the children defined in this *sequence* group. Each child
       must be inserted in the XML document in the exact order defined in this
       group.

       Type: list of 
       :class:`~pyxst.xml_struct.xsd.elements.XsdElement` or
       :class:`~pyxst.xml_struct.xsd.groups.XsdGroup`

    .. automethod:: __init__
    .. automethod:: __len__
    .. automethod:: __iter__
    """
    def __init__(self, name, uid_prefix=u""):
        """
        Initializes a new *sequence* group.

        A *sequence* group is a group where the sub-items must respect
        the given order but can occur any number of times.

        :param name:
            Name of the group.
        :type name:
            :class:`unicode`
        """
        super(XsdSequence, self).__init__(name, uid_prefix=uid_prefix)
        self.children = []

    def add_item(self, item, min_occur=1, max_occur=1):
        """
        Adds the ``item`` item as one sub-item of the *sequence* group. The
        item is added at the end of the sequence.

        This method checks that ``item`` category is ``ELEMENT`` or ``GROUP``.

        :param item:
            Item node to be added in this group.
        :type attr:
            :class:`~pyxst.xml_struct.xsd.elements.XsdElement` or
            :class:`~pyxst.xml_struct.xsd.groups.XsdGroup`
        :param min_occur:
            Minimum occurence for the item
        :type min_occur:
            :class:`int`
        :param max_occur:
            Maximum occurence for the item
        :type max_occur:
            :class:`int` or 
            :data:`~pyxst.xml_struct.utils.INFINITY`
        """
        if item.category not in [ELEMENT, GROUP]:
            raise XsdError("Can't add %s to %s (should be an element or a "
                           "group)" % (item, self))
        self.children.append(XsdUsage(item, min_occur, max_occur))

    def __len__(self):
        """
        Returns the number of children defined in this sequence.

        :return:
            The number of different children that can occur in the sequence.
        :rtype:
            :class:`int`
        """
        return len(self.children)

    def __iter__(self):
        """
        Returns an iterator over the children that can occur in this 
        group.

        :return:
            An iterator over the children defined in the group.
        :rtype:
            :class:`listiterator` over 
            :class:`~pyxst.xml_struct.xsd.utils.XsdUsage`
        """
        return iter(self.children)
