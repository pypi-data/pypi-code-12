# -*- coding: utf-8 -*-
"""
This module defines the classes that represent the constraints that can
be defined in an XML Schema when restricting a simple type.

.. autoclass:: XsdConstraint
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: XsdMinConstraint
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: XsdStrictMinConstraint
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: XsdMaxConstraint
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: XsdStrictMaxConstraint
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: XsdMaxDigitsConstraint
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: XsdMinDigitsConstraint
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: XsdLengthConstraint
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: XsdMaxLengthConstraint
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: XsdMinLengthConstraint
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: XsdPossibleValuesConstraint
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: XsdValuePatternConstraint
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: XsdWhiteSpacePolicyConstraint
   :members:
   :undoc-members:
   :show-inheritance:
"""
__docformat__ = "restructuredtext en"


from .errors import XsdError


class XsdConstraint(object):
    """
    Base class for the constraints defined in the restriction of the simple
    types.

    In an XML Schema, several sorts of constraint can be defined:
    ``minExclusive``,``minInclusive``, ``maxExclusive``,
    ``maxInclusive``, ``totalDigits``, ``fractionDigits``, ``length``,
    ``minLength``, ``maxLength``, ``enumeration``, ``whiteSpace`` and
    ``pattern``.

    .. attribute:: value

       Value associated to the constraint. The exact type of the value
       depends on the sort of constraint (minimum, policy, set of possible
       values). See the derived classes for more details.

    .. attribute:: constraint_phrase

       Class attribute defining a little phrase that explains the
       constraint (used for the string representation).

       Type: :class:`str`
    """
    constraint_phrase = ""

    def __init__(self):
        """
        Initializes a new constraint.
        """
        self.value = None
        if self.__class__ is XsdConstraint:
            raise NotImplementedError("Abstract classes can't be implemented")

    def define_value(self, value):
        """
        Defines the value associated with the constraint.

        If the new value is less constraining than the
        value actually defined in the constraint, the new value is not
        taken into account.

        This abstract method will be defined in derived classes.

        :param value:
            Value associated with the constraint.
        :type value:
            Depends on the actual constraint (see derived classes).
        """
        raise NotImplementedError("Abstract method can't be called")

    def __repr__(self):
        """
        Returns a string representation of the constraint.

        :returns:
            String representation of the constraint
        :rtype:
            :class:`str`
        """
        return "%s %s" % (self.constraint_phrase, self.value)


class XsdMinConstraint(XsdConstraint):
    """
    Constraint corresponding to ``minInclusive`` that gives the minimum of
    the content found in a simple type.

    The value associated to this constraint is a :class:`float`.
    """
    constraint_phrase = "Value >= "

    def define_value(self, value):
        """
        Defines the value associated with the constraint (minimum).

        :param value:
            Value associated with the constraint.
        :type value:
            :class:`float`
        """
        try:
            value = float(value)
        except ValueError, exc:
            raise XsdError("Value \"%s\" in constraint should be a number"
                           % value)
        if self.value is None or self.value < value:
            self.value = value


class XsdStrictMinConstraint(XsdConstraint):
    """
    Constraint corresponding to ``minExclusive`` that gives the strict
    minimum of the content found in a simple type (content can't be
    equal to the minimum).

    The value associated to this constraint is a :class:`float`.
    """
    constraint_phrase = "Value > "

    def define_value(self, value):
        """
        Defines the value associated with the constraint (strict minimum).

        :param value:
            Value associated with the constraint.
        :type value:
            :class:`float`
        """
        try:
            value = float(value)
        except ValueError, exc:
            raise XsdError("Value \"%s\" in constraint should be a number"
                           % value)
        if self.value is None or self.value < value:
            self.value = value


class XsdMaxConstraint(XsdConstraint):
    """
    Constraint corresponding to ``maxInclusive`` that gives the maximum of
    the content found in a simple type.

    The value associated to this constraint is a :class:`float`.
    """
    constraint_phrase = "Value <= "

    def define_value(self, value):
        """
        Defines the value associated with the constraint (maximum).

        :param value:
            Value associated with the constraint.
        :type value:
            :class:`float`
        """
        try:
            value = float(value)
        except ValueError, exc:
            raise XsdError("Value \"%s\" in constraint should be a number"
                           % value)
        if self.value is None or self.value > value:
            self.value = value


class XsdStrictMaxConstraint(XsdConstraint):
    """
    Constraint corresponding to ``maxExclusive`` that gives the strict
    maximum of the content found in a simple type (content can't be
    equal to maximum).

    The value associated to this constraint is a :class:`float`.
    """
    constraint_phrase = "Value < "

    def define_value(self, value):
        """
        Defines the value associated with the constraint (strict maximum).

        :param value:
            Value associated with the constraint.
        :type value:
            :class:`float`
        """
        try:
            value = float(value)
        except ValueError, exc:
            raise XsdError("Value \"%s\" in constraint should be a number"
                           % value)
        if self.value is None or self.value > value:
            self.value = value


