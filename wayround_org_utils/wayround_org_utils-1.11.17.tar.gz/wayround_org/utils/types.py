"""
Check object type by searching it's attributes

This module supports two kinds of operation:
    1. Stranded - using original method of type recognition
    2. Native - using Python isinstance built-in function

Examples of execution:

import lxml.etree

import wayround_org.utils.types

>wayround_org.utils.types.types_n(lxml.etree.Element('q'))
['Hashable', 'Sized', 'Iterable', 'Container']

>wayround_org.utils.types.types_s(lxml.etree.Element('q'))
['Hashable', 'Sized', 'Mapping', 'Iterable', 'Container']
"""

import collections.abc

# This table is taken from python-3.3.2-docs-html/library/collections.abc.html

COMPARISON_TABLE = {
    'Container': {
        # Inherits from
        'i': [],
        # Abstract Methods
        'a': ['__contains__'],
        # Mixin Methods
        'm': []
        },
    'Hashable': {
        'i': [],
        'a': ['__hash__'],
        'm': []
        },
    'Iterable': {
        'i': [],
        'a': ['__iter__'],
        'm': []
        },
    'Iterator': {
        'i': ['Iterable'],
        'a': ['__next__'],
        'm': ['__iter__']
        },
    'Sized': {
        'i': [],
        'a': ['__len__'],
        'm': []
        },
    'Callable': {
        'i': [],
        'a': ['__call__'],
        'm': []
        },
    'Sequence': {
        'i': ['Sized', 'Iterable', 'Container'],
        'a': ['__getitem__', '__len__'],
        'm': ['__contains__', '__iter__', '__reversed__', 'index', 'count']
        },
    'MutableSequence': {
        'i': ['Sequence'],
        'a': ['__getitem__', '__setitem__', '__delitem__', '__len__',
              'insert'],
        'm': ['append', 'reverse', 'extend', 'pop', 'remove', '__iadd__']
        },
    'Set': {
        'i': ['Sized', 'Iterable', 'Container'],
        'a': ['__contains__', '__iter__', '__len__'],
        'm': ['__le__', '__lt__', '__eq__', '__ne__', '__gt__', '__ge__',
              '__and__', '__or__', '__sub__', '__xor__', 'isdisjoint']
        },
    'MutableSet': {
        'i': ['Set'],
        'a': ['__contains__', '__iter__', '__len__', 'add', 'discard'],
        'm': ['clear', 'pop', 'remove', '__ior__', '__iand__',
              '__ixor__', '__isub__']
        },
    'Mapping': {
        'i': ['Sized', 'Iterable', 'Container'],
        'a': ['__getitem__', '__iter__', '__len__'],
        'm': ['__contains__', 'keys', 'items', 'values', 'get', '__eq__',
              '__ne__']
        },
    'MutableMapping': {
        'i': ['Mapping'],
        'a': ['__getitem__', '__setitem__', '__delitem__', '__iter__',
              '__len__'],
        'm': ['pop', 'popitem', 'clear', 'update', 'setdefault']
        },
    }


def check_type_s(obj, name):
    """
    Check type using stranded method
    """

    if not name in COMPARISON_TABLE.keys():
        raise ValueError("Invalid type name")

    ret = True

    ref_type = COMPARISON_TABLE[name]

    for i in ref_type['i']:

        if not check_type_s(obj, i):
            ret = False
            break

    if ret:
        for i in ref_type['a']:
            if not hasattr(obj, i):
                ret = False
                break

    if ret:
        for i in ref_type['m']:
            if not hasattr(obj, i):
                ret = False
                break

    return ret


def types_s(obj):
    """
    Make list of types object in, using stranded method
    """

    ret = []

    for name in COMPARISON_TABLE.keys():
        if check_type_s(obj, name):
            ret.append(name)

    return ret


def check_type(obj, name):
    """
    Check type using native method
    """

    if not name in COMPARISON_TABLE.keys():
        raise ValueError("Invalid type name")

    return isinstance(obj, getattr(collections.abc, name))


def types(obj):
    """
    Make list of types object in, using native method
    """

    ret = []

    for name in COMPARISON_TABLE.keys():
        if check_type(obj, name):
            ret.append(name)

    return ret


for i in COMPARISON_TABLE.keys():
    exec(
        """
def is{name}_s(obj):
    return check_type_s(obj, '{name}')
""".format(name=i)
        )

del i

