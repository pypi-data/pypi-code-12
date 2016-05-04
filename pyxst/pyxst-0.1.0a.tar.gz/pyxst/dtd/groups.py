# -*- coding: utf-8 -*-

from .errors import DtdError
from .utils import DtdNode, DtdUsage
from .constants import GROUP, ELEMENT


class DtdGroup(DtdNode):
    """
    Abstract class representing a group defined in a DTD.

    Two different groups can be defined: *choices* and *sequences*.
    A choice group defines several options from where one item must be chosen,
    a sequence group defines a sequence of items where the order matters.

    For this class, the ``category`` class attribute is set to ``GROUP``.
    """
    category = GROUP

    def __init__(self, name, uid_prefix=u""):
        super(DtdGroup, self).__init__(name, uid_prefix=uid_prefix)
        if self.__class__ is DtdGroup:
            raise NotImplementedError(u"Can't instantiate an abstract class")

    def add_item(self, item, min_occur=1, max_occur=1):
        raise NotImplementedError(u"Can't call abstract operations")

    def __len__(self):
        raise NotImplementedError(u"Can't call abstract operations")

    def __iter__(self):
        raise NotImplementedError(u"Can't call abstract operations")


class DtdChoice(DtdGroup):
    """
    Class representing a *choice* group defined in a DTD.

    A choice group defines several options from where one item must be chosen.
    """
    def __init__(self, name, uid_prefix=u""):
        super(DtdChoice, self).__init__(name, uid_prefix=uid_prefix)
        self.options = []
        self.option_ids = set()

    def add_item(self, item, min_occur=1, max_occur=1):
        """
        Adds the ``item`` item as one option into the *choice* group.

        This method checks that ``item`` category is ``ELEMENT`` or ``GROUP``,
        and that no other item with the same identifier exists in the group.
        """
        if item.category not in (ELEMENT, GROUP):
            raise DtdError("Can't add %s to %s (should be an element or a "
                           "group)" % (item, self))
        if item.uid in self.option_ids:
            raise DtdError("%s already declared in %s" % (item, self))
        self.option_ids.add(item.uid)
        self.options.append(DtdUsage(item, min_occur, max_occur))

    def __len__(self):
        return len(self.options)

    def __iter__(self):
        return iter(self.options)


class DtdSequence(DtdGroup):
    """
    Class representing a *choice* group defined in a DTD.

    A sequence group defines a sequence of items where the order
    matters.
    """
    def __init__(self, name, uid_prefix=u""):
        super(DtdSequence, self).__init__(name, uid_prefix=uid_prefix)
        self.children = []

    def add_item(self, item, min_occur=1, max_occur=1):
        """
        Adds the ``item`` item as one sub-item of the *sequence* group. The
        item is added at the end of the sequence.

        This method checks that ``item`` category is ``ELEMENT`` or ``GROUP``.
        """
        if item.category not in (ELEMENT, GROUP):
            raise DtdError("Can't add %s to %s (should be an element or a "
                           "group)" % (item, self))
        self.children.append(DtdUsage(item, min_occur, max_occur))

    def __len__(self):
        return len(self.children)

    def __iter__(self):
        return iter(self.children)
