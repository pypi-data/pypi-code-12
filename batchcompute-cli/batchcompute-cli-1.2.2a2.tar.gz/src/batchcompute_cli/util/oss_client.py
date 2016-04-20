import oss2 
from ..util import config

def __getCfg():
    return config.getConfigs(config.COMMON,['region','accesskeyid','accesskeysecret'])

def __get_endpoint(region):
    return 'http://oss-%s.aliyuncs.com' % region

def check_client(cfg=None):
    cfg = cfg or __getCfg()
    auth = oss2.Auth(cfg['accesskeyid'], cfg['accesskeysecret'])

    endpoint = __get_endpoint(cfg['region'])

    oss_path = cfg['osspath']

    (bucket, key) = parse_oss_path(oss_path)

    bucket_tool = oss2.Bucket(auth, endpoint, bucket)

    try:
        bucket_tool.list_objects(key)
    except Exception as e:
        raise Exception(e.message)
    return 'ok'


def delete_file(oss_path):

    cfg = __getCfg()

    auth = oss2.Auth(cfg['accesskeyid'], cfg['accesskeysecret'])

    endpoint = __get_endpoint(cfg['region'])

    (bucket, key) = parse_oss_path(oss_path)

    bucket_tool = oss2.Bucket(auth, endpoint, bucket)

    return bucket_tool.delete_object(key)

def download_file(oss_path, filename, progress_callback=None):
    
    cfg = __getCfg()

    auth = oss2.Auth(cfg['accesskeyid'], cfg['accesskeysecret'])

    endpoint = __get_endpoint(cfg['region'])

    (bucket, key) = parse_oss_path(oss_path)

    bucket_tool = oss2.Bucket(auth, endpoint, bucket)

    bucket_tool.get_object_to_file(key, filename, progress_callback=progress_callback)

def upload_file(filename, oss_path, progress_callback=None):

    cfg = __getCfg()

    auth = oss2.Auth(cfg['accesskeyid'], cfg['accesskeysecret'])

    endpoint = __get_endpoint(cfg['region'])

    (bucket, key) = parse_oss_path(oss_path)

    bucket_tool = oss2.Bucket(auth, endpoint, bucket)

    bucket_tool.put_object_from_file(key,filename,progress_callback=progress_callback)

def put_data(data, oss_path):

    cfg = __getCfg()

    auth = oss2.Auth(cfg['accesskeyid'], cfg['accesskeysecret'])

    endpoint = __get_endpoint(cfg['region'])

    (bucket, key) = parse_oss_path(oss_path)

    bucket_tool = oss2.Bucket(auth, endpoint, bucket)

    bucket_tool.put_object(key, data)

def get_data(oss_path):

    cfg = __getCfg()

    auth = oss2.Auth(cfg['accesskeyid'], cfg['accesskeysecret'])

    endpoint = __get_endpoint(cfg['region'])

    (bucket, key) = parse_oss_path(oss_path)

    bucket_tool = oss2.Bucket(auth, endpoint, bucket)

    a = bucket_tool.get_object(key).read()

    if isinstance(a, bytes):
        return a.decode(encoding='utf-8')
    else:
        return a

def list(oss_path, delimiter=""):

    cfg = __getCfg()

    auth = oss2.Auth(cfg['accesskeyid'], cfg['accesskeysecret'])

    endpoint = __get_endpoint(cfg['region'])

    (bucket, key) = parse_oss_path(oss_path)

    bucket_tool = oss2.Bucket(auth, endpoint, bucket)

    (obj_arr, pre_arr) = _list(bucket_tool, key, delimiter=delimiter)

    return (obj_arr, pre_arr, bucket_tool)

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

def parse_oss_path(oss_path):

    s = oss_path.lstrip('oss://')

    [bucket, key] = s.split('/',1)

    return (bucket,key)