class XsdMaxDigitsConstraint(XsdConstraint):
    """
    Constraint corresponding to ``totalDigits`` that gives the maximum number
    of digits of the content found in simple type.

    The value associated to this constraint is an :class:`int`.
    """
    constraint_phrase = "Number of digits of Value <= "

    def define_value(self, value):
        """
        Defines the value associated with the constraint (maximum number of
        digits).

        :param value:
            Value associated with the constraint.
        :type value:
            :class:`int`
        """
        try:
            value = int(value)
        except ValueError, exc:
            raise XsdError("Value %s in constraint should be an integer"
                           % value)
        if self.value is None or self.value > value:
            self.value = value


class XsdMinDigitsConstraint(XsdConstraint):
    """
    Constraint corresponding to ``fractionDigits`` that gives the
    minimum number of digits of the content found in simple type.

    The value associated to this constraint is an :class:`int`.
    """
    constraint_phrase = "Number of digits of Value >= "

    def define_value(self, value):
        """
        Defines the value associated with the constraint (minimum number of
        digits).

        :param value:
            Value associated with the constraint.
        :type value:
            :class:`int`
        """
        try:
            value = int(value)
        except ValueError, exc:
            raise XsdError("Value %s in constraint should be an integer"
                           % value)
        if self.value is None or self.value < value:
            self.value = value


class XsdLengthConstraint(XsdConstraint):
    """
    Constraint corresponding to ``length`` that gives the length of the
    content found in simple type (string length or list length).

    The value associated to this constraint is an :class:`int`.
    """
    constraint_phrase = "Length of Value == "

    def define_value(self, value):
        """
        Defines the value associated with the constraint (length).

        :param value:
            Value associated with the constraint.
        :type value:
            :class:`int`
        """
        try:
            value = int(value)
        except ValueError, exc:
            raise XsdError("Value %s in constraint should be an integer"
                           % value)
        self.value = value


class XsdMaxLengthConstraint(XsdConstraint):
    """
    Constraint corresponding to ``maxLength`` that gives the maximum
    length of the content found in simple type (string length or list
    length).

    The value associated to this constraint is an :class:`int`.
    """
    constraint_phrase = "Length of Value <= "

    def define_value(self, value):
        """
        Defines the value associated with the constraint (maximum length).

        :param value:
            Value associated with the constraint.
        :type value:
            :class:`int`
        """
        try:
            value = int(value)
        except ValueError, exc:
            raise XsdError("Value %s in constraint should be an integer"
                           % value)
        if self.value is None or self.value > value:
            self.value = value


class XsdMinLengthConstraint(XsdConstraint):
    """
    Constraint corresponding to  ``minLength`` that gives the minimum
    length of the content found in simple type (string length or list
    length).

    The value associated to this constraint is an :class:`int`.
    """
    constraint_phrase = "Length of Value >= "

    def define_value(self, value):
        """
        Defines the value associated with the constraint (minimum length).

        :param value:
            Value associated with the constraint.
        :type value:
            :class:`int`
        """
        try:
            value = int(value)
        except ValueError, exc:
            raise XsdError("Value %s in constraint should be an integer"
                           % value)
        if self.value is None or self.value < value:
            self.value = value


class XsdPossibleValuesConstraint(XsdConstraint):
    """
    Constraint corresponding to ``enumeration`` that gives the possible
    values of the content found in the simple type.

    The value associated to this constraint is a :class:`set` of
    :class:`unicode` that gives all the possible values for the
    content.
    """
    constraint_phrase = "Value in "

    def define_value(self, value):
        """
        Defines a new possible value for the constraint (defined set
        of possible values).

        :param value:
            New value associated with the constraint.
        :type value:
            :class:`unicode`
        """
        if self.value is None:
            self.value = set()
        self.value.add(value)


class XsdValuePatternConstraint(XsdConstraint):
    """
    Constraint corresponding to ``pattern`` that gives the pattern
    expected for the content of simple type. The pattern is defined as
    a regular expression.

    The value associated to this constraint is a :class:`unicode`.
    """
    constraint_phrase = "Value matches RegExp: "

    def define_value(self, value):
        """
        Defines the value associated with the constraint (pattern of
        regular expression).

        :param value:
            Value associated with the constraint.
        :type value:
            :class:`unicode`
        """
        self.value = value


class XsdWhiteSpacePolicyConstraint(XsdConstraint):
    """
    Constraint corresponding to ``whiteSpace`` that gives the policy
    for processing the white spaces in the content found in the simple
    type.

    The value associated to this constraint is a :class:`unicode`.
    """
    constraint_phrase = "White spaces processing in Value: "

    def define_value(self, value):
        """
        Defines the value associated with the constraint (chosen
        policy for the white spaces processing).

        :param value:
            Value associated with the constraint.
        :type value:
            :class:`unicode`
        """
        self.value = value
