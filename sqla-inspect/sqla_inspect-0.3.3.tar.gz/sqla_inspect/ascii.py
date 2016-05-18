# -*- coding: utf-8 -*-
# * Authors:
#       * Arezki Feth <f.a@majerti.fr>;
#       * Miotte Julien <j.m@majerti.fr>;
#       * TJEBBES Gaston <g.t@majerti.fr>
"""
    Provide common tools for string handling
"""
import re
import unidecode
import random
from string import lowercase


def force_ascii(value):
    """
        Return enforced ascii string
        éko=>ko
    """
    if not isinstance(value, (str, unicode)):
        return unicode(value)
    if isinstance(value, unicode):
        return unidecode.unidecode(value)
    else:
        return unidecode.unidecode(force_unicode(value))


def force_utf8(value):
    """
    return an utf-8 string
    """
    return force_encoding(value)


def force_encoding(value, encoding='utf-8'):
    """
    Return a string encoded in the provided encoding
    """
    if not isinstance(value, (str, unicode)):
        value = str(value)
    if isinstance(value, unicode):
        value = value.encode(encoding)
    elif encoding != 'utf-8':
        value = value.decode('utf-8').encode(encoding)
    return value


def force_unicode(value):
    """
    return an utf-8 unicode entry
    """
    if not isinstance(value, (str, unicode)):
        value = unicode(value)
    if isinstance(value, str):
        value = value.decode('utf-8')
    return value


def camel_case_to_name(name):
    """
    Used to convert a classname to a lowercase name
    """
    def convert_func(val):
        return "_" + val.group(0).lower()
    return name[0].lower() + re.sub(r'([A-Z])', convert_func, name[1:])


def gen_random_string(size=15):
    """
    Generate random string

        size

            size of the resulting string
    """
    return ''.join(random.choice(lowercase) for _ in range(size))


def random_tag_id(size=15):
    """
    Return a random string supposed to be used as tag id
    """
    return gen_random_string(size)


def to_utf8(datas):
    """
    Force utf8 string entries in the given datas
    """
    res = datas
    if isinstance(datas, dict):
        res = {}
        for key, value in datas.items():
            key = to_utf8(key)
            value = to_utf8(value)
            res[key] = value

    elif isinstance(datas, (list, tuple)):
        res = []
        for data in datas:
            res.append(to_utf8(data))

    elif isinstance(datas, unicode):
        res = datas.encode('utf-8')

    return res
