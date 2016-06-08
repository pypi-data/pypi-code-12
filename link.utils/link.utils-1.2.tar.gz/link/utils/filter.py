# -*- coding: utf-8 -*-

from operator import lt, le, gt, ge, ne, eq
from copy import deepcopy
from re import I, search

from datetime import datetime
from time import time

from b3j0f.utils.iterable import isiterable
from six import string_types, iteritems


def get_field(key, obj):
    """
    Get field in dictionary.

    :param key: path to field in dictionary
    :type key: str

    :param obj: dictionary used for search
    :type obj: dict

    :returns: field value
    """

    val = obj

    for subkey in key.split('.'):
        val = val[subkey]

    return val


def set_field(key, obj, val):
    """
    et field in dictionary.

    :param key: path to field in dictionary
    :type key: str

    :param obj: dictionary used for search
    :type obj: dict

    :param val: value to set
    """

    o = obj
    subkeys = key.split('.')

    for subkey in subkeys[:-1]:
        if subkey not in o:
            o[subkey] = {}

        o = o[subkey]

    o[subkeys[-1]] = val


def del_field(key, obj):
    """
    Remove field from dictionary.

    :param key: path to field in dictionary
    :type key: str

    :param obj: dictionary used for search
    :type obj: dict
    """

    val = obj
    subkeys = key.split('.')

    for subkey in subkeys[:-1]:
        if subkey not in val:
            return

        val = val[subkey]

    del val[subkeys[-1]]


