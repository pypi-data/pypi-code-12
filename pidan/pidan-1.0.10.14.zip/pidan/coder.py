# -*- coding: utf-8 -*-
#编码相关的函数
import uuid,datetime,base64
import hashlib
import traceback

def get_uuid():
    return str(uuid.uuid1())

def get_hash_code(value,sign='7788521'):
    '''返回加入了干扰码的md5'''
    return hashlib.new('md5',value+sign).hexdigest()

def md5(value):
    return hashlib.new('md5',value).hexdigest()


def base64_url_encode(value):
    '''base64基于url安全的加密函数'''
    value=value.encode(encoding="utf-8")
    return base64.urlsafe_b64encode(value)


def base64_url_decode(value):
    '''base64基于url安全的解密函数'''
    try:
        value = str(value)
        result= base64.urlsafe_b64decode(value)
        result = unicode(result,'utf-8')
        return result
    except:
        print(traceback.format_exc())
        return None


def to_unicode(s,encoding=None):
    '''转换成unicode'''
    if isinstance(s, unicode):
        return s
    else:
        if encoding:
            return unicode(s,encoding)
        else:
            return unicode(s)



if __name__=='__main__':
    print(md5('1'))