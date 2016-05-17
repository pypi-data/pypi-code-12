from collections import OrderedDict
import yaml


def load_yaml(path):
    class OrderedLoader(yaml.SafeLoader):
        pass
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        lambda loader, node: OrderedDict(loader.construct_pairs(node)))

    with open(path, 'r') as config_in:
        return yaml.load(config_in, OrderedLoader)


def load_yaml_config(path):
    from .configure import Configuration
    return Configuration.from_file(path).configure()


class Namespace(object):
    """
    Basic class that allows setting and getting variables as fields
    """
    pass


def get_free_port():
    """
    Find the open port and return it's number
    """
    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


def chunks(l, n):
    """
    Yield successive n-sized chunks from l.
    """
    for i in range(0, len(l), n):
        yield l[i: i + n]


def ordered_dict(seq):
    """
    Construct an ordered dictionary from a sequence of tuples.
    Should ONLY be used in the YAML.configure context
    """
    return OrderedDict(seq)