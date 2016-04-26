from __future__ import print_function, unicode_literals

import yaml

from .logger import LOG

__author__ = "danishabdullah"


def _lowercase_all(dictionary):
    res = {}
    for k, v in dictionary.items():
        if isinstance(k, str):
            k = k.lower()
        if isinstance(v, str):
            res[k] = v.lower()
        elif isinstance(v, dict):
            res[k] = _lowercase_all(v)
        else:
            res[k] = v
    return res


def make_verbose(dictionary):
    LOG.info("Converting spec to verbose mode.")
    for k, v in dictionary.items():
        fields = []
        for field in v['fields']:
            name, typ, mode = field.split(', ')
            verbose = {"name": name, "type": typ, "mode": mode}
            fields.append(verbose)
            msg = "{} ====> {}".format(field, verbose)
            LOG.debug(msg)
        v['fields'] = fields
    return dictionary


def load(filename):
    with open(filename, 'r') as file:
        LOG.info("Loading yaml file from {}".format(filename))
        spec = yaml.load(file)
        LOG.info("Lowercasing all entries.")
        spec = _lowercase_all(spec)
    mode = spec.pop('spec-mode', None)
    if not mode or mode not in ('compact', 'verbose'):
        raise ValueError("schema file must have a spec-mode which can be either 'compact' or 'verbose'")
    LOG.debug("Loaded '{}' specification:\n{}".format(mode.upper(), spec))
    if mode == 'compact':
        spec = make_verbose(spec)
        LOG.debug("Converted to 'VERBOSE' specification:\n".format(spec))
    return spec
