
# -*- coding:utf-8 -*-

from ..util import it,client,util
from terminal import green
from ..const import IMG_ID,INS_TYPE
import json


def create_cluster(clusterName, image=IMG_ID, type=INS_TYPE, nodes=1, description='', userData=None, disk=None, show_json=False):

    cluster_desc = {}
    cluster_desc['Name'] = clusterName
    cluster_desc['ImageId'] = image
    cluster_desc['InstanceType'] = type
    cluster_desc['Description'] = description

    cluster_desc['Groups']={
        'group': {
            'InstanceType': type,
            'DesiredVMCount': nodes,
            'ResourceType': 'OnDemand'
        }
    }

    if userData:
        cluster_desc['UserData'] = {}
        for item in userData:
           cluster_desc['UserData'][item.get('key')]=item.get('value')

    if disk:
        if not cluster_desc.get('Configs'):
            cluster_desc['Configs'] = {}
        cluster_desc['Configs']['Disks']=disk

    if show_json:
        print(json.dumps(cluster_desc, indent=4))
    else:
        result = client.create_cluster(cluster_desc)

        if result.StatusCode==201:
            print(green('Cluster created: %s' % result.Id))




# def trans_resource(resrc):
#     items = resrc.split(':')
#
#     m = {}
#     for item in items:
#         if item.startswith('img='):
#             img = item.split('=',1)[1] or IMG_ID
#             if not img.startswith('m-'):
#                 raise Exception('Invalid resource, for the img is invalid')
#             m['ECSImageId'] = img
#         if item.startswith('type='):
#             type = item.split('=',1)[1] or INS_TYPE
#             if not it.get_by_name(type):
#                 raise Exception('Invalid resource, for the type is invalid')
#             m['InstanceType'] = type
#     return m
#
#
# def trans_groups(groups):
#     items = groups.split(',')
#     t=[]
#
#     for item in items:
#         arr = item.split(':')
#         nodes=1
#         type= INS_TYPE
#
#         groupName = arr[0]
#         for item in arr:
#             if item.find('nodes')==0:
#                 try:
#                     nodes=int(item[6:])
#                 except:
#                     raise Exception('Invalid group, for the nodes is not a integer')
#                 if nodes < 1:
#                     raise Exception('Invalid group, for the nodes is bellow 1')
#
#             if item.find('type')==0:
#                 type = item[5:]
#                 if not it.get_by_name(type):
#                     raise Exception('Invalid group, for the type is invalid')
#
#         t.append( {'name':groupName, 'type':type, 'nodes':nodes} )
#     return t


def trans_image(image):
    if not image.startswith('m-'):
        raise Exception('Invalid imageId: %s' % image)
    return image

def trans_type(type):
    m = it.get_ins_type_map()

    if not m.get(type):
        raise Exception('Invalid instanceType')
    return type

def trans_nodes(n):
    try:
        n = int(n)
        if isinstance(n, int):
            return n
        else:
            raise Exception('Invalid nodes, it must be an integer')
    except:
        raise Exception('Invalid nodes, it must be an integer')


def trans_userData(userData):
    items = userData.split(',')
    t = []
    for item in items:
        arr = item.split(':',1)
        t.append( {'key': arr[0], 'value': arr[1] if len(arr)==2 else ''} )
    return t


def trans_disk(disk):
    return util.trans_disk(disk)