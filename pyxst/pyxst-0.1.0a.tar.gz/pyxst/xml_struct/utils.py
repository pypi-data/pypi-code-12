# -*- coding: utf-8 -*-
"""
This module defines several utilitary constants and functions, mainly for
proessing the names and namespaces of XML nodes.

Constants
.........

.. autodata:: INFINITY

.. autodata:: ANY

.. autodata:: MIXED

.. autodata:: UNKNOWN

.. autodata:: BOOLEAN

.. autodata:: INTEGER

.. autodata:: FLOAT

.. autodata:: STRING

.. autodata:: DATETIME

.. autodata:: DURATION

.. autodata:: BASE64

.. autodata:: HEXA

.. autodata:: ABSENT
.. autodata:: DIFFERENT
.. autodata:: SAME

.. autodata EMPTY
.. autodata TEXT_ONLY
.. autodata ELEMENTS_ONLY

.. autodata DTD
.. autodata XML_SCHEMA

Functions
.........

.. autofunction:: split_qname

.. autofunction:: combine_types
"""
__docformat__ = "restructuredtext en"


INFINITY = u"Infinity"
"""
Constant describing the infinity (for unbounded occurences).

Type: :class:`unicode`
"""

ANY = u"Any text or elements"
"""
Constant describing the type of content that can be anything.

Type: :class:`unicode`
"""

MIXED = u"Mixed Content"
"""
Constant describing the type of the content that can occur inside an element
if this element can contain, at the same time, sub-elements and textual data.

Type: :class:`unicode`
"""

UNKNOWN = u"Unknown"
"""
Constant describing the type of a textual content that is not known.

Type: :class:`unicode`
"""

BOOLEAN = u"Boolean"
"""
Constant describing the type of a textual content that is a boolean (``true``
or ``false`` textual value).

Type: :class:`unicode`
"""

INTEGER = u"Integer"
"""
Constant describing the type of a textual content that is an integer.

Type: :class:`unicode`
"""

FLOAT = u"Float"
"""
Constant describing the type of a textual content that is a real (float).
The ``.`` character is the separator between integer and decimal parts.

Type: :class:`unicode`
"""

STRING = u"String"
"""
Constant describing the type of a textual content that is a string (text).

Type: :class:`unicode`
"""

DATETIME = u"DateTime"
"""
Constant describing the type of a textual content that is a date, a
time or a date-time. The text representation of a date-time is defined in the
XML Schema standard.

Type: :class:`unicode`
"""

DURATION = u"Duration"
"""
Constant describing the type of a textual content that is a duration between
two dates-times. The text representation of a duration is defined in the
XML Schema standard.

Type: :class:`unicode`
"""

BASE64 = u"Base64"
"""
Constant describing the type of a textual content that is a binary content
coded in base 64.

Type: :class:`unicode`
"""

HEXA = u"Hexadecimal"
"""
Constant describing the type of a textual content that is a binary content
coded in hexadecimal.

Type: :class:`unicode`
"""

EMPTY = u"Empty"
TEXT_ONLY = u"Text only"
ELEMENTS_ONLY = u"Elements only"

ABSENT = u"Absent item"
DIFFERENT = u"Different item"
SAME = u"Same item"

DTD = u"DTD"
XML_SCHEMA = u"XML Schema"


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
    return name[name.find('{') + 1:name.find('}')], name[name.find('}') + 1:]
