# -*- coding: utf-8 -*-
"""
This module defines the classes that represent the types read in an XML
Schema.

The types are defined as a specific node derived from
:class:`~pyxst.xml_struct.xsd.utils.XsdNode`.

.. autodata:: EMPTY

.. autodata:: LIST

.. autodata:: UNION

.. autodata:: ELEMENTS_ONLY

.. autodata:: EXTENSION

.. autodata:: CONSTRAINT_MAPPING

.. autoclass:: XsdType
   :members:
   :undoc-members:
   :show-inheritance: 

.. autoclass:: XsdSimpleType
   :members:
   :undoc-members:
   :show-inheritance: 

.. autoclass:: XsdSimpleListType
   :members:
   :undoc-members:
   :show-inheritance: 

.. autoclass:: XsdSimpleUnionType
   :members:
   :undoc-members:
   :show-inheritance: 

.. autoclass:: XsdComplexType
   :members:
   :undoc-members:
   :show-inheritance: 
"""
__docformat__ = "restructuredtext en"


from .errors import XsdError
from .utils import split_qname, MIXED
from .utils import (
    XsdNode, XsdUsage, TYPE, ATTRIBUTE, ATTRIBUTE_GROUP, XSD_NS)
from .groups import XsdSequence
from .constraints import (
    XsdStrictMinConstraint, XsdMinConstraint, XsdMaxConstraint,
    XsdStrictMaxConstraint, XsdMaxDigitsConstraint, XsdMinDigitsConstraint,
    XsdLengthConstraint, XsdMinLengthConstraint, XsdMaxLengthConstraint,
    XsdPossibleValuesConstraint, XsdWhiteSpacePolicyConstraint,
    XsdValuePatternConstraint)


EMPTY = "Empty"
"""
Constant used to define the type of the content that can occur inside a type.
The type doesn't have any content.

Type: :class:`str`
"""

LIST = "List of Textual Items"
"""
Constant used to define the type of the content that can occur inside a type.
The type contains a space separated list of textual items.

Type: :class:`str`
"""

UNION = "Alternative between Textual Types"
"""
Constant used to define the type of the content that can occur inside a type.
The type of the content must be chosen among several textual types.

Type: :class:`str`
"""

ELEMENTS_ONLY = "Only Elements"
"""
Constant used to define the type of the content that can occur inside a type.
The type only contains sub-elements.

Type: :class:`str`
"""

RESTRICTION = "Restriction"
"""
Constant used to define the derivation method between a type and its base
type. The type restricts its base type (adds new constraints).

Type: :class:`str`
"""

EXTENSION = "Extension"
"""
Constant used to define the derivation method between a type and its base
type. The type extends its base type (adds new attributes or sub-elements).

Type: :class:`str`
"""

CONSTRAINT_MAPPING = {u"minExclusive"  : XsdStrictMinConstraint,
                      u"minInclusive"  : XsdMinConstraint,
                      u"maxExclusive"  : XsdStrictMaxConstraint,
                      u"maxInclusive"  : XsdMaxConstraint,
                      u"totalDigits"   : XsdMaxDigitsConstraint,
                      u"fractionDigits": XsdMinDigitsConstraint,
                      u"length"        : XsdLengthConstraint,
                      u"minLength"     : XsdMinLengthConstraint,
                      u"maxLength"     : XsdMaxLengthConstraint,
                      u"enumeration"   : XsdPossibleValuesConstraint,
                      u"whiteSpace"    : XsdWhiteSpacePolicyConstraint,
                      u"pattern"       : XsdValuePatternConstraint,
                      }
"""
Dictionary mapping the name of the constraints found in the simple type
restrictions and the classes that represent these constraints.

Type: dictionary of :class:`class` indexed with :class:`unicode`
"""


