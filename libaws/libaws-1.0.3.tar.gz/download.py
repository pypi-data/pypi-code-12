#coding:utf-8
import os
import argparse
from libaws.common import config
from libaws.common.logger import logger,enable_debug_log
from libaws.s3.download import download

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    #指定下载的bucket,必须参数
    parser.add_argument("-bucket", "--bucket", type=str, dest="bucket",help='dest bucket to download file',default=config.DEFAULT_BUCKET_NAME)
    #指定下载bucket中的文件,必须参数
    parser.add_argument("-key", "--key", type=str, dest="key", help = 'bucket file to download',required=True)
    #指定下载路径,默认为当前路径
    parser.add_argument("-path", "--path", type=str, dest="path", help = 'file download path to save',default = './',required=False)
    #指定下载文件名,默认和key一致
    parser.add_argument("-filename", "--filename", type=str, dest="filename", help = 'download file name',default = None,required=False)
    #是否强制重新下载某个文件,默认为否
    parser.add_argument("-force-again-download", "--force-again-download", action='store_true', dest="force_again_download",help='need to download again when download is exists',default = False)
    #是否开启日志调试模式
    parser.add_argument("-enable-debug-log", "--enable-debug-log", action='store_true', dest="enable_debug_log",help='enable debug log or not',default = config.ENABLE_DEBUG_LOG)
    args = parser.parse_args()
    bucket = args.bucket
    key = args.key
    
    filename = key
    if args.filename is not None:
        filename = args.filename

    dest_path = os.path.abspath(args.path)
    extra_args = {
        'force_again_download':args.force_again_download,
        'enable_debug_log':args.enable_debug_log
    }
    download_config = config.DownloadConfig(bucket,key,dest_path,filename,**extra_args)
    enable_debug_log(args.enable_debug_log)
    dest_file = os.path.join(dest_path,filename)
    logger.info('start download file %s',dest_file)
    download.download_file(download_config)
    logger.info('end download file %s',dest_file)
