# -*- coding: utf-8 -*-
import copy
import string


def merge_dict(origin_dict, add_dict):
    tmp = copy.deepcopy(origin_dict)
    for add_key, add_val in add_dict.iteritems():
        if add_key in tmp:
            if isinstance(tmp[add_key], dict):
                tmp[add_key] = merge_dict(tmp[add_key], add_val)
            else:
                tmp[add_key] = add_val
        else:
            tmp[add_key] = add_dict[add_key]
    return tmp


def replace_param_to_arg_dict(original_data, arg_dict):
    if isinstance(original_data, dict):
        tmp_dict = {}
        for key, value in original_data.items():
            tmp_dict[key] = replace_param_to_arg_dict(value, arg_dict)
        return tmp_dict
    elif isinstance(original_data, list):
        tmp_list = []
        for one_data in original_data:
            tmp_list.append(replace_param_to_arg_dict(one_data, arg_dict))
        return tmp_list
    elif isinstance(original_data, basestring):
        return string.Template(original_data).safe_substitute(arg_dict)
    else:
        return original_data
