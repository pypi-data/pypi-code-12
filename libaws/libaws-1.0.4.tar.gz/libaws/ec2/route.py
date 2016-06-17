import argparse
from libaws.common.logger import logger
from libaws.common.boto import *
from adapter import *

def create_route_table(d):

    params = d['input']
    destination = params['destination']
    gateway_id = params.get('gateway_id',None)
    try:
        vpc_id = get_value(params,'vpc_id')
        vpc = ec2.Vpc(vpc_id)
        if gateway_id is None:
            gateway = ec2.create_internet_gateway()
            gateway.attach_to_vpc(VpcId=vpc_id)
            gateway_id = gateway.id
        route_tables = list(vpc.route_tables.all())
        route_table = route_tables[0]
        route_table.create_route(DestinationCidrBlock=destination,
            GatewayId=gateway_id,
        )
    except Exception,e:
        logger.error('%s',e)
        logger.error("create route destination %s in vpc_id %s fail",destination,vpc_id)
        return False

    tags = get_common_tags(params)
    if len(tags) > 0:
        route_table.create_tags(Tags=tags)

    logger.info("create route destination %s in vpc_id %s success",destination,vpc_id)
    return True

def create_all_routetable_from_config(yaml_config_path):
    create_all_from_config(yaml_config_path,'route',create_route_table)

def create_default_routetable_from_config(yaml_config_path):
    return create_default_from_config(yaml_config_path,'route',create_route_table)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", type=str, dest="config_file_path", required=True)
    args = parser.parse_args()
    yaml_config_path = args.config_file_path
    create_all_routetable_from_config(yaml_config_path)

if __name__ == "__main__":
    main()


