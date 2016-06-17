import argparse
from adapter import *
from libaws.common.logger import logger
from libaws.common.boto import *

def create_subnet(d,only_check=False):
    params = d['input']

    cidr = get_value(params,'cidr') + "/" + str(get_value(params,'mask'))
    vpc_id = get_value(params,'vpc_id')
    try:
        response = client_ec2.create_subnet(VpcId=vpc_id,CidrBlock=cidr)
    except Exception,e:
        logger.error('%s',e)
        logger.error("create subnet cidr %s in vpc_id %s fail",cidr,vpc_id)
        return False
    
    subnet_id = response['Subnet']['SubnetId']
    tags = get_common_tags(params)
    if len(tags) > 0:
        client_ec2.create_tags(Resources=[subnet_id],Tags=tags)

    if params.has_key('publicip'):
        assgin_public_ip = bool(params['publicip'])
        client_ec2.modify_subnet_attribute(SubnetId=subnet_id, MapPublicIpOnLaunch={
            'Value':assgin_public_ip}
        )
    
    if not confirm_common_response(d,response):
        logger.error("create subnet cidr %s fail",cidr)
        return False

    logger.info("create subnet cidr %s in vpc_id %s success",cidr,vpc_id)
    return True

def create_all_subnet_from_config(yaml_config_path):
    create_all_from_config(yaml_config_path,'subnet')

def create_one_subnet_from_config(yaml_config_path,name):
    return create_one_from_config(yaml_config_path,'subnet',name,create_subnet)
    
def create_default_subnet_from_config(yaml_config_path):
    return create_default_from_config(yaml_config_path,'subnet',create_subnet)

def check_one_subnet_from_config(yaml_config_path,name = None):
    check_one_from_config(yaml_config_path,'subnet',name,create_subnet)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", type=str, dest="config_file_path", required=True)
    args = parser.parse_args()
    yaml_config_path = args.config_file_path
    create_all_subnet_from_config(yaml_config_path)
    
if __name__ == "__main__":
    main()


