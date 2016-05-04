# -*- coding: utf-8 -*-

ATTRIBUTE = u"Attribute"
"""
Constant containing the category of the attribute nodes

Type: :class:`unicode`
"""

ELEMENT = u"Element"
"""
Constant containing the category of the element nodes

Type: :class:`unicode`
"""

GROUP = u"Group"
"""
Constant containing the category of the group nodes

Type: :class:`unicode`
"""

INFINITY = u"infinity"
"""
Constant describing the infinity (for unbounded occurences).

Type: :class:`unicode`
"""

EMPTY = u"Empty"
"""
Constant describing the type of the content that can occur inside an element
if this element contain nothing.

Type: :class:`unicode`
"""

ELEMENTS_ONLY = u"Elements only"
"""
Constant describing the type of the content that can occur inside an element
if this element contain only sub-elements.

Type: :class:`unicode`
"""

TEXT_ONLY = u"Text only"
"""
Constant describing the type of the content that can occur inside an element
if this element contain only text data.

Type: :class:`unicode`
"""

MIXED = u"Mixed Content"
"""
Constant describing the type of the content that can occur inside an element
if this element can contain, at the same time, sub-elements and textual data.

Type: :class:`unicode`
"""

ANY = u"Any text or element"
"""
Constant describing the type of the content that can occur inside an element
if this element can contain anything (any text data and any elements).

Type: :class:`unicode`
"""
