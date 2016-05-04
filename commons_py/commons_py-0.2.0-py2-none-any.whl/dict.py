#!/usr/bin/python
# -*- coding: utf-8 -*-

def dict_merge(first, second):
    result = dict()
    for key, value in first.items():
        if key in second:
            is_dict = isinstance(second[key], dict)
            if is_dict: result[key] = dict_merge(value, second.pop(key))
        else:
            result[key] = value
    for key, value in second.items(): result[key] = value
    return result
