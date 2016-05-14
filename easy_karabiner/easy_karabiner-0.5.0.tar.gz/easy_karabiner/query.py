# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import glob
from itertools import chain
from . import alias
from . import config
from . import exception
from . import definition
from . import def_tag_map
from .basexml import BaseXML


def is_defined_filter(val):
    return query_filter_class_names(val, scope='all')


def is_defined_key(val):
    if get_key_alias(val.lower()):
        return True
    else:
        for k in [val, val.upper(), val.lower()]:
            if KeyHeaderQuery.query(k):
                return True

    return DefinitionBucket.has('key', val)


def is_predefined_modifier(key):
    key = get_key_alias(key.lower()) or key

    for k in [key, key.upper(), key.lower()]:
        if KeyHeaderQuery.query(k) == 'ModifierFlag':
            return True

    parts = key.split('::', 1)
    return len(parts) == 2 and parts[0] == 'ModifierFlag'


def query_filter_class_names(value, scope='all'):
    """Get `Filter` class name by `value` in `scope`."""
    definitions = DefinitionBucket.get('filter', value)
    def_tag_name = DefinitionTypeQuery.query(value)
    filter_class_names = []

    if scope in ('all', 'user') and definitions:
        for d in definitions:
            filter_class_name = def_tag_map.get_filter_class_name(d.get_def_tag_name())
            if filter_class_name:
                filter_class_names.append(filter_class_name)
            else:
                return []
    elif scope in ('all', 'predefined'):
        if not def_tag_name:
            if is_predefined_modifier(value):
                def_tag_name = definition.Modifier.get_def_tag_name()
            else:
                return []

        filter_class_name = def_tag_map.get_filter_class_name(def_tag_name)
        if filter_class_name:
            filter_class_names.append(filter_class_name)

    return filter_class_names


def get_def_alias(value):
    return alias.get_alias('DEF_ALIAS', value)


def get_key_alias(value):
    return alias.get_alias('KEY_ALIAS', value)


def get_keymap_alias(value):
    return alias.get_alias('KEYMAP_ALIAS', value)


def update_aliases(aliases_table):
    alias.update_aliases(aliases_table)


class BaseTypeQuery(object):
    """This class is used to get corresponding type of `value` by searching in XML files.
    Because there is a possibility that multiple types associated with the same value,
    for avoid this problem, we specify the order of types and return the first occurrence as the query result.
    """
    DATA_DIR = config.get_karabiner_resources_dir()

    def __init__(self):
        self.data = {}

    @classmethod
    def get_instance(cls):
        if hasattr(cls, '_instance'):
            return cls._instance
        else:
            cls._instance = cls()
            cls._instance.load_data()
            return cls._instance

    @classmethod
    def query(cls, value):
        self = cls.get_instance()
        for type in self.orders:
            if self.is_in(type, value):
                return type
        return None

    def is_in(self, type, value):
        return type if value in self.data.get(type, []) else None

    @property
    def orders(self):
        raise exception.NeedOverrideError()

    def load_data(self):
        raise exception.NeedOverrideError()


class KeyHeaderQuery(BaseTypeQuery):
    RESOURCE_FILE = 'symbol_map.xml'

    @property
    def orders(self):
        return [
            'ModifierFlag',
            'ConsumerKeyCode',
            'KeyCode',
            'Option',
            'InputSource',
            'PointingButton',
            'DeviceProduct',
            'DeviceVendor',
            'KeyboardType',
        ]

    def load_data(self):
        filepath = os.path.join(self.DATA_DIR, self.RESOURCE_FILE)

        xml_tree = BaseXML.parse(filepath)
        for symbol_map in xml_tree:
            type = symbol_map.get('type')
            value = symbol_map.get('name')
            self.data.setdefault(type, set()).add(value)


class DefinitionTypeQuery(BaseTypeQuery):
    @property
    def orders(self):
        return [
            'appdef',
            'replacementdef',
            'modifierdef',
            'devicevendordef',
            'deviceproductdef',
            'uielementroledef',
            'windownamedef',
            'vkopenurldef',
            'inputsourcedef',
            'vkchangeinputsourcedef',
        ]

    @classmethod
    def query(cls, value):
        result = super(DefinitionTypeQuery, cls).query(value)
        if result:
            return result
        elif KeyHeaderQuery.query(value) == 'ModifierFlag':
            return 'modifierdef'

    def load_data(self):
        for filepath in glob.glob(os.path.join(self.DATA_DIR, '*def.xml')):
            type, _ = os.path.splitext(os.path.basename(filepath))
            self.data[type] = self.get_data(type, filepath)

    def get_data(self, type, filepath):
        name_tag = def_tag_map.get_name_tag_name(type)
        xml_tree = BaseXML.parse(filepath)

        if name_tag == '':
            tags = xml_tree.findall(type)
        else:
            tags = xml_tree.findall('%s/%s' % (type, name_tag))

        return set(tag.text for tag in tags)


class DefinitionBucket(object):
    """This class is used to store global `Definition` objects,
    so we can create a `Definition` object from anywhere,
    and found it by the original value used to define.
    """
    def __init__(self):
        self.buckets = {
            'filter': {},
            'key': {},
        }

    @classmethod
    def get_instance(cls, reset=False):
        if not hasattr(cls, '_instance') or reset:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def get_all_definitions(cls):
        list_of_defos = [d.values() for d in cls.get_instance().buckets.values()]
        defos = set(chain.from_iterable(chain.from_iterable(list_of_defos)))
        return sorted(defos, key=lambda f: (f.get_def_tag_name(), f.get_name()))

    @classmethod
    def put(cls, category, name, definitions):
        cls.get_instance().buckets[category][name] = definitions

    @classmethod
    def get(cls, category, name):
        return cls.get_instance().buckets[category].get(name)

    @classmethod
    def has(cls, category, name):
        return name in cls.get_instance().buckets[category]

    @classmethod
    def clear(cls):
        cls.get_instance(reset=True)
