# -*- coding: utf-8 -*-


from .errors import DtdError
from .utils import DtdNode, DtdUsage
from .constants import ELEMENT, ATTRIBUTE


class DtdElement(DtdNode):
    """
    Class representing an element defined in a DTD.
    """
    category = ELEMENT

    def __init__(self, name, uid_prefix=u""):
        super(DtdElement, self).__init__(name, uid_prefix=uid_prefix)
        self.attributes = {}
        self.content_type = None
        self.sub_content = None

    def add_attribute(self, attr, min_occur=1, max_occur=1):
        """
        Adds the ``attr`` attribute to the element.

        This method checks that ``attr`` category is ``ATTRIBUTE``, that
        max_occur is never greater than 1 and that there is not already an
        attribute with the same identifier in this element.
        """
        if not attr.category is ATTRIBUTE:
            raise DtdError(u"Can't add {0} to {1} as attribute"
                           u"".format(attr, self))
        if attr.uid in self.attributes:
            raise DtdError(u"{0} already declared in {1}".format(attr, self))
        if max_occur > 1:
            raise DtdError(u"{0} can't occur more than one time in {1}"
                           u"".format(attr, self))
        self.attributes[attr.uid] = DtdUsage(attr, min_occur, max_occur)


class DtdAttribute(DtdNode):
    """
    Class representing an attribute defined in an XML Schema.
    """
    category = ATTRIBUTE

    def __init__(self, name, uid_prefix=u""):
        super(DtdAttribute, self).__init__(name, uid_prefix=uid_prefix)
        self.dtd_type = None
        self.fixed_value = False
        self.default_value = None
        self.possible_values = None

    @property
    def uid(self):
        return u"{0}/@{1}".format(self.uid_prefix, self.name)
