# -*- coding: utf-8 -*-

import redis

import gaia.config as cfg

from qiniu import Auth
from qiniu import BucketManager
from qiniu import put_file
from qiniu.utils import etag
from qiniu.config import set_default

config = cfg.load_config('app.yaml') or cfg.load_config('qiniu.yaml') or cfg.load_config('qiniu.json') or cfg.load_config('qiniu.cfg')

set_default(default_up_host=config["qiniu"]["up_host"])

q = Auth(config["qiniu"]["access_key"], config["qiniu"]["secret_key"])
b = BucketManager(q)

def file_exist(bucket, key, localfile):
    ret, info = b.stat(bucket, key)
    return ret and "hash" in ret and ret["hash"] == etag(localfile)

def file_put(bucket, key, localfile):
    token = q.upload_token(bucket, key)
    ret, info = put_file(token, key, localfile)

def url_download(key):
    host = config["qiniu"]["dn_host"]
    burl = "%s/%s" % (host, key)
    return q.private_download_url(burl, expires=3600)