import argparse
import os
import threading,time
from libaws.common.logger import logger,enable_debug_log
from libaws.common.boto import *
from adapter import *
import vpc 
from libaws.base import utils
from libaws.common import config
from libaws.common.db import Ec2InstanceDb

instance_db = Ec2InstanceDb.get_db()

def create_key_pair(key,delete_exists=False,path="."):

    path = os.path.abspath(path)
    if not os.path.exists(path):
        utils.mkdirs(path)

    if delete_exists:
        client_ec2.delete_key_pair(KeyName=key)

    response = client_ec2.create_key_pair(KeyName=key)
    pem_file_name = key + "." + "pem"
    pem_file_path = os.path.join(path,pem_file_name)

    if os.path.exists(pem_file_path):
        os.remove(pem_file_path)

    with open(pem_file_path,"w") as f:
        f.write(response['KeyMaterial'])
    os.popen('chmod 400 %s' % (pem_file_path))

    return pem_file_path 

def get_key_pair(d):

    if not d.has_key('keypair'):
        return None,None

    keypair = d['keypair']
    keyname = keypair['key'] 
    path = "."
    delete_exists = False
    if keypair.has_key('path'):
        path = keypair['path']
    
    path = get_convert_default_data_path(path)
    if keypair.has_key('delete_exists'):
        delete_exists = bool(keypair['delete_exists'])
    
    pem_file_path = create_key_pair(keyname,delete_exists,path)
    return keyname,pem_file_path

def create_vpc(d):

    if not d.has_key('vpc'):
        return True
    params = d['vpc']

    vpc_config_file = params['from_config']
    vpc_config_file = get_convert_default_data_path(vpc_config_file)
    vpc_data_name = None

    if params.has_key('name'):
        return vpc.create_one_vpc_from_config(vpc_config_file,params['name'])
    else:
        return vpc.create_default_vpc_from_config(vpc_config_file)

def get_volumes(d):
    if not d.has_key('volumes'):
        return None
    volumes = d['volumes']
    volume_list = []
    for volume in volumes: 
        size = int(volume['volume']['size'])
        name = volume['volume']['name']
        ebs = {}
        ebs_volume= {}
        ebs_volume['VolumeSize'] = size
        if volume.has_key('type'):
            ebs_volume['VolumeType'] = volume['volume']['type']

        ebs['Ebs'] = ebs_volume
        ebs['DeviceName'] = name 
        volume_list.append(ebs)
    
    device_maps = {
            'BlockDeviceMappings':volume_list
    }
    return device_maps

def create_instance(d,only_check=False,save_instance_info=False):
    
    global instance_db

    params = d['input']
    name = params['name']
    number = get_int_value(params,'number',1)
    instance_type = get_value(params,'instance_type','t2.micro')
    if not create_vpc(d):
        logger.error("create instance %s type %s number %d fail",name,instance_type,number)
        return [],None

    try:
        keyname,pem_file_path = get_key_pair(d)
    except Exception,e:
        logger.error("%s",e)
        logger.error("create keypair %s fail",d['keypair']['key'])
        return [],None

    tags = get_common_tags(params)
    image_id = get_value(params,'image_id')
    if keyname is None:
        keyname = get_value(params,'keyname')
        pem_file_path = keyname + ".pem"

    subnet_id = get_value(params,'subnet_id')
    if subnet_id is None:
        logger.error("cannt find subnet_id value")
        return [],None
    security_group_ids = get_value(params,'security_group_ids')

    device_maps = get_volumes(d)
    if not only_check:
        try:
            args = {
                'ImageId':image_id,
                'MinCount':number,
                'MaxCount': number,
                'KeyName': keyname,
                'SecurityGroupIds' : security_group_ids,
                'SubnetId':subnet_id,
                'InstanceType':instance_type
            }
            if device_maps is not None:
                args.update(device_maps)

            instance_list = ec2.create_instances(**args)
        except Exception,e:
            logger.error('%s',e)
            logger.error("create instance %s type %s number %d fail",name,instance_type,number)
            return []

        if len(tags) > 0:
            instance_ids = []
            for instance in instance_list:
                instance_id = instance.id
                instance_ids.append(instance_id)
            client_ec2.create_tags(Resources=instance_ids,Tags=tags)
        logger.info("create instance %s type %s number %d success",name,instance_type,number)

    if save_instance_info:
        instance_db.save_config(image_id,keyname,security_group_ids[0],subnet_id,pem_file_path)
    return instance_list,pem_file_path

