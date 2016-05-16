import oss2 
from ..util import config
import re

REG = r'^([\w\-]+)#oss:\/\/'

def __get_cfg():
    c = config.getConfigs(config.COMMON,['region','accesskeyid','accesskeysecret',
                                            'oss_region', 'oss_id', 'oss_key'])
    return {
        'region': c.get('oss_region') or c.get('region'),
        'accesskeyid':  c.get('oss_id') or c.get('accesskeyid') ,
        'accesskeysecret': c.get('oss_key') or c.get('accesskeysecret')
    }

def get_endpoint(region):
    return 'http://oss-%s.aliyuncs.com' % region


def check_client(cfg=None):

    cfg = cfg or __get_cfg()

    oss_path = cfg['osspath']

    (bucket, key, region) = parse_oss_path(oss_path)

    bucket_tool = _get_bucket_tool(region or cfg.get('oss_region') or cfg.get('region'),
                                  cfg.get('oss_id') or cfg.get('accesskeyid'),
                                  cfg.get('oss_key') or cfg.get('accesskeysecret'),
                                  bucket)

    try:
        bucket_tool.list_objects(key)
    except Exception as e:
        raise Exception(e.message)
    return 'ok'


def delete_file(oss_path):

    (bucket, key, region) = parse_oss_path(oss_path)

    bucket_tool = get_bucket_tool(bucket, region or config.get_oss_region())

    return bucket_tool.delete_object(key)

def download_file(oss_path, filename, progress_callback=None):

    (bucket, key, region) = parse_oss_path(oss_path)

    bucket_tool = get_bucket_tool(bucket, region or config.get_oss_region())

    bucket_tool.get_object_to_file(key, filename, progress_callback=progress_callback)

def upload_file(filename, oss_path, progress_callback=None):

    (bucket, key, region) = parse_oss_path(oss_path)
    bucket_tool = get_bucket_tool(bucket, region or  config.get_oss_region())

    bucket_tool.put_object_from_file(key,filename,progress_callback=progress_callback)

def put_data(data, oss_path):

    (bucket, key, region) = parse_oss_path(oss_path)
    bucket_tool = get_bucket_tool(bucket, config.get_oss_region())

    bucket_tool.put_object(key, data)


def get_data(oss_path):
    (bucket, key, region) = parse_oss_path(oss_path)
    bucket_tool = get_bucket_tool(bucket, region or config.get_oss_region())
    a = bucket_tool.get_object(key).read()

    if isinstance(a, bytes):
        return a.decode(encoding='utf-8')
    else:
        return a

def list(oss_path, delimiter=""):

    (bucket, key, region) = parse_oss_path(oss_path)

    bucket_tool = get_bucket_tool(bucket, region or config.get_oss_region())

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
    cfg = __get_cfg()

    return _get_bucket_tool(region or cfg['region'],
                             cfg['accesskeyid'],
                             cfg['accesskeysecret'],
                            bucket)

def _get_bucket_tool(region, id, key, bucket):
    auth = oss2.Auth(id,key)
    endpoint = get_endpoint(region)
    bucket_tool = oss2.Bucket(auth, endpoint, bucket)
    return bucket_tool


def parse_oss_path(oss_path):
    '''
       parse oss path
       1. cn-qingdao#oss://bucket/key1    =>  (bucket, key1, cn-qingdao)
       2. oss://bucket/key1    =>  (bucket, key1, None)
    '''

    matches = re.match(REG, oss_path)

    if matches:
        region = matches.groups()[0]
        s = oss_path[len(region)+len('#oss://'):]
    else:
        if not oss_path.startswith('oss://'):
            def_oss_path = config.get_oss_path()
            oss_path = def_oss_path + oss_path
        s = oss_path.lstrip('oss://')
        region = None

    [bucket, key] = s.split('/',1)

    return (bucket, key, region)