class Filter(object):
    """
    Apply MongoDB filter rule on dictionary.
    """

    def __init__(self, rule, *args, **kwargs):
        """
        :param rule: MongoDB filter rule.
        :type rule: dict
        """

        super(Filter, self).__init__(*args, **kwargs)

        self.rule = rule

    def match(self, obj):
        """
        Check if dictionary match the MongoDB filter.

        :param obj: dictionary to check
        :type obj: dict

        :returns: True if dictionary match
        :rtype: boolean
        """

        return self._match(self.rule, obj)

    def _match(self, rule, obj):
        """
        Internal method used for checking.

        :param rule: MongoDB sub-filter
        :type rule: dict

        :param obj: dictionary to check
        :type obj: dict

        :returns: True if dictionary match
        :rtype: boolean
        """

        for key in rule:
            if key == '$and':
                if not self.handle_and(key, rule[key], obj):
                    return False

            elif key == '$or':
                if not self.handle_or(key, rule[key], obj):
                    return False

            elif key == '$nor':
                if not self.handle_nor(key, rule[key], obj):
                    return False

            elif not self.handle_field(key, rule[key], obj):
                return False

        return True

    def handle_and(self, key, rule, obj):
        """
        Handle ``$and`` operator.

        :param key: key to check in dictionary (unused)
        :type key: str

        :param rule: MongoDB sub-filter
        :type rule: dict

        :param obj: dictionary to check
        :type obj: dict

        :returns: True if dictionary match all sub-filters
        :rtype: boolean
        """

        for subrule in rule:
            if not self._match(subrule, obj):
                return False

        return True

    def handle_or(self, key, rule, obj):
        """
        Handle ``$or`` operator.

        :param key: key to check in dictionary (unused)
        :type key: str

        :param rule: MongoDB sub-filter
        :type rule: dict

        :param obj: dictionary to check
        :type obj: dict

        :returns: True if dictionary match at least one sub-filter
        :rtype: boolean
        """

        for subrule in rule:
            if self._match(subrule, obj):
                return True

        return False

    def handle_nor(self, key, rule, obj):
        """
        Handle ``$nor`` operator.

        :param key: key to check in dictionary (unused)
        :type key: str

        :param rule: MongoDB sub-filter
        :type rule: dict

        :param obj: dictionary to check
        :type obj: dict

        :returns: True if dictionary doesn't match any sub-filters
        :rtype: boolean
        """

        return not self.handle_or(key, rule, obj)

    def handle_field(self, key, rule, obj):
        """
        Handle filter on field.

        :param key: key to check in dictionary
        :type key: str

        :param rule: MongoDB sub-filter
        :type rule: dict

        :param obj: dictionary to check
        :type obj: dict

        :returns: True if dictionary match
        :rtype: boolean
        """

        if isinstance(rule, dict):
            if '$in' in rule:
                return self.handle_in_field(key, rule['$in'], obj)

            elif '$nin' in rule:
                return not self.handle_in_field(key, rule['$nin'], obj)

            elif '$all' in rule:
                return self.handle_all_field(key, rule['$all'], obj)

            else:
                return self.handle_field_rule(key, rule, obj)

        else:
            try:
                field = get_field(key, obj)

            except KeyError:
                return False

            return (field == rule)

    def handle_in_field(self, key, rule, obj):
        """
        Handle ``$in`` operator.

        :param key: key to check in dictionary
        :type key: str

        :param rule: MongoDB sub-filter
        :type rule: dict

        :param obj: dictionary to check
        :type obj: dict

        :returns: True if field match at least one value
        :rtype: boolean
        """

        try:
            field = get_field(key, obj)

        except KeyError:
            return False

        return field in rule

    def handle_all_field(self, key, rule, obj):
        """
        Handle ``$all`` operator.

        :param key: key to check in dictionary
        :type key: str

        :param rule: MongoDB sub-filter
        :type rule: dict

        :param obj: dictionary to check
        :type obj: dict

        :returns: True if field match all values
        :rtype: boolean
        """

        try:
            field = get_field(key, obj)

        except KeyError:
            return False

        if not isiterable(field, exclude=string_types):
            return False

        for item in rule:
            if item not in field:
                return False

        return True

    def handle_field_exists(self, key, rule, obj):
        """
        Handle ``$exists`` operator.

        :param key: key to check in dictionary
        :type key: str

        :param rule: MongoDB sub-filter
        :type rule: dict

        :param obj: dictionary to check
        :type obj: dict

        :returns: True if field is in dictionary
        :rtype: boolean
        """

        try:
            get_field(key, obj)

        except KeyError:
            found = False

        else:
            found = True

        if rule:
            return found

        else:
            return not found

    def handle_field_regex(self, key, pattern, obj, opts=None):
        """
        Handle ``$regex`` operator.

        :param key: key to check in dictionary
        :type key: str

        :param rule: MongoDB sub-filter
        :type rule: dict

        :param obj: dictionary to check
        :type obj: dict

        :returns: True if field match regex
        :rtype: boolean
        """

        opts = I if isinstance(opts, string_types) and 'i' in opts else 0

        try:
            field = get_field(key, obj)

        except KeyError:
            return False

        if None in (field, pattern):
            return False

        return bool(search(pattern, field, opts))

    def handle_field_cond(self, key, rule, obj, cond):
        """
        Handle comparison operators.

        :param key: key to check in dictionary
        :type key: str

        :param rule: MongoDB sub-filter
        :type rule: dict

        :param obj: dictionary to check
        :type obj: dict

        :param cond: comparison operator
        :type cond: callable

        :returns: True if field match
        :rtype: boolean
        """

        try:
            field = get_field(key, obj)

        except KeyError:
            return False

        if not cond(field, rule):
            return False

        return True

    def handle_field_rule(self, key, rule, obj):
        """
        Handle other operators.

        :param key: key to check in dictionary
        :type key: str

        :param rule: MongoDB sub-filter
        :type rule: dict

        :param obj: dictionary to check
        :type obj: dict

        :returns: True if field match
        :rtype: boolean
        """

        cond = {
            '$lt': lt,
            '$lte': le,
            '$gt': gt,
            '$gte': ge,
            '$ne': ne,
            '$eq': eq
        }

        for op in rule:
            if op == '$exists':
                if not self.handle_field_exists(key, rule[op], obj):
                    return False

            elif op in cond.keys():
                if not self.handle_field_cond(key, rule[op], obj, cond[op]):
                    return False

            elif op == '$regex':
                pattern = rule[op]
                options = rule.get('$options', None)

                if not self.handle_field_regex(key, pattern, obj, options):
                    return False

            elif op == '$not':
                if isinstance(rule[op], dict):
                    if self.handle_field_rule(key, rule[op], obj):
                        return False

                else:
                    pattern = rule[op]
                    options = rule.get('$options', None)

                    if self.handle_field_regex(key, pattern, obj, options):
                        return False

        return True