class XsdType(XsdNode):
    """
    Abstract class representing a type defined in an XML Schema.

    Two different types can be defined: simple types that only contain textual
    data or complex types that can contain attributes or elements. In an XML
    Schema, it is also possible to define types that are derived from other 
    types (they use the definition of the other type and add or remove
    some content or some constraints).

    After all the types have been read, it is possible to resolve the 
    derivation hierarchy ie propagate in each type the information stored
    in the types it is derived from (see ``resolve_derivation`` method).

    If a type is directly defined inside an element, a name is nevertheless 
    automatically created for this type.

    .. attribute:: content_type

       Type of the content that can be found in the type. If the type is a 
       simple type or a complex type with a simple content, the content is 
       purely textual and therefore this attribute will give the built-in type 
       of this content (string, float, date, etc.)

       If the type is a simple list type or a simple union type, this attribute
       is left emptycomplex type with
       complex content, the content can either be ``ELEMENTS_ONLY`` or
       ``MIXED`` (a mixed content is a content that mixes textual data
       and child elements).

    .. attribute:: derivation_resolved

       Flag set to true after the derivation of this type has been resolved.
       When the derivation is resolved, all the information inherited from the
       base type has been propagated in this type.

    .. attribute:: constraints

       Constraints applied to the base type this type is
       derived from.  Different sorts of constraints can be
       defined. They are stored in a dictionary whose key is the name
       of the constraint (name of the XML constraint element in the
       XML Schema). The possible names of constraints are:
       ``minExclusive``,``minInclusive``, ``maxExclusive``,
       ``maxInclusive``, ``totalDigits``, ``fractionDigits``,
       ``length``, ``minLength``, ``maxLength``, ``enumeration``,
       ``whiteSpace``, ``pattern``.

       Only types whose content is purely textual (simple types or complex
       types with simple content) can have constraints.

       Type: Dictionary of 
       :class:`~pyxst.xml_struct.xsd.constraints.XsdConstraint` 
       indexed with :class:`unicode`

    .. attribute:: _base_type

       Base type that this type is derived from. The derivation method
       is defined with ``_derivation_method`` attribute.

       This attribute is private as it is not necessary to read the information
       in the base type after the derivation of this type has been resolved.

       Type: :class:`~pyxst.xml_struct.xsd.types.XsdType`

    .. attribute:: _deriv_method

       Method of derivation used to define this type from its base type 
       declared in ``_base_type`` attribute. The possible values for this
       attribute are ``RESTRICTION`` and ``EXTENSION``.

       This attribute is private as it is not necessary to read the information
       in the base type after the derivation of this type has been resolved.

       Type: :class:`str`

    For this class, the ``category`` class attribute is set to ``TYPE``.

    .. automethod:: __init__
    """
    category = TYPE

    def __init__(self, name, uid_prefix=u""):
        """
        Initializes a new type node.

        :param name:
            Name of the type.
        :type name:
            :class:`unicode`
        """
        super(XsdType, self).__init__(name, uid_prefix=uid_prefix)
        self.content_type = EMPTY
        self.derivation_resolved = False
        self.constraints = {}
        self._base_type = None
        self._deriv_method = None
        if self.__class__ is XsdType and \
                name not in [u"{%s}anyType" % XSD_NS, 
                             u"{%s}anySimpleType" % XSD_NS]:
            raise XsdError("Can't use this base type for instantiating %s type"
                           " (reserved to basis types)" % name)

    def add_constraint(self, name, value):
        """
        Adds a constraint whose type is ``name`` and value is ``value`` on the
        type.

        The XML Schema defines a set of possible constraints that can be
        set on the textual content found in a type.

        :param name:
            Name of the constraint. The name corresponds to the name
            of the constraint elements that exist in the XML Schema :
            ``minExclusive``,``minInclusive``, ``maxExclusive``,
            ``maxInclusive``, ``totalDigits``, ``fractionDigits``,
            ``length``, ``minLength``, ``maxLength``, ``enumeration``,
            ``whiteSpace``, ``pattern``.
        :type name:
            :class:`unicode`
        :param value:
            Value defined in the constraint.
        :type name:
            :class:`unicode`
        """
        if value is not None:
            cnstr = self.constraints.setdefault(name, 
                                                CONSTRAINT_MAPPING[name]())
            cnstr.define_value(value)

    def resolve_derivation(self):
        """
        Resolves the derivation of this type.

        As the types that are instances of ``XsdType`` are the most elementary
        built-in types that are at the basis of the types hierarchy, we have
        nothing to do.

        This method defines the ``content_type`` attribute.

        As this method must not be called more than once, a flag
        (``derivation_resolved`` attribute) is set after the method
        has been completed. The method is not executed if the flag is
        set.
        """
        if self.derivation_resolved:
            return
        # Type is a basic built-in type (anyType ou anySimpleType)
        ns, local_name = split_qname(self.name)
        self.content_type = local_name
        self.derivation_resolved = True

    @property
    def uid(self):
        return u"{0}/${1}".format(self.uid_prefix, self.name)


