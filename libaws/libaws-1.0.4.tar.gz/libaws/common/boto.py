import boto3
import botocore
from boto3.s3.transfer import S3Transfer

try:
    s3 = boto3.resource('s3')
    client_s3 = boto3.client('s3')
    ec2 = boto3.resource('ec2')
    client_ec2 = boto3.client('ec2')
except Exception,e:
    s3 = None
    client_s3 = None
    ec2 = None
    client_ec2 = None
    print e

