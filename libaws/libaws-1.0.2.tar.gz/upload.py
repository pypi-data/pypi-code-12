#coding:utf-8
import argparse
import os
from awslib.common import config
from awslib.s3.upload import upload
from awslib.common.logger import logger

if __name__== "__main__":
   
    parser = argparse.ArgumentParser()
    parser.add_argument("-file", "--file", type=str, dest="file_path", required=True)
    parser.add_argument("-bucket", "--bucket", type=str, dest="bucket",help='dest bucket to upload',\
                        default=config.DEFAULT_BUCKET_NAME)
    parser.add_argument("-part", "--part", type=int, dest="part_num",help='part num of file',default=config.DEFAULT_PART_NUM)
    parser.add_argument("-key", "--key", type=str, help="dest bucket key",dest='key',default=None)
    parser.add_argument("-ignore-bucket-file", "--ignore-bucket-file", action='store_true', dest="ignore_bucket_file",help='when file exist in bucket ,ignore it or not',default=False)
    parser.add_argument("-force-again-upload", "--force-again-upload", action='store_true', dest="force_again_upload",help='need to upload again when upload is exists',default = False)
    args = parser.parse_args()
    file_path = args.file_path
    bucket = args.bucket
    key = args.key
    part_num = args.part_num
    extra_args = {
        'ignore_bucket_file':args.ignore_bucket_file,
        'force_again_upload':args.force_again_upload
    }

    file_path = os.path.abspath(file_path)
    upload_config = config.UploadConfig(bucket,key,file_path,part_num,**extra_args)
    logger.info('start upload file %s',(file_path))

    upload.upload_file(upload_config)
    logger.info('end upload file %s',(file_path))
