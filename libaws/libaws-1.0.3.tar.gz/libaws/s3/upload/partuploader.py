#coding:utf-8
import threading
import datetime
from libaws.common.logger import *
from libaws.common import db,utils,config,const
from libaws.common.errorcode import *
from libaws.base import md5


class UploadDbProgress(object):
    '''
        更新数据库上传进度,所有分块线程操作同一个进度
    '''

    def __init__(self):
        self._lock = threading.Lock()

    @property
    def lock(self):
        '''
            互斥锁
        '''
        return self._lock

    def update_db_progress(self,multi_part_uploader,etag,succ):
        
        file_path = multi_part_uploader.file_object.path
        s3_upload_db = db.S3UploadDb().get_db()
        update_sql = '''
            update part set is_upload=?,etag=?,end_time=? where id=?
        '''

        now_time = datetime.datetime.now()
        data = [(succ,etag,now_time,multi_part_uploader.upload_part_id),]
        s3_upload_db.update(update_sql,data)
        #下面必须加互斥锁，否则会因为多线程导致进度紊乱
        with self.lock:
            #计算上传进度
            upload_size = float(s3_upload_db.get_upload_size(multi_part_uploader.file_object.upload_id))
            upload_size += multi_part_uploader.file_range.size
            percent = '%.2f%%' % (100*upload_size/multi_part_uploader.file_object.size)
            update_sql = '''
                update upload set upload_size=?,upload_percent=?,status=? where id=?
            '''

            data = [(upload_size,percent,const.STATUS_UPLOADING,multi_part_uploader.file_object.upload_id),]
            s3_upload_db.update(update_sql,data)
            logger.info('file:%s upload percentage is %s ====================================upload size(%d/%d)',file_path,percent,\
                upload_size,multi_part_uploader.file_object.size)

class MultiPartUploader(object):
    '''
        分块上传对象
    '''

    def __init__(self,upload_part_id,s3_multipart_upload,file_obj,file_range,callback=None):

        self._s3_multipart_upload = s3_multipart_upload
        self._file_obj = file_obj
        self._file_range = file_range
        self._part_id = self.s3_multipart_upload.part_number
        self._upload_part_id = upload_part_id 
        self._callback = callback
        self._upload_db_progress = None

    @property
    def s3_multipart_upload(self):
        return self._s3_multipart_upload

    @property
    def file_object(self):
        return self._file_obj
    
    @property
    def file_range(self):
        return self._file_range

    @property
    def part_id(self):
        return self._part_id
    
    @property
    def upload_part_id(self):
        return self._upload_part_id
    
    @property
    def callback(self):
        return self._callback
    
    @property
    def upload_db_progress(self):
        '''
            更新上传进度对象
        '''
        return self._upload_db_progress
    
    @upload_db_progress.setter
    def upload_db_progress(self,upload_db_progress):
        self._upload_db_progress = upload_db_progress
  
    def upload_file_part(self):
        '''
            上传分块
        '''

        file_path = self.file_object.path
        logger.debug('upload_part_id:%d---part_id:%d---%s,file_size:%ld',self.upload_part_id,self.part_id,self.file_range,self.file_object.size)
        start_byte,end_byte,block_size = self.file_range.start,self.file_range.end,self.file_range.size
        try:
            f = open(file_path,'rb')
        except IOError as e:
            logger.error("%s",e)
            logger.error("%s",ERROR_CODE_MESSAGES[OPEN_FILE_ERROR].format(file_path))
            return None,False

        with f:
            #在分块开始位置读取分块大小的文件内容
            f.seek(start_byte,0)
            assert(block_size == (end_byte - start_byte))
            rd = f.read(block_size)
            #计算分块内容的md5值
            rd_md5 = md5.get_str_md5(rd)
            #上传分块内容
            part_upload = self.s3_multipart_upload.upload(Body=rd)
            #上传分块后返回的e_tag值
            etag = part_upload['ETag']
            strip_etag = utils.get_format_tag(etag)
            logger.info('part_id:%d md5:%s etag:%s',self.part_id,rd_md5,strip_etag)
            #比较分块的md5值和上传分块返回的e_tag值，保证上传分块的正确性
            if strip_etag != rd_md5:
                raise ValueError(ERROR_CODE_MESSAGES[UPLOAD_PART_MD5_MATCH_ERROR])

            #调用上传分块回调函数
            if self.callback is not None:
                self.callback(block_size)
            return strip_etag,True

    def upload_range(self):
        number_retry_count = config.UPLOAD_RETRY_TIMES
        #上传重试，如果第一个上传成功，则后面的几次不需要重试了，直接返回成功结果
        for i in range(number_retry_count):
            try:
                etag,succ = self.upload_file_part()
                return etag,succ
            except Exception,e:
                logger.debug("Retrying exception caught (%s),retrying request, (attempt %s / %s)", e, i+1,number_retry_count)
                continue

        #超过重试次数
        raise ValueError(ERROR_CODE_MESSAGES[EXCEED_MAX_UPLOAD_ATTEMPTS])

    def upload(self):
        
        try:
            #上传分块
            etag,succ = self.upload_range()
            if not succ:
                return False
        except Exception,e:
            logger.error("%s",e)
            return False

        assert(self.upload_db_progress != None)
        #上传完成后更新数据库里面的上传进度
        self.upload_db_progress.update_db_progress(self,etag,succ) 
        return True

class MultiThreadUploader(threading.Thread):
    '''
        多线程上传分块对象
    '''

    upload_db_progress = UploadDbProgress()
    
    def __init__(self,que):
        threading.Thread.__init__(self)
        #表示线程是否是后台线程，主进程不会等待后台线程结束而退出，如果是非后台进程，则主进程会等待子线程执行完成了，才退出。
        self.daemon = False
        self.queue = que
    
    def run(self):

        while True:
            #分块队列为空，表示所有分块上传完成,跳出循环
            if self.queue.empty():
                break
            #获取上传分块对象
            my_part_uploader = self.queue.get()
            #所有分块设置同一个上传进度跟踪对象
            my_part_uploader.upload_db_progress = self.upload_db_progress
            logger.debug('thread:%s start upload part:%d',self.name,my_part_uploader.part_id)
            #开始上传分块
            if my_part_uploader.upload():
                logger.info('file:%s part:%d upload success',my_part_uploader.file_object.path,my_part_uploader.part_id)
            else:
                logger.error('file:%s part:%d upload error',my_part_uploader.file_object.path,my_part_uploader.part_id)
            self.queue.task_done()

    @classmethod
    def start_upload_parts(cls,que):

        uploaders = [MultiThreadUploader(que) for x in range(config.DEFAULT_THREAD_SIZE)]
        for uploader in uploaders:
            #启动上传分块线程
            uploader.start()

        #等待上传分块完成，直到分块队列为空
        que.join()

