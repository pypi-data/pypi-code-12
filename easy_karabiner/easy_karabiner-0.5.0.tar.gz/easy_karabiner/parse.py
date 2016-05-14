# -*- coding: utf-8 -*-
from __future__ import print_function
from collections import OrderedDict
from operator import add
from functools import reduce

from . import util
from . import query
from . import osxkit
from . import factory
from . import exception
from .basexml import BaseXML


def parse(maps, definitions):
    """Parse and convert user Easy-Karabiner config to XML objects."""
    definitions = util.encode_with_utf8(definitions)
    maps = util.encode_with_utf8(maps)

    factory.create_definitions(definitions)
    filters_keymaps_table = organize_maps(maps)
    block_objs = create_blocks(filters_keymaps_table)

    definition_objs = query.DefinitionBucket.get_all_definitions()
    return block_objs, definition_objs


def organize_maps(maps):
    """Convert `maps` to a `OrderedDict` with the consistent type.
    The items in `filters_keymaps_table` is ordered by the first present of `filters`.
    """
    filters_keymaps_table = OrderedDict()

    for raw_map in maps:
        if util.is_list_or_tuple(raw_map) and len(raw_map) > 0:
            try:
                raw_keymap, raw_filters = separate_keymap_filters(raw_map)
                filters_keymaps_table.setdefault(raw_filters, []).append(raw_keymap)
            except exception.ConfigWarning as e:
                exception.ExceptionRegister.record(raw_map, e)
            else:
                if raw_filters:
                    exception.ExceptionRegister.put(raw_filters, raw_map)
                if raw_keymap:
                    exception.ExceptionRegister.put(raw_keymap, raw_map)
        else:
            raise exception.ConfigError('Map must be a list: %s' % raw_map.__repr__())

    return filters_keymaps_table


def separate_keymap_filters(raw_map):
    """Convert `raw_map` to a `tuple` with consistent type."""
    # if last element in `raw_map` is a filter
    if util.is_list_or_tuple(raw_map[-1]):
        raw_filters = tuple(raw_map[-1])
        raw_map = raw_map[:-1]
    else:
        raw_filters = tuple()

    if len(raw_map) == 0 or len(raw_map[0]) == 0:
        raise exception.ConfigWarning("Cannot found keymap")
    else:
        # if first part in `raw_map` is command marker
        if len(raw_map[0]) > 2 and raw_map[0].startswith('_') and raw_map[0].endswith('_'):
            command = raw_map[0]
            raw_keycombos = raw_map[1:]
        else:
            command = '__KeyToKey__'
            raw_keycombos = raw_map

        # ((key1, key2, ...), (key1, key2, ...))
        keycombos = []
        for keycombo_str in raw_keycombos:
            if factory.DefinitionDetector.is_vkopenurl(keycombo_str) or osxkit.get_app_info(keycombo_str):
                keycombos.append((keycombo_str,))
            else:
                keycombos.append(tuple(util.split_ignore_quote(keycombo_str)))

        raw_keymap = (command,) + tuple(keycombos)
        return raw_keymap, raw_filters


def create_blocks(filters_keymaps_table):
    tmp = OrderedDict()

    for raw_filters in filters_keymaps_table:
        raw_keymaps = filters_keymaps_table[raw_filters]

        try:
            factory.define_filters(raw_filters)
            factory.define_keymaps(raw_keymaps)

            filter_objs = factory.create_filters(raw_filters)
            keymap_objs = factory.create_keymaps(raw_keymaps)
            tmp.setdefault(filter_objs, []).append(keymap_objs)
        except exception.UndefinedFilterException as e:
            exception.ExceptionRegister.record_by(raw_filters, e)

    blocks = []
    for filter_objs in tmp:
        keymap_objs = reduce(add, tmp[filter_objs])
        block = Block(keymap_objs, filter_objs)
        blocks.append(block)
    return blocks


class Block(BaseXML):
    """Block is a kind of XML node similar to `item` in Karabiner.
    For example, the following XML is a typical `block`.

        <block>
            <only>VIRTUALMACHINE</only>
            <autogen> __KeyToKey__
                KeyCode::F, ModifierFlag::CONTROL_L, ModifierFlag::COMMAND_L, ModifierFlag::NONE,
                KeyCode::F, ModifierFlag::COMMAND_L
            </autogen>
        </block>
    """
    def __init__(self, keymaps, filters=None):
        self.keymaps = keymaps
        self.filters = filters or tuple()

    def to_xml(self):
        xml_tree = self.create_tag('block')

        for f in self.filters:
            xml_tree.append(f.to_xml())
        for k in self.keymaps:
            xml_tree.append(k.to_xml())

        return xml_tree
