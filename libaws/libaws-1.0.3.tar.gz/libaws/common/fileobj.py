#coding:utf-8
import os
import datetime
import re
import utils
from libaws.base import filerange,md5
from libaws.common.logger import *

class FileObj(object):

    '''
        文件对象类
    '''

    def __init__(self,file_path):
        self._path = file_path
        self._name = os.path.basename(file_path) 
        self._hash = None
        self._etag = None
        self._size = None
        self._date_time = None
        self._is_multipart_upload = False

    @property
    def path(self):
        '''
            文件路径
        '''
        return self._path
    
    @path.setter
    def path(self,path):
        self._path = path

    @property
    def size(self):
        '''
            文件大小
        '''
        return self._size
    
    @size.setter
    def size(self,size):

        if size < 0:
            raise ValueError('size must greater 0')

        self._size = size

    @property
    def hash(self):
        '''
            文件hash值
        '''
        return self._hash
    
    @hash.setter
    def hash(self,hash):
        self._hash = hash
    
    @property
    def etag(self):
        '''
            文件在亚马逊s3上存储的e_tag值,用来校验文件的完整性
        '''
        return self._etag
    
    @etag.setter
    def etag(self,etag):
        '''
            设置文件的e_tag值
            注意s3上存储文件的e_tag值有2种，如果该文件是
            单块上传的话，则其e_tag值为文件的md5值，
            如果该文件时分块上传的话，则其e_tag值各块的md5值汇总后再算一次md5值+分块的大小,
            其格式为:xxxxxxxxxxxx-d，具体算法参加utils.get_etag函数,
            反之如果知道文件的e_tag值，可以根据其格式反向推算该文件是分块上传还是单块上传文件
        '''
        etag = utils.get_format_tag(etag)
        regstr = r'^(\w*)-(\d)'
        p = re.compile(regstr)
        match = p.match(etag)
        if match:
            #如果符合字母-数字正则表达式的e_tag,说明该文件是分块上传文件
            #校验文件hash值时有用
            self._is_multipart_upload = True
        self._etag = etag
    
    @property
    def name(self):
        '''
            文件名
        '''
        return self._name
    
    @property
    def is_multipart_upload(self):
        '''
            表示文件是分块上传还是单块上传，默认为单块上传
        '''
        return self._is_multipart_upload
    
    def get_hash(self):
        '''
            计算文件的md5值
        '''
        assert(os.path.exists(self.path))
        return md5.get_file_md5(self.path)

    def validate(self):
        '''
            校验文件的hash值，即校验文件的完整性
        '''
        assert(self.etag != None)
        return self.hash == self.etag
    
    def get_file_range_md5s(self,part_number):
        '''
            按分块个数对文件进行分块，并计算各个分块内容的md5值
        '''
        file_size = self.size
        file_path = self.path
        file_ranges = filerange.get_file_ranges_by_part(file_path,part_number,file_size)
        md5s = []
        for file_range in file_ranges:
            block_size,start_byte,end_byte = file_range.size,file_range.start,file_range.end
            with open(file_path,'rb') as f:
                f.seek(start_byte,0)
                assert(block_size == (end_byte - start_byte))
                rd = f.read(block_size)
                rd_md5 = md5.get_str_md5(rd)
                logger.debug('path:%s, part_id:%d, hash:%s',file_path,file_range.range_id,rd_md5)
                md5s.append(rd_md5)
        return md5s

class UploadFileObj(FileObj):
    '''
        上传文件对象
    '''

    def __init__(self,file_path):

        super(UploadFileObj,self).__init__(file_path)
        self._file_id = None
        self._upload_id = None
        file_path = os.path.abspath(file_path)
        self.path = file_path
        self.hash = self.get_hash()
        self.time_stamp = os.path.getmtime(file_path)
        self.size = os.path.getsize(file_path)
        file_time = datetime.datetime.fromtimestamp(self.time_stamp) 
    
        time_format = '%Y-%m-%d %H:%M:%S'
        file_time_str = file_time.strftime(time_format)
        self.date_time = datetime.datetime.strptime(file_time_str, time_format)

    @property
    def upload_id(self):
        return self._upload_id

    @upload_id.setter
    def upload_id(self,value):

        if not isinstance(value, int):
            raise ValueError('upload_id must be an integer!')
        if value < 0:
            raise ValueError('upload_id must greater 0')
        self._upload_id = value

    @property
    def file_id(self):
        return self._file_id

    @file_id.setter
    def file_id(self,value):

        if not isinstance(value, int):
            raise ValueError('file_id must be an integer!')
        if value < 0:
            raise ValueError('file_id must greater 0')
        self._file_id = value

    def validate(self,md5s=None):
        '''
            校验上传文件的一致性，注意分块和单块文件的校验方法不一样
        '''
        if self.is_multipart_upload:
            dest_tag = utils.get_etag(md5s)
            logger.debug('path:%s, hash tag:%s,object tag:%s',self.path,dest_tag,self.etag)
            if self.etag !=  dest_tag:
                return False
            return True
        else:
            return super(UploadFileObj,self).validate()

class DownloadFileObj(FileObj):
    '''
        下载文件对象
    '''
    def __init__(self,file_path,tmp_file_path,size,etag):

        super(DownloadFileObj,self).__init__(file_path)
        self.size = size
        self.etag = etag
        tmp_file_path = os.path.abspath(tmp_file_path)
        self._tmp_file_path = tmp_file_path
        self.path = os.path.abspath(file_path)
        self._download_id = None
    
    @property
    def tmp_file_path(self):
        '''
            下载临时文件名
        '''
        return self._tmp_file_path

    def validate(self):
        '''
            校验下载文件的一致性，注意分块和单块文件的校验方法不一样
        '''
        if not os.path.exists(self.path):
            logger.error('download file:%s is not exists',self.path)
            return False

        #分块文件校验
        if self.is_multipart_upload:
            regstr = r'^(\w*)-(\d)'
            p = re.compile(regstr)
            match = p.match(self.etag)
            md5s_hash,part_num = match.groups()
            part_num = int(part_num)
            md5s = self.get_file_range_md5s(part_num)
            dest_tag = utils.get_etag(md5s)
            logger.debug('path:%s, hash tag:%s,object tag:%s',self.path,dest_tag,self.etag)
            if self.etag !=  dest_tag:
                return False

            return True
        else:
            #单块文件校验
            return super(DownloadFileObj,self).validate()
    
    @property
    def download_id(self):
        return self._download_id
   
    @download_id.setter
    def download_id(self,value):

        if not isinstance(value, int):
            raise ValueError('download_id must be an integer!')
        if value < 0:
            raise ValueError('download_id must greater 0')
        self._download_id = value

