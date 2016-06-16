import os
import sys

try:
    import pkg_resources

    d = pkg_resources.get_distribution('metermaid')
    pkg_locations = (
        os.path.join(d.location, 'config'),
        os.path.join(os.path.dirname(d.location), 'config'),
    )
except ImportError:
    pkg_locations = ()


def get_config_paths(filename=None):
    script_name = os.path.basename(sys.argv[0])

    for dirpath in pkg_locations + (
            os.path.join(sys.prefix, 'config'),
            os.path.join(sys.prefix, 'etc', script_name),
            os.path.expanduser('~/.{}'.format(script_name)),
            ):
        full_path = dirpath

        if filename:
            full_path = os.path.join(full_path, filename)

        yield full_path
