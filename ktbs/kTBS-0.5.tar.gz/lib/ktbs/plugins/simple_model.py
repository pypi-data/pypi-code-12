# -*- coding: utf-8 -*-
#    This file is part of KTBS <http://liris.cnrs.fr/sbt-dev/ktbs>
#    Copyright (C) 2011-2012 Pierre-Antoine Champin <pchampin@liris.cnrs.fr> /
#    Universite de Lyon <http://www.universite-lyon.fr>
#
#    KTBS is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    KTBS is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with KTBS.  If not, see <http://www.gnu.org/licenses/>.

"""
Simple syntax for trace models
"""
from pyparsing import *
from re import U

def parse_simple_model(txt):
    return SIMPLE_MODEL.parseString(txt, True)

COMMENT = Suppress("'") + Regex(r"[^\n]*", U) + Suppress(LineEnd())
LABEL = Group(
    Suppress(Regex("'\w*")) + Word(alphas)("lang")
    + Suppress(Regex(r"\w*:\w*")) + Regex(r"[^\n]*", U)("value")
    + Suppress(LineEnd())
    )
URI = Suppress("<") + Regex(r"[^>]*", U) + Suppress(">")
TYPEID = Regex(r"[a-zA-Z_][\w\d_-]*", U)
INDENT = (LineStart() + Suppress(Regex(r"\s+", U))).leaveWhitespace()

UNIT = (Suppress("unit") + Suppress(":") + TYPEID)
UNIT.setParseAction(lambda x: x[0])

SUPER = Group(
    Suppress("(")
    + TYPEID("local") | URI("uri")
    + ZeroOrMore( Suppress(",") + TYPEID )
    )

ATYPE = Group(
    INDENT + TYPEID("id") + Suppress(":") + Group(
        TYPEID("xsd") | URI("uri")
        )("type")
    + Suppress(LineEnd())
    + ZeroOrMore(INDENT + LABEL)("labels")
    + ZeroOrMore(INDENT + COMMENT)("description")
    )

RTYPE = Group(
    INDENT + TYPEID("id")
    + Optional(SUPER)("supertypes") + Suppress("->") + (
        TYPEID("local") | URI("uri")
        )("target")
    + Suppress(LineEnd())
    + ZeroOrMore(INDENT + LABEL)("labels")
    + ZeroOrMore(INDENT + COMMENT)("description")
    )
    
OTYPE = Group(
    LineStart()+ TYPEID("id") + Optional(SUPER)("supertypes")
    + Suppress(LineEnd())
    + ZeroOrMore(LABEL("labels*")).leaveWhitespace()
    + ZeroOrMore(COMMENT)("description").leaveWhitespace()
    + ZeroOrMore(ATYPE("attributes*"))
    + ZeroOrMore(RTYPE("relations*"))
    )

SIMPLE_MODEL = (
    Suppress(ZeroOrMore(COMMENT))
    + Optional(UNIT("unit"))
    + Suppress(ZeroOrMore(COMMENT))
    + ZeroOrMore(
        OTYPE("otypes*")
        + Suppress(ZeroOrMore(COMMENT))
        )
    )

# TODO move this to unit tests

def test_empty():
    tree = parse_simple_model(u"")
    assert tree.unit == ""
    assert len(tree.otypes) == 0

def assert_good_model(tree):
    assert tree.unit == "millisecond", tree.unit
    #assert len(tree.otypes) == 2, len(tree.otypes)
    assert tree.otypes[0].id == "Event"
    assert len(tree.otypes[0].super) == 0
    assert len(tree.otypes[0].attributes) == 1
    assert tree.otypes[0].attributes[0].id == "component"
    assert tree.otypes[0].attributes[0].type.xsd == "string"
    assert tree.ottypes[1].id == "Click"
    assert len(tree.otypes[1].super) == 1
    assert tree.otypes[1].super[0].id == "Event"
    assert len(tree.otypes[1].attributes) == 3
    assert tree.otypes[1].attributes[0].id == "x"
    assert tree.otypes[1].attributes[0].type.xsd == "integer"
    assert tree.otypes[1].attributes[1].id == "y"
    assert tree.otypes[1].attributes[1].type.xsd == "integer"
    assert tree.otypes[1].attributes[2].id == "button"
    assert tree.otypes[1].attributes[2].type.xsd == "integer"
    assert len(tree.otypes[1].relations) == 1
    assert tree.otypes[1].relations[0].id == "related"
    assert tree.otypes[1].relations[0].type.xsd == "integer"

def test_without_comments():
    tree = parse_simple_model(u"""

unit: millisecond

Event
  component: string

Click (Event)

  x: integer
  y: integer

  button: integer

  related -> Event
    """)
    assert_good_model(tree)

def test_with_comments():
    parse_simple_model(u"""

unit: millisecond

Event
' fr: événement
' a GUI even
  component: string
  ' the xpath of the target component of this event

Click (Event)
' fr: clic
' a mouse click

  x: integer
  ' the x-coordinate of the click (on the screen)
  y: integer
  ' the x-coordinate of the click (on the screen)

  button: integer
  ' the number of the button that
  ' has been clicked

  related -> Event
  ' a related event
  ' (e.g. MouseDown and MouseUp)
    """)
    assert_good_model(tree)
    # TODO check labels and descriptions

def test_with_uri():
    tree = parse_simple_model("""
Foo (<http://example.org/Thing)
""")
    assert tree.otypes[0].supertypes[0].uri == "http://example.org/Thing"

def test_ko():
    try:
        parse_simple_model(u"""1""")
        assert 0, "ParseException expected"
    except ParseException:
        pass


# TODO remove

tree = SIMPLE_MODEL.parseString(u"""

unit: millisecond


Event
' fr : bla
  component: string
  ' comp
  a: int

Click (Event)

  x: integer
  y: integer

  button: integer

  related -> Event
    """)

print tree.asXML()
#assert_good_model(tree)
