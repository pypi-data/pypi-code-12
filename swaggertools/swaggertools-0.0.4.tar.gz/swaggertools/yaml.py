import yaml as _
from .bases import SwaggerMapping, ModelRef
from collections.abc import Mapping

__all__ = ['dump', 'load', 'Dumper', 'Loader']

_Loader = getattr(_, 'CSafeLoader', _.SafeLoader)
_Dumper = getattr(_, 'CSafeDumper', _.SafeDumper)


class Loader(_Loader):
    pass


def construct_mapping(loader, node):
    loader.flatten_mapping(node)
    return SwaggerMapping(loader.construct_pairs(node))

Loader.add_constructor('tag:yaml.org,2002:map', construct_mapping)
Loader.add_constructor('tag:yaml.org,2002:omap', construct_mapping)


def load(stream, Loader=Loader, **kwargs):
    return _.load(stream, Loader, **kwargs)


class Dumper(_Dumper):
    pass


def dict_representer(dumper, data):
    flow_style=False
    if len(data) == 1:
        for k, v in data.items():
            flow_style = isinstance(v, str) and '\n' not in v
            break
    return dumper.represent_mapping('tag:yaml.org,2002:map',
                                    data.items(),
                                    flow_style=flow_style)


def model_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data)


def list_representer(dumper, data):
    return dumper.represent_sequence(u'tag:yaml.org,2002:seq', sorted(data))


def str_representer(dumper, data):
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

Dumper.add_multi_representer(Mapping, dict_representer)
Dumper.add_representer(str, str_representer)
Dumper.add_representer(SwaggerMapping, dict_representer)
Dumper.add_representer(ModelRef, model_representer)
Dumper.add_representer(set, list_representer)


def dump(data, stream=None, Dumper=Dumper, **kwargs):
    return _.dump(data, stream, Dumper, **kwargs)
