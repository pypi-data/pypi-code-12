# -*- coding: utf-8 -*
from __future__ import print_function
import operator
from functools import reduce
from itertools import groupby

from . import util
from . import query
from . import osxkit
from . import filter
from . import keymap
from . import definition
from . import exception
from . import def_tag_map
from .basexml import BaseXML
from .fucking_string import is_string_type


def define_filters(raw_filters):
    """Found undefined `Filter` in `raw_filters`, and create a `Definition` by it."""
    for raw_filter in raw_filters:
        if raw_filter.startswith('!'):
            val = raw_filter[1:]
        else:
            val = raw_filter

        if not query.is_defined_filter(val):
            FilterCreater.define(val)


def define_keymaps(raw_keymaps):
    """Found undefined `Key` in `raw_keymaps`, and create a `Definition` by it."""
    # raw_keymap: (str, (str), ...)
    for raw_keymap in raw_keymaps:
        try:
            # raw_keycombo: (str)
            for raw_keycombo in raw_keymap[1:]:
                # raw_key: str
                for raw_key in raw_keycombo:
                    if not query.is_defined_key(raw_key):
                        KeymapCreater.define_key(raw_key)
        except exception.UndefinedKeyException as e:
            exception.ExceptionRegister.record_by(raw_keymap, e)


def create_filters(raw_filters):
    """Create `Filter` object from `raw_filters`,
    `Filter` objects with the same class has been merged to one `Filter` object.
    """
    def filter_sort_key(f):
        return f.get_tag_name()

    filter_objs = []

    for raw_filter in raw_filters:
        objs = FilterCreater.create(raw_filter)
        filter_objs.extend(objs)

    grouped = groupby(sorted(filter_objs, key=filter_sort_key), filter_sort_key)
    # merge filters in the same group
    filter_objs = tuple(reduce(operator.add, group) for _, group in grouped)
    return filter_objs


def create_keymaps(raw_keymaps):
    """Create `Keymap` object from `raw_keymaps`."""
    keymap_objs = []

    for raw_keymap in raw_keymaps:
        try:
            keymap_obj = KeymapCreater.create(raw_keymap)
            keymap_objs.append(keymap_obj)
        except exception.InvalidKeymapException as e:
            exception.ExceptionRegister.record_by(raw_keymap, e)

    return keymap_objs


def create_definitions(definitions):
    definition_objs = []

    for name in sorted(definitions.keys()):
        # make sure `vals` is iterable
        if util.is_list_or_tuple(definitions[name]):
            vals = definitions[name]
        else:
            vals = [definitions[name]]

        try:
            tmp = DefinitionCreater.create(name, vals)
            definition_objs.extend(tmp)
        except exception.InvalidDefinition as e:
            k = {name: definitions[name]}
            exception.ExceptionRegister.record(k, e)

    return definition_objs


class FilterCreater(object):
    @classmethod
    def define(cls, val):
        device_ids = osxkit.get_peripheral_info(val)
        # if `val` is a peripheral name
        if device_ids:
            return DefinitionCreater.define_device(val, device_ids)
        else:
            app_info = osxkit.get_app_info(val)
            # if `val` is a application name
            if app_info:
                bundle_id = app_info[1]
                return DefinitionCreater.define_app(val, bundle_id)
            else:
                raise exception.UndefinedFilterException(val)

    @classmethod
    def create(cls, raw_val):
        """Create a list of `Filter` object from `raw_val` string."""
        if raw_val.startswith('!'):
            val = raw_val[1:]
            type = 'not'
        else:
            val = raw_val
            type = 'only'

        class_names = query.query_filter_class_names(val, scope='all')
        # if `val` has been defined
        if class_names:
            filter_classes = [filter.__dict__.get(c) for c in class_names]
            definition_objs = query.DefinitionBucket.get('filter', val)

            # if `val` is user defined
            if definition_objs:
                filter_names = [d.get_name() for d in definition_objs]
            # if `val` is predefined
            else:
                filter_names = [val]

            filter_objs = []
            for i in range(len(filter_classes)):
                filter_class = filter_classes[i]
                filter_name = cls.escape_filter_name(filter_class.__name__, filter_names[i])
                filter_obj = filter_class(filter_name, type=type)
                filter_objs.append(filter_obj)
            return filter_objs
        else:
            raise exception.UndefinedFilterException(raw_val)

    @classmethod
    def escape_filter_name(cls, class_name, name_val):
        if class_name == 'ReplacementFilter':
            name_val = '{{%s}}' % name_val
        elif class_name == 'DeviceVendorFilter':
            name_val = 'DeviceVendor::%s' % name_val
        elif class_name == 'DeviceProductFilter':
            name_val = 'DeviceProduct::%s' % name_val
        elif class_name == 'ModifierFilter':
            name_val = KeymapCreater.get_karabiner_format_key(name_val, key_header='ModifierFlag')
        return name_val