for i in COMPARISON_TABLE.keys():
    exec(
        """
def is{name}(obj):
    return check_type(obj, '{name}')
""".format(name=i)
        )

del i


STRUCT_CHECK_KEYS = ['t', 'te', 'None', '<', '>', '.', '', ' ', '{}']


def struct_check(value, struct):
    """
    Check whatever value corresponds to struct

    This implementation can't check dict with non-str keys, so exception is
    raised in this case

    Examples of `struct':


    {
    't': list, # type or tuple of types (like in isinstance). can also be a
               # string or tuple of strings with type names. see desc below
    'te': True, # exact type check with `type' function. default is True.
    'None': False, # can value be None? (False - default)
    '<': 0, # min child count. None - is default - no check
    '>': None, # max child count. None - is default - no check
    '.': { # check children. for work with sequences. default is None - not
           #                                                 check children
         't': list,
         '<': 1,
         '>': None,
         '.': {
              't': _Element
              }
         } # - default is None

    # works only if 't' is str or bytes
    '': False,
    ' ': False,  # '' - string emptiness allow or not,
                 # ' ' - only spaces in string allow or not

    '{}': {}, # if 't' is dict and only dict: True - any keys are possible and
              # each child checked with '.' value (recursion). False - same
              # as True, but without values checking (default)
              # if '{}' is dict, then all values in this dict must be dicts
              # with structures like this.
    }

    if 't' value is of type str, then value type is checked using this module's
    types() or types_s(): if '!' in beginning of 't' value, then types_s() is
    used

    return False if value does not matches struct, and True otherwise
    """

    ret = True

    if not isinstance(struct, dict):
        raise TypeError("`struct' must be dict")

    for i in list(struct.keys()):
        if not i in STRUCT_CHECK_KEYS:
            raise ValueError("invalid `struct' key: {}".format(i))

    typ = struct['t']

    if not isinstance(typ, tuple):
        typ = typ,

    iterable_type = types(value)

    # 'Iterable' required for checking sets
    iterable_type = 'Sequence' in iterable_type or 'Iterable' in iterable_type

    for i in typ:
        t_type = type(i)
        if t_type == str:
            if i.startswith('!'):
                if not i[1:] in COMPARISON_TABLE.keys():
                    raise ValueError("Invalid type name")
            else:
                if not i in COMPARISON_TABLE.keys():
                    raise ValueError("Invalid type name")

    type_exact = True
    if 'te' in struct:
        type_exact = struct['te']
        if not isinstance(type_exact, bool):
            raise TypeError("`te' must be bool")

    can_be_none = False
    if 'None' in struct:
        can_be_none = struct['None']
        if not isinstance(can_be_none, bool):
            raise TypeError("`None' must be bool")

    min_child_count = None
    if '<' in struct:
        min_child_count = struct['<']
        if min_child_count is not None and not isinstance(
                min_child_count, int):
            raise TypeError("`<' must be None or int")

    max_child_count = None
    if '>' in struct:
        max_child_count = struct['>']
        if max_child_count is not None and not isinstance(
                max_child_count, int):
            raise TypeError("`>' must be None or int")

    string_emptiness = True
    if '' in struct:
        string_emptiness = struct['']
        if not isinstance(string_emptiness, bool):
            raise TypeError("`' must be bool")

    string_is_space = True
    if ' ' in struct:
        string_is_space = struct[' ']
        if not isinstance(string_is_space, bool):
            raise TypeError("` ' must be bool")

    next_test = None
    if '.' in struct:
        if value is not None:
            next_test = struct['.']
            if next_test is not None and not isinstance(next_test, dict):
                raise TypeError("`.' must be None or dict")

            if next_test is not None and not iterable_type:
                raise ValueError(
                    "`.' is not None so value must be a sequence"
                    )

    dict_info = False
    if '{}' in struct:
        dict_info = struct['{}']
        if not type(dict_info) in [bool, dict]:
            raise TypeError(
                "`{{}}' must be bool or dict, but it's a: {}".format(
                    type(dict_info)
                    )
                )

        keys = list(dict_info.keys())

        for i in keys:
            if not isinstance(i, str):
                raise ValueError("keys in struct dict must be str")

            if not isinstance(dict_info[i], dict):
                raise ValueError("values in struct dict must be dict")

    if can_be_none == True and value == None:
        ret = True
    elif can_be_none == False and value == None:
        ret = False
    else:
        if ret:
            if type_exact == True:
                found = False
                for i in typ:
                    t_type = type(i)
                    if t_type == str:
                        if i.startswith('!'):
                            if i[1:] in types_s(value):
                                found = True
                                break
                        else:
                            if i in types(value):
                                found = True
                                break
                    else:
                        if isinstance(value, i):
                            found = True
                            break

                if not found:
                    ret = False
            else:
                if not isinstance(value, typ):
                    ret = False

        if ret:
            if min_child_count is not None:
                if len(value) < min_child_count:
                    ret = False

        if ret:
            if max_child_count is not None:
                if len(value) > max_child_count:
                    ret = False

        if ret:
            if (isinstance(value, str)
                    and value == ''
                    and string_emptiness == False):
                ret = False

        if ret:
            if (isinstance(value, bytes)
                    and value == b''
                    and string_emptiness == False):
                ret = False

        if ret:
            if (isinstance(value, str)
                    and value.isspace()
                    and string_is_space == False):
                ret = False

        if ret:
            if (isinstance(value, bytes)
                    and value.isspace()
                    and string_is_space == False):
                ret = False

        if ret:
            if len(typ) == 1 and typ[0] == dict:
                if isinstance(dict_info, dict):

                    keys = list(dict_info.keys())
                    for i in keys:
                        if not i in value:
                            ret = False
                            break
                        else:
                            ret = struct_check(value[i], dict_info[i])
                            if ret == False:
                                break

                    keys = list(value.keys())
                    for i in keys:
                        if not i in dict_info:
                            ret = False
                            break

                elif dict_info == False:
                    pass

                elif dict_info == True:
                    vkeys = list(value.keys())
                    for i in vkeys:
                        ret = struct_check(value[i], next_test)
                        if ret == False:
                            break
                else:
                    raise Exception("Programming error")

        if ret:
            if next_test is not None:
                if iterable_type:
                    for i in value:
                        if struct_check(i, next_test) == False:
                            ret = False
                            break

                else:
                    ret = False

    return ret