def ssh_connect_instance(instance,pem_file_path):

    def waitfor_instance_run(instance_id):
        while True:
            instance = ec2.Instance(instance_id)
            state_name = instance.state['Name']
            if state_name == 'running':
                logger.info('instance %s is state %s ,start to connect',instance.id,state_name)
                time.sleep(8)
                break
            logger.info('instance %s state %s',instance.id,state_name)
            time.sleep(1)

    if instance is None:
        logger.error("can not connect none instance")
        return

    instance_id = instance.id
    t = threading.Thread(target=waitfor_instance_run,args=(instance_id,))
    t.daemon = True
    t.start()
    t.join(60)

    instance = ec2.Instance(instance_id)
    public_ip = instance.public_ip_address 
    cmd = "ssh -i %s ubuntu@%s" % (pem_file_path,public_ip)
    logger.info("%s",cmd)
    os.system(cmd)

def create_all_instance_from_config(yaml_config_path):
    create_all_from_config(yaml_config_path,'instance',create_instance)
    
def create_default_instance_from_config(yaml_config_path):
    try:
        nodes = load_yaml_config(yaml_config_path)
    except Exception,e:
        logger.error("%s",e)
        return None,None

    d = nodes[0]['instance']
    instances,pem_file_path = create_instance(d,save_instance_info=True)
    if 0 == len(instances):
        return None,None

    return instances[0],pem_file_path 

def lanuch_default_instance():
    
    data_dir = os.path.abspath(os.path.split(__file__)[0])
    default_config_path = os.path.join(data_dir,'./data/default_instance_config.yaml')
    return create_default_instance_from_config(default_config_path)

def check_keypair_exists(keyname,key_path_file):

    if not os.path.exists(key_path_file):
        return False
    try:
        key_pair = ec2.KeyPair(keyname)
        key_pair.load()
        return True

    except Exception,e:
        logger.warn("%s",e)
        return False

def launch_one_instance(instance_type,volume_size):

    global instance_db

    result = instance_db.load_default_config()
    if result is None:
        return lanuch_default_instance()
    else:
        subnet_id,keyname,security_group_id,image_id,key_path_file = result
        if not check_keypair_exists(keyname,key_path_file):
            key_path = os.path.dirname(key_path_file)
            key_path_file = create_key_pair(keyname,True,path=key_path)

        try:
            args = {
                'ImageId':image_id,
                'MinCount':1,
                'MaxCount': 1,
                'KeyName': keyname,
                'SecurityGroupIds' : [security_group_id],
                'SubnetId':subnet_id,
                'InstanceType':instance_type,
                'BlockDeviceMappings':[
                    {
                        'Ebs':{
                            'VolumeSize':volume_size
                        },
                        'DeviceName':'/dev/sda1' 
                    }
                ]
            }
            instance_list = ec2.create_instances(**args)
            logger.info("create instance type %s success",instance_type)
            return instance_list[0],key_path_file
        except Exception,e:
            logger.warn("%s",e)
            return lanuch_default_instance()

def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", type=str, dest="config_file_path")
    parser.add_argument("-launch-one-instance", action='store_true', dest="is_launch_one_instance",default=False)
    parser.add_argument("-type", type=str, dest="instance_type",default=config.DEFAULT_INSTANCE_TYPE)
    parser.add_argument("-volume", type=int, dest="instance_volume_size",default=config.DEFAULT_INSTANCE_VOLUME_SIZE)
    parser.add_argument("-connect-after-launch", action='store_true', dest="is_connect_after_lauch",default=False)
    enable_debug_log(True)
    args = parser.parse_args()
    if args.is_launch_one_instance:
        instance,key_path = launch_one_instance(args.instance_type,args.instance_volume_size)
        if args.is_connect_after_lauch:
            ssh_connect_instance(instance,key_path)
    else:
        yaml_config_path = args.config_file_path
        create_all_instance_from_config(yaml_config_path)

if __name__ == "__main__":
    main()
    
