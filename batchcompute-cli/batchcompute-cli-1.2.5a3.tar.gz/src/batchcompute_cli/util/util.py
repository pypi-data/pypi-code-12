
# -*- coding: UTF-8 -*-
import json
import os
from ..util import client,it,result_cache
from terminal import white,blue
from ..const import *
import re


def parse_id_arr(arr, type='jobs'):
    t=[]
    arr = _parse_shot_id(arr)

    print(arr)

    for item in arr:
        id = result_cache.get(item, type)
        t.append(id)
    return t

def _parse_shot_id(arr):
    t=[]
    for k in arr:
        if re.match(r"^\d+\-\d+$",k):
            (a,b) = k.split('-')
            t = t + range(int(a),int(b)+1)
        else:
            t.append(k)
    return t

# 检查是否在project目录下运行
def check_is_job_project():
    project_json_path = os.path.join(os.getcwd(),'project.json')
    job_json_path = os.path.join(os.getcwd(),'job.json')

    flag = os.path.exists( project_json_path ) and os.path.exists( job_json_path )
    if not flag:
        raise Exception('This is not a BatchCompute project folder')

    with open(project_json_path, 'r') as f:
        obj = json.loads(f.read())

    return obj.get('type')


def get_cluster_str(task_desc):
    if task_desc.get('ClusterId'):
        return task_desc.get('ClusterId')
    else:
        return "img=%s:type=%s" % (task_desc['AutoCluster']['ECSImageId']or task_desc['AutoCluster']['ImageId'],task_desc['AutoCluster']['InstanceType'])


def parse_cluster_cfg(s=None):
    if not s:
        return {
            'AutoCluster':{
                'ECSImageId': IMG_ID,
                'InstanceType': INS_TYPE
            },
            'ClusterId': ''
        }

    if s.find('=')!=-1:
        arr = s.split(':')
        m={}
        for item in arr:
            if '=' not in item:
                raise Exception('Invalid cluster format')

            [k,v]=item.split('=',1)
            if k=='img':
                m['ECSImageId']=v
            if k=='type':
                m['InstanceType']=v

        m['ECSImageId']= m['ECSImageId'] if  m.get('ECSImageId') else IMG_ID
        m['InstanceType']= m['InstanceType'] if  m.get('InstanceType') else INS_TYPE

        if not it.get_ins_type_map().get(m['InstanceType']):
            raise Exception('Invalid type(InstanceType), type "%s it" for more' % CMD)

        #print(white('using AuthCluster: %s' % m))
        return {'AutoCluster':m,'ClusterId':''}
    else:
        result = client.list_clusters()
        clusters = result.get('Items')
        for c in clusters:
            if c.get('Id')==s:
                #print(white('using Cluster: %s' % s))
                return {'ClusterId':s,'AutoCluster':{}}

        raise Exception('Invalid ClusterId, type "%s c" for more' % CMD)



def trans_mount(s):
    if not s:
        return None
    arr = s.split(',')
    mount = {}
    for item in arr:
        item = item.strip()
        if item.startswith('oss://'):
            ind = item.rfind(':')
            k = item[0:ind]
            v = item[ind+1:]
        else:
            [k,v]=item.split(':',1)
        mount[k]=v
    return mount


def trans_docker(docker=None, ignoreErr=False):
    ind = docker.find('@oss://')
    if ind > 1:

        [k,v]=docker.split('@oss://', 1)
        v = 'oss://%s' % v

        if not k.startswith('localhost:5000/'):
            k = 'localhost:5000/%s' % k
        return {"BATCH_COMPUTE_DOCKER_IMAGE":k, "BATCH_COMPUTE_DOCKER_REGISTRY_OSS_PATH":v}
    else:
        if not ignoreErr:
            raise Exception('Invalid docker option format')


def sort_task_by_deps(arr, matric):
    m = {}
    for n in arr:
        m[n['TaskName']]=n

    t=[]
    for items in matric:
        for taskname in items:
            t.append(m[taskname])
    return t


def get_task_deps(dag):
    deps = dag.get('Dependencies') or {}
    tasks = dag.get('Tasks')

    m = {}
    for k in tasks:
        m[k] = []

    for k in m:
        if not deps.get(k):
            deps[k] = []

    return deps

def print_inst_result(result):

    print('%s : %s' % (blue('ExitCode'), result.ExitCode))
    print('%s : %s' % (blue('ErrorCode'), result.ErrorCode))
    print('%s : %s' % (blue('ErrorMessage'), result.ErrorMessage))
    print('%s : %s' % (blue('Detail'), result.Detail))



def trans_disk(disk):

    try:
        infos = disk.split(',')

        result = {}

        for info in infos:

            if info.startswith('system:'):
                (name, type, size) = info.split(':')
                result['SystemDisk'] = {
                    'Type': type, 'Size': int(size)
                }
            elif info.startswith('data:'):
                (name, type2, size2, mount_point) = info.split(':')
                result['DataDisk'] = {
                    'Type': type2, 'Size': int(size2), 'MountPoint': mount_point
                }
            else:
                raise Exception('Invalid disk format')

        return result

    except BaseException as e:
        raise Exception(
            'Invalid disk format, it should like this: --disk system:ephemeral:40,data:cloud:500:/home/disk, append -h for more')

