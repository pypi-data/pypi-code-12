import os
import sys


def get_config_paths(filename=None):
    script_name = os.path.basename(sys.argv[0])

    for dirpath in (
            os.path.join(sys.prefix, 'config'),
            '/etc/{}'.format(script_name),
            os.path.expanduser('~/.{}'.format(script_name)),
            ):
        full_path = dirpath

        if filename:
            full_path = os.path.join(full_path, filename)

        yield full_path
