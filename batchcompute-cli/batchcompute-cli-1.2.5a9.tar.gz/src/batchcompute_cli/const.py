# -*- coding: utf-8 -*-

NAME = 'batchcompute-cli'

COMMAND = 'batchcompute|bcs'
CMD = 'bcs'

LOCALE_SUPPORTED = ['en', 'zh', 'zh_CN']

VERSION = '1.2.5a9'


IT = {
    'cn-qingdao': {
        'data': [
            {'cpu': 4, 'memory': 8, 'name': 'ecs.s3.large'},
            {'cpu': 4, 'memory': 16, 'name': 'ecs.m1.medium'},
            {'cpu': 4, 'memory': 32, 'name': 'ecs.m2.medium'},
            {'cpu': 8, 'memory': 16, 'name': 'ecs.c1.large'},
            {'cpu': 8, 'memory': 32, 'name': 'ecs.m1.xlarge'},
            {'cpu': 8, 'memory': 64, 'name': 'ecs.m2.xlarge'},
            {'cpu': 16, 'memory': 16, 'name': 'ecs.c2.medium'},
            {'cpu': 16, 'memory': 32, 'name': 'ecs.c2.large'},
            {'cpu': 16, 'memory': 64, 'name': 'ecs.c2.xlarge'}
        ],
        'default': 'ecs.s3.large'
    }
}

IMG = {
    'cn-qingdao': {
        'data': [],
        'default': 'm-282q1y6ld'
    }
}


from .util import config


configObj = config.getConfigs(config.COMMON)
region = configObj.get('region')
if region:
    REGION = region

IS_GOD = configObj.get('god') or False


try:
    IT_DATA = IT[REGION]['data']
    INS_TYPE = configObj.get('defaulttype') or IT[REGION]['default']
    IMG_ID = configObj.get('defaultimage') or IMG[REGION]['default']

except Exception as e:
    IT_DATA = IT['cn-qingdao']['data']
    INS_TYPE= configObj.get('defaulttype') or 'ecs.s3.large'
    IMG_ID = configObj.get('defaultimage') or IMG['cn-qingdao']['default']



import sys


# Python 2 or Python 3 is in use.
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
WIN = sys.platform == 'win32'

# Definition of descriptor types.
if PY2:
    STRING = (str, unicode)
    NUMBER = (int, long)

if PY3:
    STRING = (str, bytes)
    NUMBER = int


# fix chinese view
def get_local():
    return codecs.lookup(locale.getpreferredencoding()).name
if PY2:
    import locale
    import codecs
    try:
        reload(sys)
        loc = get_local()
        sys.setdefaultencoding(loc) # utf-8
    except:
        pass