class XsdSimpleType(XsdType):
    """
    Class representing a simple type defined in an XML Schema.

    Simple types are types that only contain textual data (no attribute nor
    sub-elements).

    .. automethod:: __init__
    """
    def __init__(self, name, uid_prefix=u""):
        """
        Initializes a new simple type node.

        :param name:
            Name of the type.
        :type name:
            :class:`unicode`
        """
        super(XsdSimpleType, self).__init__(name, uid_prefix=uid_prefix)

    def resolve_derivation(self):
        """
        Resolves the derivation of this type by propagating the information
        defined on the base type into this type.

        This method defines the ``content_type`` attribute (even if there is
        no derivation from a base type), propagates the constraints defined
        on the base type into this type.

        As this method must not be called more than once, a flag
        (``derivation_resolved`` attribute) is set after the method
        has been completed. The method is not executed if the flag is
        set.
        """
        if self.derivation_resolved:
            return
        # Resolution of derivation on base type that we derive from
        if self._base_type is not None:
            self._base_type.resolve_derivation()
        # Content type definition
        if self._base_type is not None:
            self.content_type = self._base_type.content_type
        else:
            # Simple type is a built-in type
            ns, local_name = split_qname(self.name)
            self.content_type = local_name
        # Constraints propagation
        if self._base_type is not None:
            for name, cnst in self._base_type.constraints.items():
                if name == u"enumeration":
                    for val in cnst.value:
                        self.add_constraint(u"enumeration", val)
                else:
                    if name not in self.constraints:
                        self.constraints[name] = cnst                
        self.derivation_resolved = True


class XsdSimpleListType(XsdSimpleType):
    """
    Class representing a simple type defined in an XML Schema that contains a
    list of items whose type is also a simple one.

    Simple types are types that only contain textual data (no attribute nor
    sub-elements).

    .. attribute:: listitem_type

       Type of the list items contained in the list

       Type: :class:`~pyxst.xml_struct.xsd.types.SimpleType`

    .. automethod:: __init__
    """
    def __init__(self, name, listitem_type=None, uid_prefix=u""):
        """Initializes a new simple list type node.

        :param name: Name of the type.  :type name: :class:`unicode`
            :param listitem_type: Type of the list items contained in
            this list.  :type listitem_type:
            :class:`~pyxst.xml_struct.xsd.types.XsdType`

        """
        super(XsdSimpleListType, self).__init__(name, uid_prefix=uid_prefix)
        self.content_type = LIST
        if not listitem_type is None and not listitem_type.category is TYPE:
            raise XsdError("%s can't contain %s list items (should be another "
                           "type)." % (self, listitem_type))
        self.listitem_type = listitem_type

    def add_constraint(name, value):
        """
        Raises an exception as it is impossible to directly set a constraint
        on a list type.
        """
        raise XsdError("Can't set a constraint on %s" % self)

    def resolve_derivation(self):
        """
        Resolves the derivation of this type by propagating the resolution
        onto the list item type.

        This method redefines the ``content_type`` attribute that is always
        set to ``LIST`` and doesn't propagate the constraints as there is
        no constraint on a list type.

        As this method must not be called more than once, a flag
        (``derivation_resolved`` attribute) is set after the method
        has been completed. The method is not executed if the flag is
        set.
        """
        if self.derivation_resolved:
            return
        if self._base_type is not None:
            raise XsdError("%s can't derive from a base type" % self)
        if self.listitem_type is None:
            raise XsdError("%s should contain a list item type" % self)
        self.content_type = LIST
        # Resolution of derivation on the list item type
        self.listitem_type.resolve_derivation()
        self.derivation_resolved = True


