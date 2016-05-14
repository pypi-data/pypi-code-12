###########################################
# This is very naive replacement algorithm
# TODO
############################################
import string
import uuid

import ruamel.yaml
from ruamel.yaml.util import load_yaml_guess_indent

def replaceable(code, kv):
    # change keyword to value
    keys = kv.keys()
    # find keyword which is ${keyword}
    # replace value ${keyword} <- kv[keyword]
    for key in keys:
        nkey = "${%s}" % key
        code = string.replace(code, nkey, kv[key])
    print '#' * 40
    print code
    print '#' * 40
    return code

def find_file_path(lookahead):
    print lookahead
    if lookahead == None:
        return None
    ctx = lookahead['text']
    items = ctx.split()
    if items[0] == 'edit':
        return items[1]

def execute_yaml(**kwargs):
    code = kwargs['code']
    kv = kwargs['kv']

    import os
    # call replaceable
    rcode = replaceable(code, kv)

    file_path = find_file_path(kwargs['lookahead'])
    if file_path == None:
        msg = "[DEBUG] I don't know how to edit!"
        print msg
        return msg

    config, ind, bsi = load_yaml_guess_indent(open(file_path))
    config2, ind2, bsi2 = load_yaml_guess_indent(rcode)

    # Overwrite config2 to config
    config.update(config2)

    ruamel.yaml.round_trip_dump(config, open(file_path, 'w'), indent=ind, block_seq_indent=bsi)
    return "Yaml executed"

