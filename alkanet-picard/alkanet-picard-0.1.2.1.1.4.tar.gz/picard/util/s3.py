from __future__ import absolute_import

import os
import errno
import boto3
bucket = boto3.resource('s3').Bucket('hadamard-data')

def upload_s3_file(localpath, targetname):
    return bucket.upload_file(localpath, targetname)

def get_s3_file(filepath):

    localpath = save_s3_file(filepath)

    with open(localpath) as tempFile:
        fileContent = tempFile.read()

    os.remove(localpath)
    return fileContent

def save_s3_file(filepath):
    localpath = get_temp_path(filepath)
    create_path(localpath)

    bucket.download_file(
        filepath,
        localpath
    )

    return localpath

def get_temp_path(s3path):
    return 'tmp/' + s3path

def create_path(filepath):
    if not os.path.exists(os.path.dirname(filepath)):
        try:
            os.makedirs(os.path.dirname(filepath))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