class XsdSimpleUnionType(XsdSimpleType):
    """
    Class representing a simple type defined in an XML Schema that is
    a choice between several possible types, each one being a simple type.

    Simple types are types that only contain textual data (no attribute nor
    sub-elements).

    .. attribute:: possible_types

       Set of the possible types that can be chosen.

       Type: Set of :class:`~pyxst.xml_struct.xsd.types.SimpleType`

    .. automethod:: __init__
    """
    def __init__(self, name, possible_types=None, uid_prefix=u""):
        """
        Initializes a new simple union type node.

        :param name:
            Name of the type.
        :type name:
            :class:`unicode`
        :param possible_types:
            Possible types of this union.
        :type possible_types:
            List of :class:`~pyxst.xml_struct.xsd.types.XsdType`
        """
        super(XsdSimpleUnionType, self).__init__(name, uid_prefix=uid_prefix)
        self.content_type = UNION
        self.possible_types = set([])
        if possible_types is not None:
            for typ in possible_types:
                if not typ.category is TYPE:
                    raise XsdError("%s can't contain %s possible type (should "
                                   "be another type)." % (self, typ))
                self.possible_types.add(typ)

    def add_constraint(name, value):
        """
        Raises an exception as it is impossible to directly set a constraint
        on an union type.
        """
        raise XsdError("Can't set a constraint on %s" % self)

    def resolve_derivation(self):
        """
        Resolves the derivation of this type by propagating the resolution
        onto each of the possible types.

        This method redefines the ``content_type`` attribute that is always
        set to ``UNION`` and doesn't propagate the constraints as there is
        no constraint on a union type.

        As this method must not be called more than once, a flag
        (``derivation_resolved`` attribute) is set after the method
        has been completed. The method is not executed if the flag is
        set.
        """
        if self.derivation_resolved:
            return
        if self._base_type is not None:
            raise XsdError("%s can't derive from a base type" % self)
        if len(self.possible_types) == 0:
            raise XsdError("%s should contain several possible types" % self)
        self.content_type = UNION
        # Resolution of derivation on all the possible types
        for typ in self.possible_types:
            typ.resolve_derivation()
        self.derivation_resolved = True


