# -*- coding: utf-8 -*-
import re
import json
import unicodedata


def replace_str_by_dict_value(target_str, replace_dict):
    for key, new_str in replace_dict.items():
        old_str = '${' + key + '}'
        if old_str in target_str:
            target_str = target_str.replace(old_str, str(new_str))
    return target_str


def get_string_width(target_str):
    width = 0
    for c in target_str:
        char_width = unicodedata.east_asian_width(c)
        if char_width in u"WFA":
            width += 2
        else:
            width += 1
    return width


def cut_string(target_str, length):
    width = 0
    result_str = ''
    for c in target_str:
        char_width = unicodedata.east_asian_width(c)
        if char_width in u'WFA':
            if width + 2 > length:
                break
            width += 2
            result_str += c
        else:
            if width + 1 > length:
                break
            width += 1
            result_str += c
    return result_str


def to_camel_string(target):
    ret = target.lower()
    words = re.split('[\s_]', ret)
    words = map(lambda x: x.capitalize(), words)
    return ''.join(words)


def convert_str(target):
    if isinstance(target, list) or isinstance(target, dict):
        return json.dumps(target)
    return str(target)
