from os import getenv
from os.path import dirname, abspath, isabs, join
import yaml
from fabric.api import env

def mkabs(home, path):
    return path if isabs(path) else join(home, path)

def fabex_config(config=None, config_file=None):
    """Use config or fabex config file, hand it off env.fabex_config"""
    if config:
        env.fabex_config = config
    else:
        config_file = config_file or getenv('FABEX_CONFIG', 'fabex_config.yaml')
        with open(config_file) as f:
            env.fabex_config = yaml.load(f)

    home = env.fabex_config['fabfile_home'] = dirname(env.real_fabfile)
    env.fabex_config['target_dir'] = env.fabex_config.get('target_dir', 'targets')
    env.fabex_config['template_dir'] = env.fabex_config.get('template_dir', 'templates')

    # if env.roles set from cl or top of fabfile we populate env.roledefs, so
    # role based task selection
    if env.roles:
        env.roledefs = { role: list() for role in env.roles }
    if 'template_config' in env.fabex_config:
        with open(env.fabex_config['template_config']) as f:
            env.fabex_templates = yaml.load(f)
    else:
        env.fabex_templates = {}
