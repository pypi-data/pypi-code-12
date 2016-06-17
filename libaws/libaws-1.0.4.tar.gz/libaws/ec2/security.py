import argparse
from libaws.common.logger import logger
from libaws.common.boto import *
from adapter import *

def create_security_group(d):

    params = d['input']
    groupname = str(params['groupname'])
    description = str(params['description'])

    try:
        vpc_id = get_value(params,'vpc_id')
        response = client_ec2.create_security_group(
            VpcId = vpc_id,
            GroupName = groupname,
            Description = description
        )

        group_id = response['GroupId']
        if params.has_key('inbounds'):
            inbounds = params['inbounds']
            for inbound in inbounds:
                inbound = inbound['inbound']
                protocol = inbound['protocol']
                fromport = inbound['fromport']
                toport = inbound['toport']
                cidr = inbound['cidr']
                client_ec2.authorize_security_group_ingress(GroupId=group_id,IpProtocol = protocol,
                    FromPort = fromport,CidrIp = cidr,ToPort = toport,
                ) 
        if params.has_key('outbounds'):
            outbounds = params['outbounds']
            for outbound in outbounds:
                outbound = outbound['outbound']
                protocol = outbound['protocol']
                fromport = outbound['fromport']
                toport = outbound['toport']
                cidr = outbound['cidr']
                client_ec2.authorize_security_group_egress(GroupId=group_id,IpProtocol = protocol,
                    FromPort = fromport,CidrIp = cidr,ToPort = toport,
                ) 

    except Exception,e:
        logger.error('%s',e)
        logger.error("create security group %s in vpc_id %s fail",groupname,vpc_id)
        return False

    tags = get_common_tags(params)
    if len(tags) > 0:
        client_ec2.create_tags(Resources=[group_id],Tags=tags)

    if not confirm_common_response(d,response):
        logger.error("create security group %s fail",groupname)
        return False

    logger.info("create security group %s in vpc_id %s success",groupname,vpc_id)
    return True

def create_all_security_group_from_config(yaml_config_path):
    create_all_from_config(yaml_config_path,'security',create_security_group)    

def create_default_security_group_from_config(yaml_config_path):
    return create_default_from_config(yaml_config_path,'security',create_security_group)    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", type=str, dest="config_file_path", required=True)
    args = parser.parse_args()
    yaml_config_path = args.config_file_path
    create_all_security_group_from_config(yaml_config_path)

if __name__ == "__main__":
    main()


