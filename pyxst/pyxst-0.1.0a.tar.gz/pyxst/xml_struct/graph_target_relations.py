# -*- coding: utf-8 -*-
"""
This module contains the classes that represent relations between XML
elements of the graph that can be translated in some arKItect
concepts. It also contains the function that creates these relations in
the graph decribing the XML structure by analyzing the structure of XML
elements.

The graph that describes the XML structure is a
:class:`pyxst.xml_struct.graph.XMLGraph` object. It
contains several nodes including XML elements that come from the
:mod:`pyxst.xml_struct.graph_nodes` module.

.. autoclass:: TargetRelation
   :members:
   :undoc-members:
   :show-inheritance: 

.. autoclass:: IsParentOf
   :members:
   :undoc-members:
   :show-inheritance: 

.. autoclass:: HasAttribute
   :members:
   :undoc-members:
   :show-inheritance: 

.. autoclass:: HasListAttribute
   :members:
   :undoc-members:
   :show-inheritance: 

.. autodata:: RELATION_CLASS

.. autodata:: IS_PARENT_OF
.. autodata:: HAS_ATTRIBUTE
.. autodata:: HAS_LIST_ATTRIBUTE

.. autofunction:: weave_target_relations

.. autofunction:: build_relations_in_group
"""
__docformat__ = "restructuredtext en"


from .utils import MIXED, INFINITY
from .graph_nodes import Group


class TargetRelation(object):
    """
    Abstract class that describes a target relation between two nodes
    of the graph (XML elements or XML attributes).

    .. attribute:: start

       Node where the relation starts from.

       Type: :class:`~pyxst.xml_struct.graph_nodes.XMLNode`

    .. attribute:: end

       Node where the relation ends to.

       Type: :class:`~pyxst.xml_struct.graph_nodes.XMLNode`
 
    .. attribute:: DESC

       Class attribute containing the textual description of the relation 
       that will be used to display the text representation of this object.

       Type: :class:`str`
    """
    DESC = "%s is in relation with %s"

    def __init__(self, start_node, end_node):
        """
        Initializes a new target relation between two graph nodes.

        :param start_node:
            Node where the relation starts from.
        :type start_node:
            :class:`~pyxst.xml_struct.graph_nodes.XMLNode`
        :param end_node:
            Node where the relation ends to.
        :type end_node:
            :class:`~pyxst.xml_struct.graph_nodes.XMLNode`
        """
        self.start = start_node
        self.end = end_node
        if self.__class__ is TargetRelation:
            raise NotImplementedError("Abstract classes can't be instantiated")

    def __repr__(self):
        """
        Returns a string representation of the object.

        Uses ``DESC`` class attribute to build this representation.

        :returns:
            Text representation of the object.
        :rtype:
            :class:`str`
        """
        return self.DESC % (self.start, self.end)


class IsParentOf(TargetRelation):
    """
    Target relation that describes an XML element will be the parent of another
    XML element in the target structure in arKItect.
    """
    DESC = "%s is parent of %s"


class HasAttribute(TargetRelation):
    """
    Target relation that describes an XML element will have an XML element
    or an XML attribute as an attribute in the target structure in arKItect.
    """
    DESC = "%s has %s as attribute"


class HasListAttribute(TargetRelation):
    DESC = "%s has %s as list attribute"


IS_PARENT_OF = "IsParentOf Relation"
"""
Constant describing the "IsParentOf" relation.

Type: :class:`str`
"""

HAS_ATTRIBUTE = "HasAttribute Relation"
"""
Constant describing the "HasAttribute" relation.

Type: :class:`str`
"""

HAS_LIST_ATTRIBUTE = "HasListAttribute Relation"
"""
Constant describing the "HasListAttribute" relation.

Type: :class:`str`
"""

RELATION_CLASS = {IS_PARENT_OF: IsParentOf,
                  HAS_ATTRIBUTE: HasAttribute,
                  HAS_LIST_ATTRIBUTE: HasListAttribute,
                  }
"""
Dictionary mapping the names of the target relations with the classes that
represent them.

Type: :class:`dict` of :class:`class` indexed with :class:`str`
"""


def weave_target_relations(graph):
    """
    Function that creates target relations between the nodes of the graph
    that describes the XML structure.

    Target relations describe relations that can be translated into
    arKItect concepts:

    * "has attribute" between an XML element and an XML attribute or
      between an XML element and an XML sub-element that contains
      textual data and no attribute;

    * "has list attribute" between an XML element and an XML attribute
      that contains a list of values or between an XML element and an
      XML sub-element that contains textual data and no attribute but
      can occur several times or between an XML element and an XML
      sub-element that contains a textual list of values and no attribute;

    * "is parent of" between an XML element and an XML sub-element that 
      contains mixed content or sub-elements.

    :param graph:
        Graph that decribes the XML structure. The target relations will be
        created inside this graph between the graph nodes.
    :type graph:
        :class:`~pyxst.xml_struct.graph.XMLGraph`
    """
    for elt in graph.elements:
        for occur in elt.attributes.values():
            attr = occur.target
            if attr.textual_content_is_list:
                graph.add_target_relation(HAS_LIST_ATTRIBUTE, elt, attr)
            else:
                graph.add_target_relation(HAS_ATTRIBUTE, elt, attr)
        if elt.content is not None:
            grp = elt.content.target
            grp_min = elt.content.minimum
            grp_max = elt.content.maximum
            build_relations_in_group(graph, elt, grp, grp_max)


def build_relations_in_group(graph, parent_elt, grp, grp_max):
    """
    Private function that builds the target relations between a parent element
    and the sub-elements that occur inside a group.

    As groups can contain sub-groups, this function can be recursively called
    in order to completely process the sub-content of the parent element.

    This function should not be directly called. Use ``weave_target_relations``
    function instead.

    :param graph:
        Graph where the target relations are weaved in.
    :type graph:
        :class:`~pyxst.xml_struct.graph.XMLGraph`
    :param parent_elt:
        XML Element where the considered group is defined. This element will
        be the starting point of the target relations.
    :type parent_elt:
        :class:`~pyxst.xml_struct.graph_nodes.XMLElement`
    :param grp:
        Group that contains the sub-elements of ``parent_elt``. This group
        might also contain sub-groups that contain the sub-elements.
    :type grp:
        :class:`~pyxst.xml_struct.graph_nodes.Group`
    :param grp_max:
        Maximum occurence of the ``grp`` group. This maximum occurence has been
        cumulated since the reading of ``parent_elt`` content.
    :type grp_max:
        :class:`int` or :data:`~pyxst.xml_struct.utils.INFINITY`
    """
    for occur in grp.children:
        sub_item = occur.target
        if occur.maximum == INFINITY or grp_max == INFINITY:
            sub_max = INFINITY
        else:
            sub_max = occur.maximum * grp_max
        if isinstance(sub_item, Group):
            build_relations_in_group(graph, parent_elt, sub_item, sub_max)
        else:
            if sub_item.textual_content_type in [None, MIXED] or \
                    len(sub_item.attributes) > 0:
                graph.add_target_relation(IS_PARENT_OF, parent_elt, sub_item)
            elif sub_item.textual_content_is_list:
                graph.add_target_relation(HAS_LIST_ATTRIBUTE, 
                                          parent_elt, sub_item)
            elif sub_max == INFINITY or sub_max > 1:
                graph.add_target_relation(HAS_LIST_ATTRIBUTE, 
                                          parent_elt, sub_item)
            else:
                graph.add_target_relation(HAS_ATTRIBUTE, parent_elt, sub_item)
