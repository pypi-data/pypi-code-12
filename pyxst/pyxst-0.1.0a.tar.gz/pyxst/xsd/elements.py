# -*- coding: utf-8 -*-
"""
This module defines the classes that represent the elements read in an XML
Schema.

The elements are defined as a specific node derived from
:class:`~pyxst.xml_struct.xsd.utils.XsdNode`.

.. autoclass:: XsdElement
   :members:
   :undoc-members:
   :show-inheritance: 
"""
__docformat__ = "restructuredtext en"


from .errors import XsdError
from .utils import XsdNode, ELEMENT


class XsdElement(XsdNode):
    """
    Class representing an element defined in an XML Schema.

    .. attribute:: xsd_type 

       Type of this element declared in the XML Schema. This type is a
       type node. The type of an element can be left undefined
       when creating the element and defined later. When the XML Schema has
       been read, all the elements must have a type.

       Type: :class:`~pyxst.xml_struct.xsd.types.XsdType`

    .. attribute:: _elts_with_same_type

       Private attribute used to temporarly store other elements that
       have the same type as this element. When the type of this
       element is defined, it must also be given to all these other
       elements. At the end of the building step, this attribute is empty as
       each element directly points to its type.

       Type: List of 
       :class:`~pyxst.xml_struct.xsd.elements.XsdElement`

    For this class, the ``category`` class attribute is set to ``ELEMENT``.

    .. automethod:: __init__
    """
    category = ELEMENT

    def __init__(self, name, uid_prefix=u""):
        """
        Initializes a new element node.

        :param name:
            Name of the element.
        :type name:
            :class:`unicode`
        """
        super(XsdElement, self).__init__(name, uid_prefix=uid_prefix)
        self.xsd_type = None
        self._elts_with_same_type = []
