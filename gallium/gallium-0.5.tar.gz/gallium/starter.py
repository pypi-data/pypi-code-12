import codecs
import json
import os
import sys

from gallium                    import Console, Core
from gallium.loader.basic       import Loader as BasicLoader
from gallium.loader.imagination import Loader as ImaginationLoader

base_path = os.path.abspath(os.getcwd())

global_base_path        = '/usr/local/gallium'
global_config_path      = os.path.join(global_base_path, 'etc')
global_config_file_path = os.path.join(global_config_path, 'config.json')
default_user_home_path  = os.path.join(os.getenv('HOME'), '.gallium')
user_home_path          = os.getenv('GALLIUM_HOME') or default_user_home_path
user_config_file_path   = os.path.join(user_home_path, 'config.json')

symlinks = {
    global_config_path: '/etc/gallium',
}

def __p(path):
    return os.path.join(base_path, path)

def __update_config(base_config, updating_config):
    for section in ['extensions', 'paths', 'services', 'imports', 'settings']:
        extending_list = updating_config[section] if section in updating_config else []

        if not extending_list:
            continue

        if section not in base_config:
            base_config[section] = []

        base_config[section].extend(extending_list)
        base_config[section] = list(set(base_config[section]))

def __is_readable(path):
    return os.path.exists(path) and os.access(path, os.R_OK)

def __can_read_any_of(*paths):
    readable_paths = []

    for path in paths:
        if __is_readable(path):
            readable_paths.append(os.path.abspath(path))

    return readable_paths

def load_config():
    # Ensure that the base path is at the top of the Python paths.
    if base_path not in sys.path:
        sys.path.insert(0, base_path)

    # Load configuration files.
    local_config_path = os.getenv('GALLIUM_CONF') \
        or os.getenv('GA_CONF') \
        or __p('cli.json')

    seeking_config_files = [local_config_path, user_config_file_path, global_config_file_path]
    readable_file_paths  = __can_read_any_of(*seeking_config_files)

    cli_config = {}

    if not readable_file_paths:
        raise IOError('{} is not readable.'.format(seeking_config_files[0]))

    for readable_file_path in readable_file_paths:
        with codecs.open(readable_file_path, 'r') as f:
            file_cli_config = json.load(f)

            __update_config(
                cli_config,
                file_cli_config
            )

    # Extends Python paths.
    if 'paths' in cli_config:
        sys.path.extend(cli_config['paths'])

    return {
        'content':    cli_config,
        'local_path': local_config_path,
    }

def main():
    console_name = __package__ or sys.argv[0]
    config       = load_config()

    # Initialize the Gallium core.
    framework_core = Core()

    basic_loader       = BasicLoader()
    imagination_loader = ImaginationLoader(framework_core)

    enabled_loaders = [
        basic_loader,
        imagination_loader
    ]

    console = Console(
        name        = console_name,
        core        = framework_core,
        config      = config['content'],
        config_path = config['local_path'],
        loaders     = enabled_loaders
    )

    console.activate()
