# -*- coding: utf-8 -*-
from __future__ import print_function
from . import __version__
from . import parse
from .basexml import BaseXML


class Generator(BaseXML):
    """Construct Karabiner favorite XML tree

    >>> g = Generator()
    >>> s = '''
    ...     <root>
    ...       <Easy-Karabiner>{version}</Easy-Karabiner>
    ...       <item>
    ...         <name>Easy-Karabiner</name>
    ...         <item>
    ...           <name>Enable</name>
    ...           <identifier>private.easy_karabiner</identifier>
    ...         </item>
    ...       </item>
    ...     </root>
    ...     '''.format(version=__version__)
    >>> util.assert_xml_equal(g, s)
    """

    ITEM_IDENTIFIER = 'private.easy_karabiner'

    def __init__(self, maps=None, definitions=None):
        self.maps = maps or []
        self.definitions = definitions or {}

    def init_xml_tree(self, xml_root):
        """
            <Easy-Karabiner>{version}</Easy-Karabiner>
            <item>
                <name>Easy-Karabiner</name>
                <!-- REMAIN NODES HERE -->
            </item>
        """
        version_tag = BaseXML.create_tag('Easy-Karabiner', __version__)
        item_tag = BaseXML.create_tag('item')
        item_tag.append(BaseXML.create_tag('name', 'Easy-Karabiner'))
        xml_root.append(version_tag)
        xml_root.append(item_tag)
        return item_tag

    def init_subitem_tag(self, item_tag):
        """
        <item>
            <name>Easy-Karabiner</name>
            <item>
                <name>Enable</name>
                <identifier>private.easy_karabiner</identifier>
                <!-- REMAIN NODES HERE -->
            </item>
        </item>
        """
        subitem_tag = BaseXML.create_tag('item')
        name_tag = BaseXML.create_tag('name', 'Enable')
        identifier_tag = BaseXML.create_tag('identifier', self.ITEM_IDENTIFIER)
        item_tag.append(subitem_tag)
        subitem_tag.append(name_tag)
        subitem_tag.append(identifier_tag)
        return subitem_tag

    def to_xml(self):
        blocks, definitions = parse.parse(self.maps, self.definitions)

        # construct XML tree
        xml_tree = BaseXML.create_tag('root')

        item_tag = self.init_xml_tree(xml_tree)
        for definition in definitions:
            item_tag.append(definition.to_xml())

        subitem_tag = self.init_subitem_tag(item_tag)
        for block in blocks:
            subitem_tag.append(block.to_xml())

        return xml_tree


if __name__ == '__main__':
    import doctest
    from . import util
    doctest.testmod(extraglobs={
        '__version__': __version__,
        'util': util,
    })
