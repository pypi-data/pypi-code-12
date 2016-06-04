#coding:utf-8
import base64
from awslib.base import md5
from boto import *
from awslib.base import platform
import os

def get_format_tag(etag):
    '''
        将s3上的文件e_tag值去除前后的引号(")
    '''

    strip_etag = etag.lstrip('"').rstrip('"')
    return strip_etag

def get_etag(md5s):
    '''
        s3上计算分块上传文件的e_tag算法
        将所有分块的md5值汇总，转换大写，计算base64值，再获取base64内容的md5值
    '''

    md5str = ''.join(md5s)
    upper_md5str = md5str.upper()
    b64 = base64.b16decode(upper_md5str)
    b64_md5 = md5.get_str_md5(b64)
	
    etag = b64_md5 + "-" + str(len(md5s))
    return etag


def split_etag(etag):

    strip_etag = get_format_tag(etag)
    lsts = strip_etag.split('-')

    md5_str = lsts[0]
    part_number = int(lst[1])

    return md5_str,part_number


def is_bucket_file_exists(bucket,key):
    '''
        判断bucket里面的文件是否存在
        不存在的文件没有e_tag值，会抛出异常
    '''
    try:
        s3_file_obj = s3.Object(bucket,key)
        etag = s3_file_obj.e_tag
        return True
    except botocore.exceptions.ClientError,e:
        if str(e).find('(404)') != -1:
            return False

def is_bucket_exists(bucket):
    '''
        判断bucket是否存在
    '''

    s3_bucket = s3.Bucket(bucket)
    try:
        s3_bucket = s3.Bucket(bucket)
        s3_bucket.wait_until_exists()
        return True
    except botocore.exceptions.ClientError,e:
        if str(e).find('(404)') != -1:
            return False
    except botocore.exceptions.WaiterError,e:
        return False


def get_app_data_path():

    if platform.CURRENT_OS_SYSTEM == platform.WINDOWS_OS_SYSTEM:
        #from win32com.shell import shell  
        #from win32com.shell import shellcon  
      
        #app_data_path = shell.SHGetPathFromIDList(shell.SHGetSpecialFolderLocation(0,shellcon.CSIDL_APPDATA))

        base_app_data_path = os.getenv('APPDATA')
        app_data_path = os.path.join(base_app_data_path,'awslib')
    elif platform.CURRENT_OS_SYSTEM == platform.LINUX_OS_SYSTEM:

        base_app_data_path = os.getenv('HOME')
        app_data_path = os.path.join(base_app_data_path,'.awslib')
    
    return app_data_path

