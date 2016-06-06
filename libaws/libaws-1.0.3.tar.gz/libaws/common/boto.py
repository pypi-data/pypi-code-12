import boto3
import botocore
from boto3.s3.transfer import S3Transfer

try:
    s3 = boto3.resource('s3')
    client = boto3.client('s3')
except Exception,e:
    s3 = None
    client = None
    print e