class KeymapCreater(object):
    @classmethod
    def define_key(cls, val):
        app_info = osxkit.get_app_info(val)

        # if `val` is a application name
        if app_info:
            app_path = app_info[0]
            return DefinitionCreater.define_open(app_path, index=val)
        # if `val` is `VKOpenURL` format
        elif DefinitionDetector.is_vkopenurl(val):
            return DefinitionCreater.define_open(val)
        else:
            raise exception.UndefinedKeyException(val)

    @classmethod
    def create(cls, raw_keymap):
        """Create a `Keymap` object from `raw_keymap`."""
        # found the `Keymap` constructor by the command marker
        command = raw_keymap[0].strip('_')
        command = query.get_keymap_alias(command) or command
        keymap_class = keymap.__dict__.get(command)

        new_keycombos = []

        # Translate key string to `Header::Value` format if it has been defined,
        # otherwise, keep it unchanged.
        for raw_keycombo in raw_keymap[1:]:
            new_keycombo = []

            for raw_key in raw_keycombo:
                definition_objs = query.DefinitionBucket.get('key', raw_key)
                if definition_objs:
                    new_keys = [d.get_name() for d in definition_objs]
                else:
                    new_keys = [query.get_key_alias(raw_key) or raw_key]

                for new_key in new_keys:
                    new_key = cls.get_karabiner_format_key(new_key)
                    new_keycombo.append(new_key)

            new_keycombos.append(new_keycombo)

        try:
            if keymap_class:
                return keymap_class(*new_keycombos)
            # if can't found the `Keymap` constructor
            else:
                return keymap.UniversalKeyToKey(command, *new_keycombos)
        except TypeError:
            raise exception.InvalidKeymapException(raw_keymap)

    @classmethod
    def get_karabiner_format_key(cls, key, key_header=None):
        key_parts = key.split('::', 1)

        if len(key_parts) < 2:
            key = query.get_key_alias(key.lower()) or key

            for k in [key, key.upper(), key.lower()]:
                predefined_header = query.KeyHeaderQuery.query(k)
                if predefined_header:
                    return "%s::%s" % (predefined_header, k)

        if key_header:
            return "%s::%s" % (key_header, key_parts[-1])
        else:
            return key


