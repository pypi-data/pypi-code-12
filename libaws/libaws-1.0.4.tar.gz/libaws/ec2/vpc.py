import argparse
from libaws.common.logger import logger,enable_debug_log
from libaws.common.boto import *
from adapter import *
import subnet,route,security

extra_name_subnet = 'subnet'
extra_name_route = 'route'
extra_name_security = 'security'

def create_extra_config(extra):

    if extra[extra_name_subnet]['create']:
        suc = False
        if not extra[extra_name_subnet].has_key('name'):
            subnet_config_file = extra[extra_name_subnet]['from_config']
            subnet_config_file = get_convert_default_data_path(subnet_config_file)
            suc = subnet.create_default_subnet_from_config(subnet_config_file)
        else:
            suc = subnet.create_subnet_from_config(subnet_config_file,extra[extra_name_subnet]['name'])

        if not suc:
            logger.error("create subnet fail")
            return False

    if extra[extra_name_route]['create']:
        suc = False
        if not extra[extra_name_route].has_key('name'):
            route_config_file = extra[extra_name_route]['from_config']
            route_config_file = get_convert_default_data_path(route_config_file)
            suc = route.create_default_routetable_from_config(route_config_file)
        else:
            suc = route.create_routetable_from_config(subnet_config_file,extra[extra_name_route]['name'])

        if not suc:
            logger.error("create route fail")
            return False
    
    if extra[extra_name_security]['create']:
        suc = False
        if not extra[extra_name_security].has_key('name'):
            security_config_file = extra[extra_name_security]['from_config']
            security_config_file = get_convert_default_data_path(security_config_file)
            suc = security.create_default_security_group_from_config(security_config_file)
        else:
            suc = security.create_security_group_from_config(subnet_config_file,extra[extra_name_security]['name'])

        if not suc:
            logger.error("create security fail")
            return False


def create_vpc(d,only_check=False):

    def get_extra_data(params,name):
        extra_data = {
            'create':False,
            'from_config':None
        }

        if params.has_key(name):
            param_data = params[name]
            extra_config_file = param_data['from_config']
            extra_data_name = None
            if param_data.has_key('name'):
                extra_data_name = param_data['name']
                extra_data['name'] = extra_data_name 
            extra_data['create'] = True
            extra_data['from_config'] = extra_config_file

        return extra_data

    params = d['input']
    cidr = get_value(params,'cidr') + "/" + str(get_value(params,'mask'))
    tags = get_common_tags(params)
    extra = {}
    extra[extra_name_subnet] = get_extra_data(d,extra_name_subnet)
    extra[extra_name_route] = get_extra_data(d,extra_name_route)
    extra[extra_name_security] = get_extra_data(d,extra_name_security)

    if not confirm_common_response(d,None):
        logger.error("create vpc cidr %s fail",cidr)
        return False

    if not only_check:
        try:
            response = client_ec2.create_vpc(CidrBlock=cidr)
        except Exception,e:
            logger.error('%s',e)
            logger.error("create vpc cidr %s fail",cidr)
            return False

        if len(tags) > 0:
            vpc_id = response['Vpc']['VpcId']
            client_ec2.create_tags(Resources=[vpc_id],Tags=tags)

        if not confirm_common_response(d,response):
            logger.error("create vpc cidr %s fail",cidr)
            return False

        logger.info("create vpc cidr %s success",cidr)
        create_extra_config(extra)

    return True

def create_all_vpc_from_config(yaml_config_path):
    create_all_from_config(yaml_config_path,'vpc',create_vpc)
    
def create_default_vpc_from_config(yaml_config_path):
    return create_default_from_config(yaml_config_path,'vpc',create_vpc)

def create_one_vpc_from_config(yaml_config_path,name):
    return create_one_from_config(yaml_config_path,'vpc',name)
    
def check_one_vpc_from_config(yaml_config_path,name = None):
    check_one_from_config(yaml_config_path,'vpc',name)

def check_all_vpc_from_config(yaml_config_path):
    check_all_from_config(yaml_config_path,'vpc')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", type=str, dest="config_file_path", required=True)
    args = parser.parse_args()
    yaml_config_path = args.config_file_path
    enable_debug_log(True)
    create_all_vpc_from_config(yaml_config_path)  

if __name__ == "__main__":
    main()