def attrs_object_to_dict(object_, dict_, attrs_keys=None):
    """
    attrs_keys: list of tuples, each of wich ('attr_name', 'key_name')
    """

    if attrs_keys is None:
        attrs_keys = list(object_.__dict__.keys())

    for i in attrs_keys:
        dict_[i[1]] = getattr(object_, i[0])

    return


def attrs_dict_to_object(
        dict_, object_, attrs_keys=None, create_new_attributes=False
        ):
    """
    attrs_keys: list of tuples, each of wich ('attr_name', 'key_name')
    """

    if attrs_keys is None:
        attrs_keys = list(dict_.keys())

    for i in attrs_keys:
        if hasattr(object_, i[0]) or create_new_attributes == True:
            setattr(object_, i[0], dict_[i[1]])
        else:
            raise KeyError(
                "object `{}' has no attribute `{}'".format(
                    object_,
                    i[0]
                    )
                )

    return


def attrs_dict_to_object_same_names(lst):

    ret = []

    for i in lst:
        ret.append((i, i,))

    return ret


def is_method(obj):
    return hasattr(obj, '__self__')


def value_to_bool(value):

    ret = False

    if isinstance(value, str):
        ret = text_to_bool(value)
    else:
        ret = bool(value)

    return ret


def text_to_bool(text):

    if not isinstance(text, str):
        raise TypeError("`text' must be str")

    return text.lower().strip() in ['1', 'yes', 'true', 'ok', 'y']


def is_all_rec_bytes_str(args, empty_fails=False, must_be=None):
    """
    Check's what all values in args ar bytes or str, recurcevely

    return bool, type (bool is True if passed. type is bytes, str or None)
    """

    if not isSequence(args):
        raise TypeError("`args' must be sequence, not {}".format(type(args)))

    if len(args) == 0:
        ret = not empty_fails, must_be
    else:

        tt = must_be
        error = False
        for i in args:

            if isinstance(i, list):
                res, res_t = is_all_rec_bytes_str(i, empty_fails, tt)

                if res == False:
                    error = True
                    break
                else:
                    if tt is None:
                        tt = res_t
                    else:
                        if tt != res_t:
                            error = True
                            break

            else:

                if tt is None:
                    tt = type(i)
                else:
                    if not isinstance(i, tt):
                        error = True
                        break

        if error:
            ret = False, None
        else:
            ret = True, tt

    return ret
