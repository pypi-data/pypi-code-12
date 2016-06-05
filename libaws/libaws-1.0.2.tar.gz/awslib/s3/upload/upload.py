#coding:utf-8
import datetime
import os
import sys
import argparse
import Queue
from awslib.common.boto import *
from awslib.common import config
from awslib.common.fileobj import *
from awslib.common.logger import *
from awslib.common.db import *
from awslib.common import utils
from awslib.base import callback
from awslib.base import filerange
import partuploader
from awslib.common.errorcode import *
from awslib.common import const

s3_upload_db = S3UploadDb.get_db()

def daemonize():

    if not hasattr(os,'fork'):
        raise ValueError("Daemonizing is not available on this platform.")
        
     # fork进程        
    try:
        if os.fork() > 0: os._exit(0)
    except OSError, error:
        print 'fork #1 failed: %d (%s)' % (error.errno, error.strerror)
        os._exit(1)    
    os.chdir('/')
    os.setsid()
    os.umask(0)
    try:
        pid = os.fork()
        if pid > 0:
            os._exit(0)
    except OSError, error:
        print 'fork #2 failed: %d (%s)' % (error.errno, error.strerror)
        os._exit(1)

     # 重定向标准IO
    sys.stdout.flush()
    sys.stderr.flush()
    si = file("/dev/null", 'r')
    so = file("/dev/null", 'a+')
    se = file("/dev/null", 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

def create_multipart_upload(bucket,dest_key):
    '''
        创建s3文件分块上传对象,返回一个随机唯一的upload_id
    '''

    response = client.create_multipart_upload(Bucket=bucket,Key=dest_key)
    upload_id = response['UploadId']
    multi_part_upload = s3.MultipartUpload(bucket,dest_key,upload_id)

    return multi_part_upload

def create_upload_parts(multi_part_upload,part_num):
    '''
        创建s3上传分块对象列表
    '''
    
    if 1 >= part_num:
        return []

    multi_parts = []
    for i in range(part_num):
        part = multi_part_upload.Part(i + 1)
        multi_parts.append(part)

    return multi_parts


def sort_with_part_number(l,r):
    """
        按分块序号升序排序
    """
    p1 = l['PartNumber']
    p2 = r['PartNumber']

    if p1 > p2:
        return 1
    return -1

def save_file_info(file_obj):
    '''
        保存上传文件信息
    '''
    global s3_upload_db

    sql = '''
        INSERT INTO file(name,path,hash,time,size) VALUES (?, ?, ?,?,?)
    '''
    file_name,file_path,file_hash,file_date_time,file_size = file_obj.name,file_obj.path,\
                    file_obj.hash,file_obj.date_time,file_obj.size
    s3_upload_db.save(sql,[(file_name,file_path,file_hash,file_date_time,file_size),])

def store_multi_parts(file_obj,multi_parts):
    '''
        保存文件分块信息
    '''
    
    global s3_upload_db

    file_size = file_obj.size
    upload_id = file_obj.upload_id
    #分块个数
    part_number = len(multi_parts)
    #按分块个数对文件进行分割
    file_ranges = filerange.get_file_ranges_by_part(file_obj.path,part_number,file_size)

    datas = []
    for file_range in file_ranges:
        part_id = file_range.range_id
        block_size,start_byte,end_byte = file_range.size,file_range.start,file_range.end
        logger.debug('part_id:%d block_size:%d,start_byte:%d end_byte:%d,is_last_block:%s',\
                        part_id,block_size,start_byte,end_byte,file_range.is_last)
        datas.append((part_id,block_size,start_byte,end_byte,upload_id,file_range.is_last))

    sql = '''
        insert into part (part_id,part_size,start_byte,end_byte,upload_id,is_last_part) values (?,?,?,?,?,?)
    '''
    s3_upload_db.save(sql,datas)

def create_multipart_upload_parts(file_obj,bucket,key,part_num):
    
    global s3_upload_db

    file_id = file_obj.file_id

    multi_part_upload = create_multipart_upload(bucket,key)
    s3_upload_id = multi_part_upload.id

    sql = '''
        insert into upload(s3_upload_id,bucket,key,part_num,file_id,total_size,start_time,status) values(?,?,?,?,?,?,?,?) 
    '''

    now_time = datetime.datetime.now()
    s3_upload_db.save(sql,[(s3_upload_id,bucket,key,part_num,file_id,file_obj.size,now_time,const.STATUS_START_UPLOAD)])
    upload_parts = create_upload_parts(multi_part_upload,part_num)

    upload_id = s3_upload_db.get_upload_id(s3_upload_id)
    file_obj.upload_id = upload_id
    store_multi_parts(file_obj,upload_parts)

def is_file_upload(file_obj):
    '''
        查询文件是否已经成功上传过
    '''

    global s3_upload_db

    file_id = file_obj.file_id
    sql = '''
        select is_upload from upload where file_id=%d
    ''' % (file_id)
    result = s3_upload_db.fetchone(sql)

    is_upload, = result
    if is_upload:
        return True

    return False

def upload_file_multi_parts(file_obj,callback=None):
    '''
        上传所有文件分块
    '''
    
    global s3_upload_db

    file_path,file_id = file_obj.path,file_obj.file_id

    #先在数据库里面查询该文件的上传分块信息
    sql = '''
        select id,s3_upload_id,part_num,bucket,key from upload where file_id=%d
    ''' % (file_id)
    result = s3_upload_db.fetchone(sql)
    upload_id,s3_upload_id,part_num,bucket,dest_key = result
    sql = '''
        select * from part where upload_id=%d
    ''' % (upload_id)
    results = s3_upload_db.fetchall(sql)
    #分块个数不一致，报错
    if len(results) != part_num:
        logger.error('file:%s upload parts is damaged',file_path)
        return None,part_num,[] 
    
    multi_part_upload = s3.MultipartUpload(bucket,dest_key,s3_upload_id)
    part_ids = []
    #上传分块对象队列，采用多线程上传分块
    que = Queue.Queue()

    for row in results:
        multi_part_id = row[0]
        part_ids.append(multi_part_id)

        part_id = row[1]
        is_upload = row[5]
        block_size = row[2]

        start_time = row[8]
        if start_time is None:
            update_sql = '''
                update part set start_time=? where id=?
            '''
            now_time = datetime.datetime.now()
            data = [(now_time,multi_part_id),]
            s3_upload_db.update(update_sql,data)
        #分块已经上传成功，略过
        if is_upload:
            logger.warn('file:%s part:%d has already uploaded',file_path,part_id)
            continue

        start_byte = row[3]
        end_byte = row[6]
        block_size = row[2]
        is_last_part = row[10]
        file_range = filerange.FileRange(file_path,part_id,start_byte,end_byte,block_size,is_last_part)
        multipart_upload_part = s3.MultipartUploadPart(bucket,dest_key,s3_upload_id,part_id)
        my_part_uploader = partuploader.MultiPartUploader(multi_part_id,multipart_upload_part,file_obj,file_range,callback)
        #将上传分块对象放入队列
        que.put(my_part_uploader)
    #启用多线程上传分块
    partuploader.MultiThreadUploader.start_upload_parts(que)
    return multi_part_upload,part_num,part_ids

def complete_multi_parts(file_obj,multi_part_upload,multi_part_ids,part_num):
    '''
        完成文件分块上传
    '''

    global s3_upload_db
    
    #判断分块个数是否一致
    if len(multi_part_ids) != part_num:
        return False

    parts = []
    upload_id = None

    md5s = []

    for upload_part_id in multi_part_ids:
        query_sql = '''
            select part_id,is_upload,etag,upload_id from part where id=%d
        ''' % (upload_part_id)

        result = s3_upload_db.fetchone(query_sql)
        if result is None:
            logger.error('part_id:%d has been deleted',upload_part_id)
            return False

        part_id,is_upload,etag,upload_id = result
        #判断分块是否上传成功，如果有一个未上传成功，则终止上传
        if not is_upload:
            logger.error('part_id:%d is not uploaded',upload_part_id)
            return False

        md5s.append(etag)
        #组合分块所需的分块的序号以及e_tag值
        part = {
            'PartNumber':part_id,
            'ETag':etag
        } 
   
        parts.append(part)
    s3_upload_db.set_upload_status(const.STATUS_UPLOAD_FINISHED,upload_id)
    #分块列表必须要按分块序号进行升序排序
    parts.sort(sort_with_part_number)
    try:
        #将所有分块组合成一个完整的文件，完成分块上传,返回最终文件的s3文件对象
        upload_object = multi_part_upload.complete(
            MultipartUpload={
                'Parts':parts
            }    
        )
    except Exception,e:
        logger.error("%s",e)
        return False
    now_time = datetime.datetime.now()
    update_sql = '''
        update upload set is_upload=?,end_time=?,upload_percent=?,etag=?,status=? where id=?
    '''
    #获取上传文件的e_tag值
    file_obj.etag = upload_object.e_tag
    #上传文件后校验上传文件是否正确
    if not file_obj.validate(md5s):
        s3_upload_db.set_upload_status(const.STATUS_UPLOAD_FAIL,upload_id)
        logger.error("upload_id:%d md5 check sum is not match,etag is:%s",upload_id,utils.get_etag(md5s))
        return False

    s3_upload_db.update(update_sql,[(True,now_time,'100%',file_obj.etag,const.STATUS_UPLOAD_SUCCESS,upload_id)])
    return True

def upload_one_file(file_obj,bucket,key):
    '''
        文件单块上传
    '''

    transfer = S3Transfer(client)
    file_path = file_obj.path
    
    s3_file_obj = s3.Object(bucket,key)
    s3_file_obj.upload_file(file_path,Callback=callback.UploadProgressPercentage(file_path))
    
    file_obj.etag = s3_file_obj.e_tag
    if file_obj.validate():
        logger.info("file:%s upload to bucket %s success",file_path,bucket)
        return

    logger.error("file:%s upload to bucket %s error",file_path,bucket)

def upload_file(upload_config):
    
    def init_upload_part():
        '''
            初始化上传信息
        '''
        save_file_info(file_obj)
        file_id = s3_upload_db.get_file_id_id_by_hash(file_obj.hash)
        file_obj.file_id = file_id
        create_multipart_upload_parts(file_obj,bucket,key,part_num)
        logger.info('create file %s multi upload parts success',file_obj.path)
        return file_id

    global s3_upload_db
    file_path,bucket,key,part_num = upload_config.file_path,upload_config.bucket,\
            upload_config.key,upload_config.part_number
    #判断bucket是否存在
    try:
        if not utils.is_bucket_exists(bucket):
            logger.error("%s",ERROR_CODE_MESSAGES[BUCKET_NOT_EXISTS].format(bucket))
            logger.error("file:%s upload to bucket %s error",file_path,bucket)
            return
    except Exception,e:
        logger.error("%s",e)
        logger.error("file:%s upload to bucket %s error",file_path,bucket)
        return
        
    #判断本地文件是否存在
    if not os.path.exists(file_path):
        logger.error('file:[%s] is not exists',file_path)
        logger.error("file:%s upload to bucket %s error",file_path,bucket)
        return

    file_obj = UploadFileObj(file_path)
    if key is None:
        key = file_obj.name
    
    #上传文件时，如果bucket上已经存在该文件，提示是否替换该文件
    if not upload_config.ignore_bucket_file and utils.is_bucket_file_exists(bucket,key):
        logger.warn("%s",ERROR_CODE_MESSAGES[BUCKET_UPLOAD_FILE_EXISTS].format(key,bucket))
        return
    
    #文件大小小于默认分块上传的最小值时，使用单块上传方式
    if file_obj.size < config.DEFAULT_MULTI_UPLOAD_SIZE:
        upload_one_file(file_obj,bucket,key)
        return
    
    #通过文件hash值查找文件id
    file_id = s3_upload_db.get_file_id_id_by_hash(file_obj.hash)
    logger.info('get file %s hash success',file_obj.path)
    #第一次上传
    if not file_id:
        file_id = init_upload_part()
    else:
        file_obj.file_id = file_id
        if upload_config.force_again_upload:
            logger.debug('delete upload file_id:%d',file_id)
            s3_upload_db.delete_upload(file_id)
            file_id = init_upload_part()
    upload_id = s3_upload_db.get_upload_id_by_fileid(file_id)
    if not upload_id:
        create_multipart_upload_parts(file_obj,bucket,key,part_num)
        upload_id = s3_upload_db.get_upload_id_by_fileid(file_id)

    file_obj.upload_id = upload_id
    #文件已经上传过了
    if is_file_upload(file_obj):
        #已经上传过的文件提示是否重新上传
        if not upload_config.force_again_upload:
            logger.warn('%s',ERROR_CODE_MESSAGES[UPLOAD_AGAIN_FILE_SUCCESS].format(file_obj.path,bucket))
            return
    #开始上传所有分块 
    if config.LOGGER_DISABLED:
        multi_part_upload,part_num,part_ids = upload_file_multi_parts(file_obj,callback=callback.UploadProgressPercentage(file_path))
    else:
        multi_part_upload,part_num,part_ids = upload_file_multi_parts(file_obj)
    if not multi_part_upload:
        return
    
    logger.info('upload file %s multi parts success',file_obj.path)
    #将所有分块组合成一个最终的文件，并校验其hash值是否一致，完成此次上传
    if complete_multi_parts(file_obj,multi_part_upload,part_ids,part_num):
        logger.info("file:%s upload to bucket %s success",file_path,bucket)
    else:
        logger.error("file:%s upload to bucket %s error",file_path,bucket)

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

    try:
        daemonize()
    except Exception,e:
        logger.warn('%s',e)
    upload_file(upload_config)
    logger.info('end upload file %s',(file_path))
