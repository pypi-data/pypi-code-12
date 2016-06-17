#coding:utf-8
import argparse
import os
from libaws.common import config
from libaws.common.logger import logger,enable_debug_log
from libaws.s3.upload import upload

def daemonize():
    try:
        from libaws.base import daemon
        daemon.daemonize()
    except Exception,e:
        logger.warn('%s',e)

def main():
    parser = argparse.ArgumentParser()
    #上传文件路径，必须参数
    parser.add_argument("-file", "--file", type=str, dest="file_path", required=True)
    #上传至的bucket,必须参数
    parser.add_argument("-bucket", "--bucket", type=str, dest="bucket",help='dest bucket to upload',\
                        default=config.DEFAULT_BUCKET_NAME)
    #上传分块个数，默认为6
    parser.add_argument("-part", "--part", type=int, dest="part_num",help='part num of file',default=config.DEFAULT_PART_NUM)
    #上传至bucket的文件名,默认为上传文件名
    parser.add_argument("-key", "--key", type=str, help="dest bucket key",dest='key',default=None)
    #bucket存在和上传文件名一致的时候是否替换目的文件
    parser.add_argument("-ignore-bucket-file", "--ignore-bucket-file", action='store_true', dest="ignore_bucket_file",help='when file exist in bucket ,ignore it or not',default=False)
    #是否强制重新上传某个文件
    parser.add_argument("-force-again-upload", "--force-again-upload", action='store_true', dest="force_again_upload",help='need to upload again when upload is exists',default = False)
    #进程是否后台运行
    parser.add_argument("-daemon", "--daemon", action='store_true', dest="is_daemon_run",help='indicate this process is run in daemon or not',default = False)
    #是否开启日志调试模式
    parser.add_argument("-enable-debug-log", "--enable-debug-log", action='store_true', dest="enable_debug_log",help='enable debug log or not',default = config.ENABLE_DEBUG_LOG)
    args = parser.parse_args()
    file_path = args.file_path
    bucket = args.bucket
    key = args.key
    part_num = args.part_num
    extra_args = {
        'ignore_bucket_file':args.ignore_bucket_file,
        'force_again_upload':args.force_again_upload,
        'is_daemon_run':args.is_daemon_run,
        'enable_debug_log':args.enable_debug_log
    }

    file_path = os.path.abspath(file_path)
    upload_config = config.UploadConfig(bucket,key,file_path,part_num,**extra_args)

    #设置调试日志
    enable_debug_log(args.enable_debug_log)
    #设置进程后台运行
    if args.is_daemon_run:
        daemonize()
    logger.info('start upload file %s',(file_path))
    upload.upload_file(upload_config)
    logger.info('end upload file %s',(file_path))

if __name__== "__main__":
    main()

