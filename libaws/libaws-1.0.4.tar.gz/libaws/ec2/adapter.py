import os
import yaml
from libaws.common.logger import logger
from libaws.common import config

global_data = {}

def load_yaml_config(yaml_config_file):

    f = open(yaml_config_file)
    nodes = yaml.load(f)
    f.close()

    return nodes 



def get_value(d,name,default_value=None):

    global global_data
    if not d.has_key(name):
        return default_value

    dist = d[name]
    if isinstance(dist,dict):
        if dist.has_key('value'):
            return dist['value']
        else:
            key = dist['from']
            if isinstance(key,list):
                values = []
                for l in key:
                    values.append(global_data.get(l,None))
                return values
            else: 
                return global_data.get(key,None)
    else:
        return dist

def get_int_value(d,name,default_value=None):
    return int(get_value(d,name,default_value))

def set_global_data(key,value):

    global global_data
    global_data[key] = value

def confirm_response_param(expert_data,data):

    for param in expert_data.keys():
        if data is not None:
            data_value = data[param]
        else:
            data_value = None

        expert_data = expert_data[param]
        if expert_data.has_key('export'):
            export_data_name = expert_data['export']
            set_global_data(export_data_name,data_value)
        
        elif type(expert_data).__name__ == 'dict':
            confirm_response_param(expert_data,data_value)

def confirm_common_response(config_data,response=None):
    try:
        if config_data.has_key('response'):
            response_data = config_data['response']
            confirm_response_param(response_data,response)
    except Exception,e:
        logger.error("%s",e)
        return False

    return True

def get_common_tags(params):

    tags = []
    if params.has_key('tags'):
        param_tags = params['tags']
        for param_tag in param_tags:
            param_tag = param_tag['tag']
            tag = {
                'Key':str(param_tag['key']),
                'Value':str(param_tag['value'])
            }
            tags.append(tag)
 
    return tags

def create_all_from_config(yaml_config_path,config_name,create_func):

    try:
        nodes = load_yaml_config(yaml_config_path)
    except Exception,e:
        logger.error("%s",e)
        return

    for node in nodes:
        d = node[config_name]
        create_func(d)

def get_config_by_name(yaml_config_path,config_name,config_name_name):
    
    try:
        nodes = load_yaml_config(yaml_config_path)
    except Exception,e:
        logger.error("%s",e)
        return

    for node in nodes:
        d = node[config_name]
        if d['name'] == config_name_name:
            return d

    return None

def create_one_from_config(yaml_config_path,config_name,config_name_name,create_func):

    d = get_config_by_name(yaml_config_path,config_name,config_name_name)
    if d is None:
        logger.error('can not find %s name %s in config %s',config_name,config_name_name,yaml_config_path)
        return False

    return create_func(d)
    
def create_default_from_config(yaml_config_path,config_name,create_func):

    try:
        nodes = load_yaml_config(yaml_config_path)
    except Exception,e:
        logger.error("%s",e)
        return False

    d = nodes[0][config_name]
    return create_func(d)

def check_one_from_config(yaml_config_path,config_name,create_func,config_name_name = None):
    
    try:
        nodes = load_yaml_config(yaml_config_path)
    except Exception,e:
        logger.error("%s",e)
        return False

    if name is None:
        d = get_config_by_name(yaml_config_path,nodes[0]['name'])
    else:
        d = get_config_by_name(yaml_config_path,name)
    
    if d is None:
        logger.error('can not find %s name %s in config %s',config_name,config_name_name,yaml_config_path)
        return

    return create_func(d,True)

def check_all_from_config(yaml_config_path,config_name,create_func):

    try:
        nodes = load_yaml_config(yaml_config_path)
    except Exception,e:
        logger.error("%s",e)
        return

    for node in nodes:
        d = node[config_name]
        create_func(d,True)


def get_convert_default_data_path(src_path):

    if src_path.find(config.DEFAULT_DATA_DIR_FLAG) != -1:
        data_dir = os.path.abspath(os.path.split(__file__)[0])
        dest_path = src_path.replace(config.DEFAULT_DATA_DIR_FLAG,data_dir)
        return dest_path
    else:
        return src_path

