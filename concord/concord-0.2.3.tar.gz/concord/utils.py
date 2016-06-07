import os
import json
import logging
from concord.dcos_utils import *

CONCORD_FILENAME = '.concord.cfg'

CONCORD_DEFAULTS = { 'zookeeper_path' : '/concord',
                     'zookeeper_hosts' : 'localhost:2181' }

def build_logger(module_name, fmt_string=None):
    if fmt_string is not None:
        logging.basicConfig(format=fmt_string)
    else:
        logging.basicConfig()
    logger = logging.getLogger(module_name)
    level = logging.INFO if 'DCOS_LOG_LEVEL' not in os.environ else \
            os.environ['DCOS_LOG_LEVEL']
    logger.setLevel(level)
    return logger

def find_config(src, config_file):
    """ recursively searches .. until it finds a file named config_file
    will return None in the case of no matches or the abspath if found"""
    filepath = os.path.join(src, config_file)
    if os.path.isfile(filepath):
        return filepath
    elif src == '/':
        return None
    else:
        return find_config(os.path.dirname(src), config_file)

def fetch_config_opts(src, config_file):
    if ON_DCOS is True:
        return dcos_config_data()

    location = find_config(os.getcwd(), CONCORD_FILENAME)
    config_data = {}
    if location is None:
        config_data = CONCORD_DEFAULTS
    else:
        with open(location, 'r') as data_file:
            config_data = json.load(data_file)
    return config_data
    
def default_options(opts):
    config_data = fetch_config_opts(os.getcwd(), CONCORD_FILENAME)
    opts_methods = dir(opts)
    opts.zookeeper = config_data['zookeeper_hosts'] if opts.zookeeper is None \
                     else opts.zookeeper
    opts.zk_path =  config_data['zookeeper_path'] if opts.zk_path is None \
                    else opts.zk_path

def default_manifest_options(manifest, all_options):
    config_data = fetch_config_opts(os.getcwd(), CONCORD_FILENAME)
    for option, value in config_data.iteritems():
        if option in all_options and option not in manifest:
            manifest[option] = value
            
def human_readable_units(num, suffix='B'):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Y', suffix)
