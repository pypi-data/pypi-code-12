#coding:utf-8
import os
import argparse
from libaws.common.boto import * 
from libaws.common import config

def put_bucket_policy(bucket,json_file):

    with open(json_file) as f:
        content = f.read()
        print content
        response = client_s3.put_bucket_policy(
            Bucket=bucket,Policy= content
        )


def main():
    parser = argparse.ArgumentParser()
    #指定下载的bucket,必须参数
    parser.add_argument("-name", "--name", type=str, dest="bucket",help='dest bucket to operate',default=config.DEFAULT_BUCKET_NAME)
    #指定下载bucket中的文件,必须参数
    parser.add_argument("-put-bucket-policy", "--put-bucket-policy", action="store_true", dest="is_put_bucket_policy", help = 'set bucket policy',required=False)
    parser.add_argument("-json", "--json", type=str, dest="bucket_policy_json",help='bucket policy json file')

    args = parser.parse_args()
    bucket = args.bucket

    if args.is_put_bucket_policy:
        put_bucket_policy(bucket,args.bucket_policy_json)
   
