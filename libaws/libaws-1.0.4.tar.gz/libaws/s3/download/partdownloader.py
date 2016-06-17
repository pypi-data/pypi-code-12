#coding:utf-8
import datetime
from libaws.common import config
from libaws.common.logger import *
from libaws.common.db import *
from libaws.common import const

class DownloadCell(object):
    '''
        下载对象细分最小单元
    '''

    def __init__(self,start_pos,cell_size,cell_download_size = 0):

        self._start = start_pos
        self._size = cell_size
        self._download_size = cell_download_size 

    @property
    def start(self):
        return self._start
    
    @property
    def size(self):
        return self._size
    
    @property
    def download_size(self):
        return self._download_size

class MultiPartDownloader(object):
    '''
        分块下载对象
    '''

    def __init__(self,download_range_id,download_file_obj,s3_file_obj,file_range):

        self._download_file_obj = download_file_obj
        self._file_range = file_range
        self._s3_file_obj = s3_file_obj
        self._download_range_id = download_range_id

    @property
    def download_file_obj(self):
        return self._download_file_obj
    
    @property
    def file_range(self):
        return self._file_range

    @property
    def s3_file_obj(self):
        return self._s3_file_obj
    
    @property
    def download_range_id(self):
        return self._download_range_id
    
    def download(self,body,file_obj,callback=None):
        '''
            下载分块
        '''

        s3_download_db = S3DownloadDb.get_db()

        file_path = self.download_file_obj.path
        #分块写入文件的开始位置，保证已经下载过的文件内容，不重复下载
        #分块正确的写入位置为分块的开始位置+该分块已经下载过的字节数
        start_byte = self.file_range.start + s3_download_db.get_range_download_size(self.download_range_id)
        #每次下载的最小单元字节数
        block_size = config.DOWNLAD_BLOCK_SIZE
        read_size = 0
        #按最小单元每次下载16384个字节,直到字节流返回为空
        for chunk in iter(lambda:body.read(block_size),b''):
            #文件指针定位到正确的写入位置
            file_obj.seek(start_byte)
            #在某个正确的文件位置，写入字节流
            file_obj.write(chunk)
            #接收的字节流的大小
            chunk_length = len(chunk)
            #构建最小下载单元对象
            download_cell = DownloadCell(start_byte,chunk_length,0)
            start_byte += chunk_length
            #调用下载回调函数
            if callback is not None:
                callback(chunk_length)
            read_size += chunk_length 
            #计算下载进度
            download_size = float(s3_download_db.get_download_size(self.download_file_obj.download_id))
            download_size += chunk_length
            percent = '%.2f%%' % (100*download_size/self.download_file_obj.size)
            update_sql = '''
                update download set download_size=?,download_percent=?,status=? where id=?
            '''
            data = [(download_size,percent,const.STATUS_DOWNLOADING,self.download_file_obj.download_id),]
            s3_download_db.update(update_sql,data)
            logger.info('file:%s download percentage is %s ====================================download size(%d/%d)',file_path,percent,download_size,self.download_file_obj.size)
            logger.debug('download part:%d start:%d,block_size:%d',self.file_range.range_id,start_byte,block_size)
            #下载文件内容完成
            if download_size >= self.download_file_obj.size:
                #设置下载内容完成状态
                s3_download_db.set_download_status(const.STATUS_DOWNLOAD_FINISHED,self.download_file_obj.download_id)
            
            #更新分块已经下载字节数
            range_download_size = s3_download_db.get_range_download_size(self.download_range_id)
            range_download_size += chunk_length
            update_range_sql = '''
                update range set download_size=? where id=?
            '''
            data = [(range_download_size,self.download_range_id),]
            s3_download_db.update(update_range_sql,data)
        
        #设置分块下载成功，以及分块下载完成时间
        update_range_sql = '''
                update range set is_download=?,end_time=? where id=?
            '''
        data = [(True,datetime.datetime.now(),self.download_range_id),]
        s3_download_db.update(update_range_sql,data)
        #当分块下载完成后，下载的字节数必须等于分块的大小
        assert(s3_download_db.get_range_download_size(self.download_range_id) == self.file_range.size)
        return read_size

