import os
import json

CONCORD_FILENAME = '.concord.cfg'

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

def default_options(opts):
    location = find_config(os.getcwd(), CONCORD_FILENAME)
    if location is None:
        return
    with open(location, 'r') as data_file:
        config_data = json.load(data_file)
    opts_methods = dir(opts)
    opts.zookeeper = config_data['zookeeper_hosts'] if opts.zookeeper is None \
                     else opts.zookeeper
    opts.zk_path =  config_data['zookeeper_path'] if opts.zk_path is None \
                    else opts.zk_path

def default_manifest_options(manifest, all_options):
    location = find_config(os.getcwd(), CONCORD_FILENAME)
    if location is None:
        return
    with open(location, 'r') as data_file:
        config_data = json.load(data_file)
    for option, value in config_data.iteritems():
        if option in all_options and option not in manifest:
            manifest[option] = value
            
def human_readable_units(num, suffix='B'):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Y', suffix)
