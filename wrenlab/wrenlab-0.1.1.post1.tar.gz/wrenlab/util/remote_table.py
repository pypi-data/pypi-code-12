"""
Utility to download, parse, and memoize remote data tables in various formats.

The specification for each table is found in wrenlab/yml/rtable.yml.

(TODO: document the YAML format).
"""

import collections
import functools
import os.path
import zipfile

import pandas as pd
import yaml

from wrenlab.util.log import LOG
from wrenlab.util.memoize import memoize
from wrenlab.util.net import download

################
# YAML utilities
################

# make PyYAML read dicts into OrderedDict
_mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG

def dict_representer(dumper, data):
    return dumper.represent_dict(data.iteritems())

def dict_constructor(loader, node):
    return collections.OrderedDict(loader.construct_pairs(node))

yaml.add_representer(collections.OrderedDict, dict_representer)
yaml.add_constructor(_mapping_tag, dict_constructor)

@functools.lru_cache()
def _read_bundled_yaml(name):
    path = os.path.join(os.path.dirname(__file__), 
            "..",
            "yml",
            "{}.yml".format(name))
    with open(path) as h:
        return yaml.load(h)

@memoize
def remote_table(key, **kwargs):
    LOG.debug("Initializing remote table: {}".format(key))

    schemata = _read_bundled_yaml("rtable")
    schema = schemata[key]
    url = schema["url"]
    if "parameters" in schema:
        for k in schema["parameters"]:
            assert k in kwargs
        url = url.format(**kwargs)
    path = download(url)

    kwargs = {
        "compression": "gzip" if url.endswith(".gz") else None,
        "encoding": "utf-8"
    }

    columns = schema.get("columns")
    if isinstance(columns, dict):
        kwargs["names"] = list(schema["columns"].keys())
        kwargs["dtype"] = dict([(k,eval(v[1])) for k,v in schema["columns"].items()])
        kwargs["usecols"] = [v[0] for v in schema["columns"].values()]
        assert list(sorted(kwargs["usecols"])) == kwargs["usecols"]
    elif isinstance(columns, list):
        kwargs["names"] = columns

    if "kwargs" in schema:
        assert isinstance(schema["kwargs"], dict)
        kwargs.update(schema["kwargs"])

    archive = schema.get("archive")
    if archive is None:
        df = pd.read_table(path, **kwargs)
    else:
        type = archive["type"]
        name = archive["name"]
        if type == "zip":
            with zipfile.ZipFile(path) as obj:
                with obj.open(name) as h:
                    df = pd.read_table(h, **kwargs)
        else:
            raise NotImplementedError

    index_columns = schema.get("index")
    if index_columns is not None:
        df.drop_duplicates(index_columns, inplace=True)
        df = df.set_index(index_columns)

    return df


