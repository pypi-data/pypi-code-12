import oss2 
from ..util import config
import re

REG = r'^([\w\-]+)#oss:\/\/'

def __getCfg():
    return config.getConfigs(config.COMMON,['region','accesskeyid','accesskeysecret'])

def get_endpoint(region):
    return 'http://oss-%s.aliyuncs.com' % region

def check_client(cfg=None):

    cfg = cfg or __getCfg()

    oss_path = cfg['osspath']

    (bucket, key, region, bucket_tool) = parse_oss_path(oss_path)

    try:
        bucket_tool.list_objects(key)
    except Exception as e:
        raise Exception(e.message)
    return 'ok'


def delete_file(oss_path):

    (bucket, key, region, bucket_tool) = parse_oss_path(oss_path)

    return bucket_tool.delete_object(key)

def download_file(oss_path, filename, progress_callback=None):

    (bucket, key, region, bucket_tool) = parse_oss_path(oss_path)

    bucket_tool.get_object_to_file(key, filename, progress_callback=progress_callback)

def upload_file(filename, oss_path, progress_callback=None):

    (bucket, key, region, bucket_tool) = parse_oss_path(oss_path)

    bucket_tool.put_object_from_file(key,filename,progress_callback=progress_callback)

def put_data(data, oss_path):

    (bucket, key, region, bucket_tool) = parse_oss_path(oss_path)

    bucket_tool.put_object(key, data)


# def copy(source, target):
#
#     cfg = __getCfg()
#
#     auth = oss2.Auth(cfg['accesskeyid'], cfg['accesskeysecret'])
#
#     endpoint = get_endpoint(cfg['region'])
#
#     (bucket, key) = parse_oss_path(source)
#     (target_bucket, target_key) = parse_oss_path(target)
#
#
#     if bucket == target_bucket:
#         # same bucket
#         bucket_tool = oss2.Bucket(auth, endpoint, bucket)
#         bucket_tool.copy_object(bucket, key, target_key)
#     else:
#         # different bucket
#         bucket_tool = oss2.Bucket(auth, endpoint, bucket)
#         obj = bucket_tool.get_object(key)
#
#         target_bucket_tool = oss2.Bucket(auth, endpoint, target_bucket)
#         target_bucket_tool.put_object(target_key, obj)


def get_data(oss_path):
    (bucket, key, region, bucket_tool) = parse_oss_path(oss_path)

    a = bucket_tool.get_object(key).read()

    if isinstance(a, bytes):
        return a.decode(encoding='utf-8')
    else:
        return a

def list(oss_path, delimiter=""):

    (bucket, key, region, bucket_tool) = parse_oss_path(oss_path)

    (obj_arr, pre_arr) = _list(bucket_tool, key, delimiter=delimiter)

    return (obj_arr, pre_arr, bucket_tool, region, bucket, key)

def _list(bucket_tool, key, marker='', delimiter=""):
    obj_arr = []
    pre_arr = []
    obj = bucket_tool.list_objects(key, delimiter=delimiter, marker=marker)

    obj_arr += obj.object_list
    pre_arr += obj.prefix_list

    if obj.next_marker:
        (v,v2) = _list(bucket_tool, key, obj.next_marker, delimiter=delimiter)
        obj_arr += v
        pre_arr += v2

    return (obj_arr, pre_arr)

def get_bucket_tool(bucket, region=None):

    cfg = __getCfg()

    auth = oss2.Auth(cfg['accesskeyid'], cfg['accesskeysecret'])

    endpoint = get_endpoint(region or cfg['region'])

    bucket_tool = oss2.Bucket(auth, endpoint, bucket)

    return bucket_tool

def parse_oss_path(oss_path):
    '''
       parse oss path
       1. cn-qingdao#oss://bucket/key1    =>  (bucket, key1, cn-qingdao)
       2. oss://bucket/key1    =>  (bucket, key1, cn-qingdao)
    '''

    matches = re.match(REG, oss_path)

    if matches:
        region = matches.groups()[0]
        s = oss_path[len(region)+len('#oss://'):]
    else:
        if not oss_path.startswith('oss://'):
            def_oss_path = config.get_oss_path()
            oss_path = def_oss_path + oss_path

        region = config.getRegion()
        s = oss_path.lstrip('oss://')

    [bucket, key] = s.split('/',1)

    bucket_tool = get_bucket_tool(bucket, region)

    return (bucket, key, region, bucket_tool)