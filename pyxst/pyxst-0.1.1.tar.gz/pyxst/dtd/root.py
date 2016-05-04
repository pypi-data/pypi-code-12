# -*- coding: utf-8 -*-
"""
This module defines the class where the data read from a DTD will be stored.

.. autoclass:: DtdDefinition
   :show-inheritance: 
"""
__docformat__ = "restructuredtext en"


from .constants import ELEMENT


class DtdDefinition(object):
    """
    Class representing a DTD.

    This class stores the elements with their attributes and their sub-content.
    """
    def __init__(self):
        self.elements = {}

    def add_element(self, elt):
        """
        Adds an element described by a declaration from the DTD.

        This method checks that ``elt`` category is ``ELEMENT`` and that
        there is not already an element with the same identifier in this DTD.

        :param elt:
            Element to be stored ib the DTD.
        :type elt_decl:
            :class:`~dtd.nodes.Element`
        """
        if not elt.category is ELEMENT:
            raise DtdError(u"Can't add {0} to {1} as an element"
                           u"".format(attr, self))
        if elt.uid in self.elements:
            raise DtdError(u"{0} already declared in the DTD".format(elt_name))
        self.elements[elt.uid] = elt