class Mangle(object):
    """
    Apply MongoDB update spec on dictionary.
    """

    def __init__(self, rule, *args, **kwargs):
        """
        :param rule: MongoDB update spec
        :type rule: dict
        """

        super(Mangle, self).__init__(*args, **kwargs)

        self.rule = rule

    def __call__(self, obj):
        """
        Apply rule on dictionary.

        :param obj: dictionary used to apply rule on
        :type obj: dictionary

        :returns: Modified dictionary
        :rtype: dict
        """

        obj = deepcopy(obj)

        for op in self.rule:
            if not op.startswith('$'):
                continue

            method = getattr(self, op[1:])
            method(self.rule[op], obj)

        return obj

    def inc(self, rule, obj):
        """
        Handle ``$inc`` operator.

        :param rule: sub-spec
        :type rule: dict

        :param obj: dictionary to apply sub-rule on
        :type obj: dict
        """

        for key, amount in iteritems(rule):
            try:
                val = get_field(key, obj)

            except KeyError:
                val = 0

            set_field(key, obj, val + amount)

    def mul(self, rule, obj):
        """
        Handle ``$mul`` operator.

        :param rule: sub-spec
        :type rule: dict

        :param obj: dictionary to apply sub-rule on
        :type obj: dict
        """

        for key, amount in iteritems(rule):
            try:
                val = get_field(key, obj)

            except KeyError:
                val = 0

            set_field(key, obj, val * amount)

    def rename(self, rule, obj):
        """
        Handle ``$rename`` operator.

        :param rule: sub-spec
        :type rule: dict

        :param obj: dictionary to apply sub-rule on
        :type obj: dict
        """

        for key, newkey in iteritems(rule):
            try:
                val = get_field(key, obj)

            except KeyError:
                pass

            else:
                del_field(key, obj)
                set_field(newkey, obj, val)

    def set(self, rule, obj):
        """
        Handle ``$set`` operator.

        :param rule: sub-spec
        :type rule: dict

        :param obj: dictionary to apply sub-rule on
        :type obj: dict
        """

        for key, val in iteritems(rule):
            set_field(key, obj, val)

    def unset(self, rule, obj):
        """
        Handle ``$unset`` operator.

        :param rule: sub-spec
        :type rule: dict

        :param obj: dictionary to apply sub-rule on
        :type obj: dict
        """

        for key in rule:
            try:
                get_field(key, obj)

            except KeyError:
                pass

            else:
                del_field(key, obj)

    def min(self, rule, obj):
        """
        Handle ``$min`` operator.

        :param rule: sub-spec
        :type rule: dict

        :param obj: dictionary to apply sub-rule on
        :type obj: dict
        """

        for key, newval in iteritems(rule):
            try:
                val = get_field(key, obj)

            except KeyError:
                set_field(key, obj, newval)

            else:
                if newval < val:
                    set_field(key, obj, newval)

    def max(self, rule, obj):
        """
        Handle ``$max`` operator.

        :param rule: sub-spec
        :type rule: dict

        :param obj: dictionary to apply sub-rule on
        :type obj: dict
        """

        for key, newval in iteritems(rule):
            try:
                val = get_field(key, obj)

            except KeyError:
                set_field(key, obj, newval)

            else:
                if newval > val:
                    set_field(key, obj, newval)

    def currentDate(self, rule, obj):
        """
        Handle ``$currentDate`` operator.

        :param rule: sub-spec
        :type rule: dict

        :param obj: dictionary to apply sub-rule on
        :type obj: dict
        """

        for key, typespec in iteritems(rule):
            if isinstance(typespec, bool):
                val = datetime.now() if typespec else time()

            elif typespec['$type'] == 'date':
                val = datetime.now()

            elif typespec['$type'] == 'timestamp':
                val = time()

            else:
                continue

            set_field(key, obj, val)

    def addToSet(self, rule, obj):
        """
        Handle ``$addToSet`` operator.

        :param rule: sub-spec
        :type rule: dict

        :param obj: dictionary to apply sub-rule on
        :type obj: dict
        """

        for key, value in iteritems(rule):
            try:
                array = get_field(key, obj)

            except KeyError:
                array = []

            if isinstance(value, dict) and '$each' in value:
                value = value['$each']

            if not isinstance(value, list):
                value = [value]

            for val in value:
                if val not in array:
                    array.append(val)

            set_field(key, obj, array)

    def pop(self, rule, obj):
        """
        Handle ``$pop`` operator.

        :param rule: sub-spec
        :type rule: dict

        :param obj: dictionary to apply sub-rule on
        :type obj: dict
        """

        for key, spec in iteritems(rule):
            array = get_field(key, obj)

            if spec == -1:
                array.pop()

            elif spec == 1:
                array.pop(0)

            set_field(key, obj, array)

    def pull(self, rule, obj):
        """
        Handle ``$pull`` operator.

        :param rule: sub-spec
        :type rule: dict

        :param obj: dictionary to apply sub-rule on
        :type obj: dict
        """

        for key, spec in iteritems(rule):
            array = get_field(key, obj)

            if isinstance(spec, dict):
                _filter = Filter(spec)

                array = [
                    val
                    for val in array
                    if not _filter.match(val)
                ]

            else:
                array = [val for val in array if val != spec]

            set_field(key, obj, array)

    def pullAll(self, rule, obj):
        """
        Handle ``$pullAll`` operator.

        :param rule: sub-spec
        :type rule: dict

        :param obj: dictionary to apply sub-rule on
        :type obj: dict
        """

        for key, vals in iteritems(rule):
            array = get_field(key, obj)

            array = [
                val
                for val in array
                if val not in vals
            ]

            set_field(key, obj, array)

    def push(self, rule, obj):
        """
        Handle ``$push`` operator.

        :param rule: sub-spec
        :type rule: dict

        :param obj: dictionary to apply sub-rule on
        :type obj: dict
        """

        for key, spec in iteritems(rule):
            try:
                array = get_field(key, obj)

            except KeyError:
                array = []

            p, sort, s = -1, None, None

            if isinstance(spec, dict):
                if '$each' in spec:
                    val = spec['$each']
                    p = spec.get('$position', -1)
                    sort = spec.get('$sort', None)
                    s = spec.get('$slice', None)

            else:
                val = spec

            if not isinstance(val, list):
                val = [val]

            array = array[:p] + val + array[p:]

            if sort is not None:
                if isinstance(sort, dict):
                    for sortkey in sort:
                        keyfunc = lambda item, sk=sortkey: item[sk]
                        array.sort(key=keyfunc, reverse=(sort[sortkey] < 0))

                else:
                    array.sort(reverse=(sort < 0))

            if s is not None:
                if s < 0:
                    array = array[s:]

                else:
                    array = array[:s]

            set_field(key, obj, array)

    def bit(self, rule, obj):
        """
        Handle ``$bit`` operator.

        :param rule: sub-spec
        :type rule: dict

        :param obj: dictionary to apply sub-rule on
        :type obj: dict
        """

        for key, spec in iteritems(rule):
            try:
                val = get_field(key, obj)

            except KeyError:
                val = 0

            if 'and' in spec:
                val &= spec['and']

            elif 'or' in spec:
                val |= spec['or']

            elif 'xor' in spec:
                val ^= spec['xor']

            set_field(key, obj, val)
