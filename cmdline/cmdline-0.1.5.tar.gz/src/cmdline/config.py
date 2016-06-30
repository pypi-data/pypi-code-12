import os
import sys

CONFIG_ROOT = 'CMDLINE_CONFIG_ROOT'


def get_config_paths(filename=None, reversed=False):
    config_paths = []

    script_name = os.path.basename(sys.argv[0])

    config_root = os.environ.get(CONFIG_ROOT)
    if config_root:
        if not os.path.exists(config_root):
            raise OSError('{}={} does not exist'.format(CONFIG_ROOT, config_root))

        pkg_locations = (
            config_root,
        )
    else:
        pkg_locations = ()

    # handle debian/ubuntu strangeness where `pip install` will install
    # to /usr/local, yet sys.prefix is /usr
    prefix = sys.prefix
    if not os.path.exists(os.path.join(prefix, 'config')):
        _prefix = os.path.join(prefix, 'local')
        if os.path.exists(os.path.join(_prefix, 'config')):
            prefix = _prefix

    for dirpath in pkg_locations + (
            os.path.join(prefix, 'config'),
            os.path.join(prefix, 'etc', script_name),
            os.path.expanduser('~/.{}'.format(script_name)),
            ):
        full_path = dirpath

        if filename:
            full_path = os.path.join(full_path, filename)

        config_paths.append(full_path)

    # The config root given via environment variable should always have
    # precedence, and when asking for the paths in reversed order, the
    # environment's config should still be first
    if config_root and reversed:
        config_paths.append(config_paths.pop(0))

        return config_paths[-1::-1]

    return config_paths