class XsdComplexType(XsdType):
    """
    Class representing a complex type defined in an XML Schema.

    Complex types are types that can contain attributes. Complex types
    with complex content can contain sub-elements whereas complex
    types with simple content only contain text data.

    Some complex types with complex content can contain elements and
    textual data. This content is called mixed. Mixed content is
    specified in the ``content_type`` attribute.

    .. attribute:: sub_content

       When the complex type has a complex content, this attribute
       contains an usage node pointing towards a group (sequence, choice or 
       all) that contains the sub-elements and sub-groups that can occur 
       inside the type.

       When the complex type has a simple content, this attribute remains
       empty.

       Type: :class:`~pyxst.xml_struct.xsd.utils.XsdUsage`

    .. attribute:: attributes 

       List of all the attributes of this complex type.

       The uniqueness of each attribute is checked thanks to the ``attr_ids``
       attribute of this class.

       Type: list of 
       :class:`~pyxst.xml_struct.xsd.attributes.XsdAttribute`

    .. attribute:: attr_ids

       Set containing the identifiers of the attributes of this complex type. 
       Hence, this complex type can't have two attributes with the same name.

       This attribute is only used to check that new attributes added
       to this complex type don't collide with already defined
       attributes with the same name.

       Type: set of :class:`str`

    .. attribute:: attr_groups

       List of attribute groups used in this complex type.

       As it is much more interesting to directly have all the
       attributes defined in this complex type (instead of having a
       hierarchy of attribute groups), a method
       (``resolve_attribute_groups``) is provided to add all the
       attributes of the attributes groups in the complex type.

       Type: list of 
       :class:`~pyxst.xml_struct.xsd.attributes.XsdAttributeGroup`

    .. attribute:: _attr_groups_resolved

       Flag that is true id the attribute groups of this complex type have
       already been resolved (ie if the attributes defined in the attribute
       groups have been directly added to this complex type).

       See ``resolve_attribute_groups`` method.

       Type: :class:`boolean`

    .. automethod:: __init__
    """
    def __init__(self, name, uid_prefix=u""):
        """
        Initializes a new complex type node.

        :param name:
            Name of the type.
        :type name:
            :class:`unicode`
        """
        super(XsdComplexType, self).__init__(name, uid_prefix=uid_prefix)
        self.sub_content = None
        self.attributes = []
        self.attr_ids = set()
        self.attr_groups = []
        self._attr_groups_resolved = False

    def add_attribute(self, attr, min_occur=1, max_occur=1):
        """
        Adds the ``attr`` attribute to the complex type.

        This method checks that ``attr`` category is ``ATTRIBUTE``, that
        max_occur is never greater than 1 and that there is not already an
        attribute with the same identifier in this complex type.

        :param attr:
            Attribute node to be added in this complex type.
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
        attr_id = attr.uid
        if not attr.category is ATTRIBUTE:
            raise XsdError("Can't add %s to %s as attribute" % (attr, self))
        if attr_id in self.attr_ids:
            raise XsdError("%s already declared in %s" % (attr, self))
        if max_occur > 1:
            raise XsdError("%s can't occur more than one time in %s" 
                           % (attr, self))
        self.attr_ids.add(attr_id)
        self.attributes.append(XsdUsage(attr, min_occur, max_occur))

    def add_attribute_group(self, attr_grp):
        """
        Adds the ``attr_grp`` attribute group to this complex type.

        This method checks ``attr_grp`` category is ``ATTRIBUTE_GROUP``.

        :param attr_grp:
            Attribute group node to be added in this complex type.
        :type attr_grp:
            :class:`~pyxst.xml_struct.xsd.attributes.XsdAttributeGroup` 
        """
        if not attr_grp.category is ATTRIBUTE_GROUP:
            raise XsdError("Can't add %s to %s as attribute group" 
                           % (attr_grp, self))
        self.attr_groups.append(attr_grp)

    def resolve_attribute_groups(self):
        """
        Resolves the attribute group references by reading their
        content and adding all the attributes defined in the attribute
        groups into this complex type thanks to the ``add_attribute``
        method.

        As this method must not be called more than once (it is an error to
        define several times an attribute with the same name), a flag 
        (``_attr_groups_resolved`` attribute) is set after the method has been
        completed. The method is not executed if the flag is set.
        """
        if self._attr_groups_resolved:
            return
        for attr_grp in self.attr_groups:
            for attr, min_occur, max_occur in iter(attr_grp):
                self.add_attribute(attr, min_occur, max_occur)
        self._attr_groups_resolved = True

    def resolve_derivation(self):
        """
        Resolves the derivation of this type by propagating the information
        defined on the base type into this type. The propagation depends on
        the derivation method (restriction or extension).

        This method defines the ``content_type`` attribute (even if there is
        no derivation from a base type), propagates the constraints defined
        on the base type into this type, aggregates the inner content defined
        in the ``sub_content`` attribute with the inner content defined in the 
        base type (only if the derivation method is extension) and propagates 
        the attributes defined in the base type into this type.

        As this method must not be called more than once, a flag
        (``derivation_resolved`` attribute) is set after the method
        has been completed. The method is not executed if the flag is
        set.
        """
        if self.derivation_resolved:
            return
        # Resolution of derivation on base type that we derive from
        if self._base_type is not None:
            self._base_type.resolve_derivation()
        # Content type definition
        if self.content_type != MIXED:
            if self._base_type is not None:
                self.content_type = self._base_type.content_type
                if self.sub_content is not None and \
                        len(self.sub_content.referenced_node) > 0:
                    self.content_type = ELEMENTS_ONLY
                elif self._deriv_method == RESTRICTION and \
                        self._base_type.content_type in [MIXED, ELEMENTS_ONLY]:
                    self.content_type = EMPTY
                elif self._deriv_method == EXTENSION and \
                        self._base_type.content_type == MIXED and \
                        self._base_type.sub_content is not None and \
                        len(self._base_type.sub_content.referenced_node) > 0:
                    self.content_type = ELEMENTS_ONLY
            else:
                if self.sub_content is not None and \
                        len(self.sub_content.referenced_node) > 0:
                    self.content_type = ELEMENTS_ONLY
                else:
                    self.content_type = EMPTY
        elif self.sub_content is None:
            # A Mixed content with no sub-element is just a textual content
            self.content_type = u"anySimpleType"
        # Constraints propagation
        if self._base_type is not None:
            for name, cnst in self._base_type.constraints.items():
                if name == u"enumeration":
                    for val in cnst.value:
                        self.add_constraint(u"enumeration", val)
                else:
                    if name not in self.constraints:
                        self.constraints[name] = cnst
        # Sub-content aggregation
        if isinstance(self._base_type, XsdComplexType) and \
                self._base_type.sub_content is not None:
            if self._deriv_method == EXTENSION:
                if self.sub_content is None or \
                        len(self.sub_content.referenced_node) == 0:
                    self.sub_content = self._base_type.sub_content
                else:
                    aggr = XsdSequence("%s/extension" % self.name)
                    aggr.children.append(self._base_type.sub_content)
                    aggr.children.append(self.sub_content)
                    self.sub_content = XsdUsage(aggr, 1, 1)
        # Attributes propagation
        if isinstance(self._base_type, XsdComplexType):
            for attr_use in self._base_type.attributes:
                attr_id = attr_use.referenced_node.uid
                if attr_id not in self.attr_ids:
                    self.attr_ids.add(attr_id)
                    self.attributes.append(attr_use)
                elif self._deriv_method == EXTENSION:
                    raise XsdError("%s already declared in %s" % (attr, self))
        self.derivation_resolved = True
