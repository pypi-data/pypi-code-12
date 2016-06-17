#coding:utf-8

#上传文件时默认分块个数
DEFAULT_PART_NUM = 6
#允许文件分块上传的默认最小值10M
DEFAULT_MULTI_UPLOAD_SIZE = 10*1024*1024
#上传文件时默认多线程个数
DEFAULT_THREAD_SIZE = 10
#默认上传分块在服务器保存的天数
BUCKET_UPLOAD_EXPIRE_DAY = 3 
#上传下载文件时默认bucket
DEFAULT_BUCKET_NAME = 'wukan_test_bucket'

#上传数据库
UPLOAD_DB_NAME = "upload.db"
#下载数据库
DOWNLOAD_DB_NAME = "download.db"
#上传表
UPLOAD_TABLE = "upload"
#上传分块表
UPLOAD_PART_TABLE = "part"
#上传文件表
UPLOAD_FILE_TABLE = "file"
#上传失败重试次数
UPLOAD_RETRY_TIMES = 5

#下载表
DOWNLOAD_TABLE = "download"
#下载分块表
DOWNLOAD_RANGE_TABLE = "range"
#随机分配下载临时文件名
DOWNLOAD_SALT_SOURCE = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
#下载文件时默认下载分块的大小
DOWNLAD_PART_LIMIT_SIZE = 8*1024*1024
#每次下载最小单元的大小
DOWNLAD_BLOCK_SIZE = 16*1024
#下载失败重试次数
DOWNLOAD_RETRY_TIMES = 5
#是否禁止使用日志
LOGGER_DISABLED = False
#是否启用调试日志
ENABLE_DEBUG_LOG = False


DEFAULT_INSTANCE_TYPE = "t2.micro"
DEFAULT_INSTANCE_VOLUME_SIZE = 8
DEFAULT_INSTANCE_CONFIG_DB_NAME = "instance.db"
DEFAULT_INSTANCE_CONFIG_TABLE_NAME = "instance"
DEFAULT_DATA_DIR_FLAG = "{data_dir}"

#下载参数配置类
class DownloadConfig(object):

    def __init__(self,bucket,key,dest_path,file_name,**kwargs):

        self.bucket = bucket
        self.key = key
        self.dest_path = dest_path
        self.filename = file_name

        for arg in kwargs:
            setattr(self,arg,kwargs[arg])


#上传参数配置类
class UploadConfig(object):

    def __init__(self,bucket,key,file_path,part_num,**kwargs):

        self.bucket = bucket
        self.key = key
        self.file_path = file_path
        self.part_number = part_num

        for arg in kwargs:
            setattr(self,arg,kwargs[arg])
