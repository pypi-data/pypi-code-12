# -*- coding: utf-8 -*-
from __future__ import print_function
from . import exception
from . import def_tag_map
from .basexml import BaseXML


class DefinitionBase(BaseXML):
    """A object represent definition XML node in Karabiner.
    For example, the following XML is a typical definition.

        <appdef>
          <appname>BILIBILI</appname>
          <equal>com.typcn.Bilibili</equal>
        </appdef>
    """
    def __init__(self, name, *tag_vals, **kwargs):
        self.name = name
        self.tag_vals = tag_vals
        self.kwargs = kwargs

    def get_name(self):
        return self.name

    @classmethod
    def get_def_tag_name(cls):
        return '%sdef' % cls.get_class_name().lower()

    @classmethod
    def get_name_tag_name(cls):
        return def_tag_map.get_name_tag_name(cls.get_def_tag_name())

    def get_tag_val_pair(self, val):
        raise exception.NeedOverrideError()

    def get_tag_val_pairs(self, tag_vals):
        return [self.get_tag_val_pair(tag_val) for tag_val in tag_vals]

    @classmethod
    def split_name_and_attrs(cls, tag_name):
        """Because some tag names contain attributes,
        so we need separate it into two parts.
        """
        # transform `key="value"` to `(key, value)`
        def to_pair(s):
            removed_quote = ''.join(ch for ch in s if ch not in ('"', "'"))
            return removed_quote.split('=')

        name_parts = tag_name.split()
        name = name_parts[0]
        raw_attrs = [w for w in name_parts if "=" in w]
        tag_attrs = dict(to_pair(w) for w in raw_attrs)
        return name, tag_attrs

    def to_xml(self):
        xml_tree = self.create_tag(self.get_def_tag_name())
        name_tag = self.create_tag(self.get_name_tag_name(), self.name)
        xml_tree.append(name_tag)

        tag_val_pairs = self.get_tag_val_pairs(self.tag_vals)

        for tag_name, tag_val in tag_val_pairs:
            if len(tag_name) > 0:
                tag_name, tag_attrs = self.split_name_and_attrs(tag_name)
                tag = self.create_tag(tag_name, tag_val, attrib=tag_attrs)
                xml_tree.append(tag)

        return xml_tree

    @property
    def id(self):
        return self.get_def_tag_name(), self.get_name()

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id


class NoNameTagDefinitionBase(DefinitionBase):
    def to_xml(self):
        xml_tree = self.create_tag(self.get_def_tag_name(), self.name)
        return xml_tree


class App(DefinitionBase):
    """
    >>> d = App('BILIBILI', 'com.typcn.Bilibili')
    >>> s = '''
    ...     <appdef>
    ...       <appname>BILIBILI</appname>
    ...       <equal>com.typcn.Bilibili</equal>
    ...     </appdef>
    ...     '''
    >>> util.assert_xml_equal(d, s)
    """

    def get_tag_val_pair(self, val):
        if len(val) == 0:
            return ()
        if val[0] == '.':
            return ('suffix', val)
        elif val[-1] == '.':
            return ('prefix', val)
        else:
            return ('equal', val)


class WindowName(DefinitionBase):
    def get_tag_val_pair(self, val):
        return ('regex', val)


class DeviceVendor(DefinitionBase):
    def get_tag_val_pair(self, val):
        return ('vendorid', val)


class DeviceProduct(DefinitionBase):
    def get_tag_val_pair(self, val):
        return ('productid', val)


class InputSource(DefinitionBase):
    @classmethod
    def is_host(cls, val):
        parts = val.split('.')
        return len(parts) >= 3 and all(len(part) for part in parts)

    def get_tag_val_pair(self, val):
        if len(val) == 0:
            return ()
        if val[-1] == '.':
            return ('inputsourceid_prefix', val[:-1])
        elif self.is_host(val):
            return ('inputsourceid_equal', val)
        else:
            return ('languagecode', val)


class VKChangeInputSource(InputSource):
    pass


class VKOpenURL(DefinitionBase):
    def get_tag_val_pair(self, val):
        if len(val) == 0:
            return ()
        elif val.startswith('/'):
            return ('url type="file"', val)
        elif val.startswith('#!'):
            if val.startswith('#! '):
                val = val[3:]
            script = self.create_cdata_text(val)
            return ('url type="shell"', script)
        else:
            return ('url', val)

    def to_xml(self):
        xml_tree = super(VKOpenURL, self).to_xml()
        if self.kwargs.get('background', False):
            background_tag = self.create_tag('background')
            xml_tree.append(background_tag)
        return xml_tree


class Replacement(DefinitionBase):
    def get_tag_val_pair(self, val):
        return ('replacementvalue', val)

    def get_tag_val_pairs(self, tag_vals):
        vals = []

        for tag_val in tag_vals:
            val = tag_val.strip()
            if self.is_cdata_text(val):
                val = self.create_cdata_text(self.remove_cdata_mark(val))
            else:
                val = tag_val

            vals.append(val)

        return [self.get_tag_val_pair(', '.join(vals))]


class UIElementRole(NoNameTagDefinitionBase):
    pass


class Modifier(NoNameTagDefinitionBase):
    pass


if __name__ == "__main__":
    import doctest
    from . import util
    doctest.testmod(extraglobs={'util': util})
