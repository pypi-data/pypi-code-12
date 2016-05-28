# -*- coding: utf-8 -*-
from bson import json_util
from simplejson import dumps,loads

__all__ = ['dictfy','jsonify']

def dictfy(_):
    try:
        return loads(_,object_hook=json_util.object_hook)
    except:
        return False

def jsonify(_):
    try:
        return dumps(_,default=json_util.default,separators=(',',':'))
    except:
        return False
