# -*- coding: utf-8 -*-
"""
This module defines the classes that represent the attributes or the
groups of attributes read in an XML Schema.

The attributes and the groups of attributes are defined as a specific
nodes derived from
:class:`~pyxst.xml_struct.xsd.utils.XsdNode`.

.. autoclass:: XsdAttribute
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: XsdAttributeGroup
   :members:
   :undoc-members:
   :show-inheritance:
"""
__docformat__ = "restructuredtext en"


from .errors import XsdError
from .utils import ATTRIBUTE, ATTRIBUTE_GROUP
from .utils import XsdNode


class XsdAttribute(XsdNode):
    """
    Class representing an attribute defined in an XML Schema.

    .. attribute:: xsd_type

       Type of this attribute declared in the XML Schema. This type is a
       type node.

       Type: :class:`~pyxst.xml_struct.xsd.types.XsdType`

    For this class, the ``category`` class attribute is set to ``ATTRIBUTE``.

    .. automethod:: __init__
    """
    category = ATTRIBUTE

    def __init__(self, name, uid_prefix=u""):
        """
        Initializes a new attribute node.

        :param name:
            Name of the attribute.
        :type name:
            :class:`unicode`
        """
        super(XsdAttribute, self).__init__(name, uid_prefix=uid_prefix)
        self.xsd_type = None

    @property
    def uid(self):
        return u"{0}/@{1}".format(self.uid_prefix, self.name)

class XsdAttributeGroup(XsdNode):
    """
    Class representing an attribute group defined in an XML Schema.

    Attribute groups are only defined to group attributes and ease the
    elements definition.

    As attribute groups can contain attribute groups, before iterating over
    the attributes of this group, it is necessary to collect all the attributes
    defined in the sub-groups.

    .. attribute:: attribute_uses

       List of attribute uses defined in the attribute group.

       Each attribute use is kept as a tuple composed with the attribute
       node itself, the minimum occurence and the maximum occurence.

       Type: list of tuples
       (:class:`~pyxst.xml_struct.xsd_nodes.XsdAttribute`,
       :class:`int`, :class:`int`)

    .. attribute:: attr_groups

       List of attribute groups used in this attribute group.

       Type: list of
       :class:`~pyxst.xml_struct.xsd_nodes.XsdAttributeGroup`

    For this class, the ``category`` class attribute is set to
    ``ATTRIBUTE_GROUP``.

    .. automethod:: __init__
    .. automethod:: __iter__
    """
    category = ATTRIBUTE_GROUP

    def __init__(self, name, uid_prefix=u""):
        """
        Initializes a new attribute group node.

        :param name:
            Name of the attribute group.
        :type name:
            :class:`unicode`
        """
        super(XsdAttributeGroup, self).__init__(name, uid_prefix=uid_prefix)
        self.attribute_uses = []
        self.attr_groups = []

    def add_attribute(self, attr, min_occur=1, max_occur=1):
        """
        Adds the ``attr`` attribute to the attribute group.

        This method only checks that ``attr`` category is ``ATTRIBUTE``. The
        other checks will be performed when the attribute will be inserted in
        the complex types where the attribute group is inserted.

        :param attr:
            Attribute node to be added in this element.
        :type attr:
            :class:`~pyxst.xml_struct.xsd.attributes.XsdAttribute`
        :param min_occur:
            Minimum occurence for the attribute (0 or 1)
        :type min_occur:
            :class:`int`
        :param max_occur:
            Maximum occurence for the attribute (0 or 1)
        :type max_occur:
            :class:`int`
        """
        if not attr.category is ATTRIBUTE:
            raise XsdError("Can't add %s to %s as attribute" % (attr, self))
        self.attribute_uses.append( (attr, min_occur, max_occur) )

    def add_attribute_group(self, attr_grp):
        """
        Adds the ``attr_grp`` attribute group to this attribute group.

        This method only checks ``attr_grp`` category is ``ATTRIBUTE_GROUP``.

        :param attr_grp:
            Attribute group node to be added in this attribute group.
        :type attr_grp:
            :class:`~pyxst.xml_struct.xsd.attributes.XsdAttributeGroup`
        """
        if not attr_grp.category is ATTRIBUTE_GROUP:
            raise XsdError("Can't add %s to %s as attribute group"
                           % (attr_grp, self))
        self.attr_groups.append(attr_grp)

    def __iter__(self):
        """
        Returns an iterator over the attribute uses defined in this
        attribute group and in all its sub-groups.

        The items returned by the iterator are tuples composed with
        (:class:`~pyxst.xml_struct.xsd.attributes.XsdAttribute`,
        :class:`int`, :class:`int`)

        :returns:
            An iterator over all the attribute uses defined in this attribute
            group and its sub-groups.
        :rtype:
            :class:`listiterator`
        """
        lst = self.attribute_uses[:]
        for grp in self.attr_groups:
            for attr_use in iter(grp):
                lst.append(attr_use)
        return iter(lst)

    @property
    def uid(self):
        return u"{0}/@@{1}".format(self.uid_prefix, self.name)
