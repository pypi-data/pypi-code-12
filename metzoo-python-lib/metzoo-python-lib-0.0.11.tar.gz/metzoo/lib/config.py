# -*- coding: utf-8 -*-

import yaml

def get(config_dict, name, default=None):
    keys = name.split(".")
    data = config_dict
    try:
        for key in keys:
            data = data[key]
    except KeyError:
        data = default
    return data

def load_yaml_dict(filename):
    with open(filename) as f:
        return yaml.load(f)
    return None
