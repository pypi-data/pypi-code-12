from ..util import util,formater,oss_client,config
import json
import os
import sys
import tarfile
import glob
from terminal import green,blue

def upload(localpath, osspath):

    if '*' in localpath:
        raise Exception('Invalid filename')

    if not osspath.startswith('oss://'):
        raise Exception('Invalid osspath')

    abs_path = formater.get_abs_path(localpath)


    if not os.path.exists(abs_path):
        raise Exception('Not found %s' % abs_path)


    if os.path.isdir(abs_path):
        # folder
        if not osspath.endswith('/'):
            osspath+='/'
        # d - d
        upload_folder_2_folder(abs_path, osspath)
    else:
        # file
        if osspath.endswith('/'):
            osspath += os.path.basename(abs_path)
        oss_client.upload_file(abs_path, osspath, upload_progress_callback)


def upload_folder_2_folder(abs_path, osspath):
    print('%s: %s to %s' % (blue('upload folder'),abs_path, osspath) )

    arr = os.listdir(abs_path)
    for k in arr:
        filename = os.path.join(abs_path, k)
        if os.path.isdir(filename):
            upload_folder_2_folder(filename, osspath+k+'/')
        else:
            print('  %s => %s' % (filename, osspath+k))
            oss_client.upload_file(filename, osspath+k,  upload_progress_callback)


def upload_progress_callback(a,b):

    if a!= b:
        p = int(a*50/b)
        s = ('%s %s%%\r' % ('#' * p , p*2) )
    else:
        s = ('%s 100%%\n' % ('#' * 50) )

    sys.stdout.write(s)
    sys.stdout.flush()