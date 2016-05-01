import os

from ._read_dot_env import read_file_values
from ._environ import _Environment


def initialize_env(env_file=None, fail_silently=True, load_globally=True):
    """
    Returns an instance of _Environment after reading the system environment an
    optionally provided file.
    """
    data = {}
    data.update(os.environ)
    if env_file:
        data.update(read_file_values(env_file, fail_silently))

    if load_globally:
        os.environ.update(data)

    return _Environment(env_dict=data)
