import boto3
import botocore
from boto3.s3.transfer import S3Transfer

s3 = boto3.resource('s3')
client = boto3.client('s3')

