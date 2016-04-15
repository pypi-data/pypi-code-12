
# -*- coding:utf-8 -*-

from ..util import client,config, formater, oss_client,util
from terminal import bold, magenta, white, blue, green,red, yellow, confirm
import json
import os
import uuid
import tarfile
import glob
from ..const import IMG_ID,INS_TYPE,CMD



try:
    import ConfigParser
except:
    import configparser as ConfigParser
cf = ConfigParser.ConfigParser()



DEFAULT_CLUSTER = "img=%s:type=%s" % (IMG_ID,INS_TYPE)

def submit(cmd=None, job_name='cli-job', description='BatchCompute cli job', cluster=DEFAULT_CLUSTER, timeout=172800, nodes=1,
           force=False, docker=None, file=None, pack=None, env=None, read_mount={}, write_mount={}, mount=None, show_json=None):

    if not cmd and not file:
        raise Exception('Missing argument: cmd')


    if job_name.startswith('-'):
        raise Exception('Invalid job_name')

    pre_oss_path = config.get_oss_path()

    job_desc = gen_job_desc(job_name, description)

    #######################
    if file:
        if file.get('cmd'):
            cmd=file.get('cmd')
        if file.get('job_name'):
            job_name = file.get('job_name')
        if file.get('description'):
            description = file.get('description')
        if file.get('cluster'):
            cluster = file.get('cluster')
        if file.get('timeout'):
            timeout = trans_timeout(file.get('timeout'))
        if file.get('nodes'):
            nodes = trans_nodes(file.get('nodes'))

        if file.get('force')!=None:
            force = (file.get('force'))
        if file.get('docker'):
            docker = trans_docker(file.get('docker'))
        if file.get('env'):
            env = trans_env(file.get('env'))
        if file.get('read_mount'):
            read_mount = trans_mount(file.get('read_mount'))
        if file.get('write_mount'):
            write_mount = trans_mount(file.get('write_mount'))
        if file.get('mount'):
            mount = trans_mount(file.get('mount'))



    #######################
    if job_name:
        job_desc['Name'] = job_name
    if description:
        job_desc['Description'] = description

    job_desc['DAG']['Tasks']['task']['Parameters']['Command']['CommandLine']=cmd

    cluster = util.parse_cluster_cfg(cluster)
    for (k,v) in cluster.items():
        job_desc['DAG']['Tasks']['task'][k]=v


    job_desc['DAG']['Tasks']['task']['Timeout']=timeout
    job_desc['DAG']['Tasks']['task']['InstanceCount']=nodes

    if env:
        job_desc['DAG']['Tasks']['task']['Parameters']['Command']['EnvVars']=env

    if docker:
        for (k,v) in docker.items():
            job_desc['DAG']['Tasks']['task']['Parameters']['Command']['EnvVars'][k]=v


    if mount:
        for k,v in mount.items():
            read_mount[k]=v
            write_mount[k]=v

    if read_mount:
        job_desc['DAG']['Tasks']['task']['InputMapping']=read_mount
    if write_mount:
        job_desc['DAG']['Tasks']['task']['OutputMapping']=reverse_kv(write_mount)


    rand = gen_rand_id()

    # pack, upload

    if pack:
        package_path = '%s%s/worker.tar.gz' % (pre_oss_path,rand)
        if ',' in pack:
            arr = pack.split(',')
            build_tar_from_arr_and_upload(arr, package_path)
        else:

            folder_path = formater.get_abs_path(pack)
            if os.path.isdir(folder_path):
                build_tar_from_dir_and_upload(folder_path, package_path)
            else:
               build_tar_from_arr_and_upload([pack],package_path)


        job_desc['DAG']['Tasks']['task']['Parameters']["Command"]['PackagePath'] = package_path

    job_desc['DAG']['Tasks']['task']['Parameters']['StdoutRedirectPath'] = '%s%s/logs/' % (pre_oss_path,rand)
    job_desc['DAG']['Tasks']['task']['Parameters']['StderrRedirectPath'] = '%s%s/logs/' % (pre_oss_path,rand)

    if force:
        job_desc['JobFailOnInstanceFail'] = False





    if show_json:
        print(json.dumps(job_desc, indent=4))
    else:
        result = client.create_job(job_desc)

        if result.StatusCode==201:
            print(green('Job created: %s' % result.Id))



def trans_file(file):

    cfg_path = os.path.join(os.getcwd(), file)

    if  not os.path.exists(cfg_path):
        raise Exception('Invalid file: %s' % cfg_path)

    cf.read(cfg_path)
    m = {}
    arr = cf.sections()
    for name in arr:
        items = cf.items(name)
        for (k,v) in items:
            m[k]=v
    return m



def gen_job_desc(job_name, description):

    task = {
        "OutputMapping": {},
        "Timeout": 172800,
        "InputMapping": {},
        "LogMapping": {},
        "InstanceCount": 1,
        # "ClusterId": "",
        # "AutoCluster": {
        #     "InstanceType":"ecs.s3.large",
        #     "ECSImageId": "m-287zklx8l",
        #     "ResourceType": "OnDemand"
        # },
        "MaxRetryCount": 0,
        "Parameters": {
            "StderrRedirectPath": "",
            "InputMappingConfig": {
                "Locale": "GBK",
                "Lock": False
            },
            "StdoutRedirectPath": "",
            "Command": {
                "EnvVars": {},
                "CommandLine": "",
                "PackagePath": ""
            }
        },
        "WriteSupport": True
    }
    return {
        "DAG": {
            "Tasks": {
                'task': task
            },
            "Dependencies": {}
        },
        "Description": description,
        "JobFailOnInstanceFail": True,
        "Priority": 1,
        "Type": "DAG",
        "Name": job_name
    }

def trans_nodes(n):
    try:
        n = int(n)
        return n if n > 0 else 1
    except:
        return 1

def trans_timeout(n):
    try:
        n = int(n)
        return n if n > 0 else 172800
    except:
        return 172800




def trans_docker(docker=None):
    return util.trans_docker(docker)


def trans_env(s):
    if not s:
        return None
    arr = s.split(',')
    env = {}
    for item in arr:
        [k,v]=item.split(':',1)
        env[k]=v
    return env

def trans_mount(s):
    return util.trans_mount(s)

def reverse_kv(m):
    m2={}
    for k,v in m.items():
        m2[v]=k
    return m2

def gen_rand_id():
    return uuid.uuid1()





def build_tar_from_dir_and_upload(folder_path, oss_path):
    '''
    pack program files, and upload to oss_path
    :param folder_path:
    :param oss_path:
    :return:
    '''

    dist = os.path.join(os.getcwd(), 'worker.tar.gz')


    # cd
    #os.chdir(folder_path)

    # tar
    print('pack %s' % dist)
    with tarfile.open(dist, 'w|gz') as tar:
        for root,dir,files in os.walk(folder_path):
            for file in files:
                fullpath=os.path.join(root,file)
                print('add %s' % fullpath)
                tar.add(fullpath,arcname=file)

    # upload
    print('Upload: %s ==> %s' % (dist, oss_path))
    oss_client.upload_file( dist, oss_path)


def build_tar_from_arr_and_upload(arr, oss_path):
    dist = os.path.join(os.getcwd(), 'worker.tar.gz')

     # tar
    print('pack %s' % dist)
    with tarfile.open(dist, 'w|gz') as tar:
        for file in arr:
            fullpath = formater.get_abs_path(file)
            print('add %s' % fullpath)
            tar.add(fullpath,arcname=file)
    # upload
    print('Upload: %s ==> %s' % (dist, oss_path))
    oss_client.upload_file( dist, oss_path)