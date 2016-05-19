# -*- coding: utf-8 -*-
from __future__ import print_function
from . import util
from . import config


def _apply_if_is_alias(vars, func):
    result = {}

    for alias_name in vars.keys():
        alias = vars[alias_name]
        if hasattr(alias, '__iter__') \
                and alias_name.endswith('ALIAS') \
                and not alias_name.startswith('_'):
            result[alias_name] = func(vars, alias_name)

    return result


def _get_aliases():
    if not hasattr(_get_aliases, 'aliases'):
        aliases = util.read_python_file(config.get_data_path('alias.data'))
        _get_aliases.aliases = _apply_if_is_alias(aliases, lambda d, k: d[k])

    return _get_aliases.aliases


# alias is case-insensitive
def get_alias(alias_name, value):
    def get(aname, avalue):
        return _get_aliases()[aname].get(avalue.lower())

    if alias_name == 'KEY_ALIAS':
        return get('KEY_ALIAS', value) or get('MODIFIER_ALIAS', value)
    else:
        return get(alias_name, value)


def update_alias(alias_name, new_aliases):
    _get_aliases().setdefault(alias_name, {}).update(new_aliases)


def update_aliases(aliases_table):
    _apply_if_is_alias(aliases_table, lambda d, k: update_alias(k, d[k]))
