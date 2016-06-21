
from batchcompute.utils.functions import ConfigError
from terminal import Logger, prompt, password, green

from ..util import config, client

log = Logger()


def login(region, accessKeyId=None, accessKeySecret=None):

    opt = config.getConfigs(config.COMMON)

    opt['region'] = region

    if region and accessKeyId and accessKeySecret:

        opt['accesskeyid'] = accessKeyId
        opt['accesskeysecret'] = accessKeySecret

    else:
        opt['accesskeyid'] = prompt('input accessKeyId')
        opt['accesskeysecret'] = password('and accessKeySecret')

    try:
        client.check_client(opt)

        config.setConfigs(config.COMMON, opt)

        print(green('login success' ))

    except Exception as e:
        e = '%s' % e
        if 'nodename nor servname provided' in e:
            raise Exception('Invalid region %s' % region)
        else:
            raise Exception(e)