class DefinitionCreater(object):
    @classmethod
    def create(cls, raw_name, vals):
        """Create a list of `Definition` object by found out the relevant constructor intelligently."""
        name_parts = raw_name.split('::', 1)
        # { name : [val] }
        # if no explicit `DefinitionType`, then look at `vals` to figure it out
        if len(name_parts) == 1:
            # { name : val }
            if len(vals) == 1:
                val = vals[0]
                if DefinitionDetector.is_vkopenurl(val):
                    return cls.define('VKOpenURL', raw_name, raw_name, vals)
                elif DefinitionDetector.is_uielementrole(val):
                    return cls.define('UIElementRole', raw_name, raw_name, vals)
                elif DefinitionDetector.is_app(val):
                    return cls.define('App', raw_name, raw_name, vals)
                elif DefinitionDetector.is_replacement(val):
                    return cls.define_replacement(raw_name, vals)
                else:
                    raise exception.InvalidDefinition(raw_name)
            # { name : [val] }
            elif len(vals) > 1:
                if all(is_string_type(val) for val in vals):
                    # { name : [DeviceVendorID, DeviceProductID] }
                    if DefinitionDetector.is_device(vals):
                        return cls.define_device(raw_name, vals)
                    elif DefinitionDetector.is_all_app(vals):
                        return cls.define('App', raw_name, raw_name, vals)

                return cls.define_replacement(raw_name, vals)
        # { DefHeader::DefName : [val] }
        else:
            def_header, def_name = name_parts
            class_name = query.get_def_alias(def_header) or def_header
            definition_objs = cls.define(class_name, raw_name, def_name, vals)
            if definition_objs:
                return definition_objs
            else:
                raise exception.InvalidDefinition(raw_name)

    @classmethod
    def define(cls, class_name, raw_name, def_name, vals, escape_def_name=True):
        def_class = definition.__dict__.get(class_name)
        if def_class:
            if escape_def_name:
                def_name = cls.escape_def_name(def_name, class_name)
            definition_obj = def_class(def_name, *vals)

            def_category = DefinitionDetector.get_definition_caregory(def_class)
            query.DefinitionBucket.put(def_category, raw_name, [definition_obj])
            query.DefinitionBucket.put(def_category, def_name, [definition_obj])
            return [definition_obj]
        else:
            return []

    @classmethod
    def define_replacement(cls, raw_name, vals):
        # if `vals` is `Keymap` format, define and create it
        if all(DefinitionDetector.is_keymap(val) for val in vals):
            from .parse import parse

            block_objs, _ = parse(vals, {})

            keymap_strs = ''
            for block in block_objs:
                keymap_strs += '\n'.join(str(o) for o in block.keymaps)

            after_defined = [BaseXML.create_cdata_text(keymap_strs)]
        else:
            after_defined = []

            for val in vals:
                # if `val` is application name, define it and replace with define name
                app_info = osxkit.get_app_info(val)
                if app_info:
                    bundle_id = app_info[1]
                    DefinitionCreater.define_app(val, bundle_id)
                    after_defined.append(cls.escape_def_name(val, 'App'))
                else:
                    after_defined.append(val)

        return cls.define('Replacement', raw_name, raw_name, after_defined)

    @classmethod
    def define_device(cls, raw_name, vals):
        def_name = cls.escape_def_name(raw_name)
        vdef_name = '%s_VENDOR' % def_name
        pdef_name = '%s_PRODUCT' % def_name

        [vdefinition_obj] = cls.define('DeviceVendor', raw_name, vdef_name, [vals[0]], escape_def_name=False)
        [pdefinition_obj] = cls.define('DeviceProduct', raw_name, pdef_name, [vals[1]], escape_def_name=False)
        definition_objs = (vdefinition_obj, pdefinition_obj)

        query.DefinitionBucket.put('filter', raw_name, definition_objs)
        return definition_objs

    @classmethod
    def define_app(cls, raw_name, bundle_id):
        return cls.define('App', raw_name, raw_name, [bundle_id])

    @classmethod
    def define_open(cls, val, index=None):
        if index:
            return cls.define('VKOpenURL', index, index, [val])
        else:
            def_name = util.get_checksum(val)
            return cls.define('VKOpenURL', val, def_name, [val])

    @classmethod
    def escape_def_name(cls, def_name, class_name=None):
        if class_name == 'VKOpenURL' and not def_name.startswith('KeyCode::VK_OPEN_URL_'):
            def_name = util.escape_string(def_name)
            return 'KeyCode::VK_OPEN_URL_%s' % def_name
        else:
            return util.escape_string(def_name)


class DefinitionDetector(object):
    @classmethod
    def is_device(cls, vals):
        return len(vals) == 2 and all(util.is_hex(val) for val in vals)

    @classmethod
    def is_vkopenurl(cls, val):
        # if `val` is script, application or file, or url
        return any([val.startswith('#! '),
                    val.endswith('.app') or val.startswith('/'),
                    val.startswith('http://') or val.startswith('https://')])

    @classmethod
    def is_uielementrole(cls, val):
        return val.startswith('AX') and val.isalpha()

    @classmethod
    def is_app(cls, val):
        """`appdef` has format like:

             equal:  com.example.application
             prefix: com.example.
             suffix: .example.application
        """
        words = val.split('.')
        if len(words) < 3:
            return False
        else:
            if words[0] == '':
                words.pop(0)
            elif words[-1] == '':
                words.pop()
            return all(w.isalpha() for w in words)

    @classmethod
    def is_all_app(cls, vals):
        return all(cls.is_app(val) for val in vals)

    @classmethod
    def is_replacement(cls, val):
        if BaseXML.is_cdata_text(val):
            return True
        elif cls.is_keymap(val):
            return True
        else:
            return False

    @classmethod
    def is_keymap(cls, val):
        return util.is_list_or_tuple(val)

    @classmethod
    def get_definition_caregory(cls, def_class):
        def_tag_name = def_class.get_def_tag_name()
        if def_tag_map.get_filter_class_name(def_tag_name):
            return 'filter'
        else:
            return 'key'
