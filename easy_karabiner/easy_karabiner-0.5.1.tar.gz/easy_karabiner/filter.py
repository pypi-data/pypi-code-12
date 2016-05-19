# -*- coding: utf-8 -*-
from __future__ import print_function
from .basexml import BaseXML


class FilterBase(BaseXML):
    """A object represent filter XML node in Karabiner.
    For example, the following XML is a typical filter.

        <only>SKIM</only>
    """
    def __init__(self, *vals, **kwargs):
        """
        :param vals: List[str]
        :param kwargs: Dict
        """
        self.type = kwargs.get('type', 'only')
        self.vals = vals
        self.kwargs = kwargs

    def get_vals(self):
        return self.vals

    def get_tag_name(self):
        header = self.get_class_name().lower().rsplit('filter', 1)[0]
        tag_name = '%s_%s' % (header, self.type)
        return tag_name

    def to_xml(self):
        xml_tree = self.create_tag(self.get_tag_name())
        text = ',\n'.join(self.get_vals())
        self.assign_text_attribute(xml_tree, text)
        return xml_tree

    def __add__(self, another):
        if self.get_tag_name() == another.get_tag_name():
            self.vals += another.vals
            return self
        else:
            tagname1 = self.get_tag_name()
            tagname2 = another.get_tag_name()
            errmsg = "Cannot add %s with %s" % (tagname1, tagname2)
            raise TypeError(errmsg)

    @property
    def id(self):
        return self.get_tag_name(), tuple(sorted(self.get_vals()))

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.id == other.id


class Filter(FilterBase):
    """
    >>> print(Filter('SKIM'))
    <only>SKIM</only>
    >>> print(Filter('SKIM', type='not'))
    <not>SKIM</not>
    """

    def get_tag_name(self):
        return self.type


class ReplacementFilter(Filter):
    pass


class DeviceFilter(FilterBase):
    def get_tag_name(self):
        tag_name = 'device_%s' % self.type
        return tag_name


class DeviceProductFilter(DeviceFilter):
    pass


class DeviceVendorFilter(DeviceFilter):
    pass


class WindowNameFilter(FilterBase):
    pass


class UIElementRoleFilter(FilterBase):
    pass


class InputSourceFilter(FilterBase):
    pass


class ModifierFilter(FilterBase):
    def get_tag_name(self):
        tag_name = 'modifier_%s' % self.type
        return tag_name


if __name__ == "__main__":
    import doctest
    doctest.testmod()
