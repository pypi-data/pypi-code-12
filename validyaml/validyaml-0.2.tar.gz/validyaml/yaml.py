from ruamel import yaml as ruamelyaml


def load(stream):
    """
    Parse the first YAML document in a stream
    and produce the corresponding Python object.
    """
    return ruamelyaml.load(stream, Loader=ruamelyaml.RoundTripLoader)
