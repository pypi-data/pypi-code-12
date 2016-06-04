#coding:utf-8
import os
import config
import sql
from awslib.common.logger import *
from awslib.base import singleton
from awslib.base.basedb import *
from boto import client
import utils
import awslib.base.utils


def get_db_path():
    app_data_path = utils.get_app_data_path()
    data_path = os.path.join(app_data_path,'data')
    awslib.base.utils.mkdirs(data_path)

    return data_path

class S3UploadDb(BaseDb):

    '''
        上传文件数据库类
    '''
    #设置该类是单例
    __metaclass__ = singleton.Singleton

    def __init__(self):
        
        db_dir = get_db_path()
        db_path = os.path.join(get_db_path(),config.DATA_DB_NAME)

        super(S3UploadDb,self).__init__(db_path)
        self.init_upload_db()

    @classmethod
    def get_db(cls):
        return S3UploadDb()

    def init_upload_db(self):

        table_already_exist_flag = 'already exists'

        #创建upload表，表存在时不抛异常
        try:
            self.create_table(sql.CREATE_UPLOAD_TABLE_SQL,config.UPLOAD_TABLE)
            logger.info('create table %s success',config.UPLOAD_TABLE)
        except sqlite3.OperationalError,e:
            if str(e).find(table_already_exist_flag) == -1:
                print e
                return 

        #创建part表，表存在时不抛异常
        try:
            self.create_table(sql.CREATE_PART_TABLE_SQL,config.UPLOAD_PART_TABLE)
            logger.info('create table %s success',config.UPLOAD_PART_TABLE)
        except sqlite3.OperationalError,e:
            if str(e).find(table_already_exist_flag) == -1:
                print e
                return 

        #创建file表，表存在时不抛异常
        try:
            self.create_table(sql.CREATE_FILE_TABLE_SQL,config.UPLOAD_FILE_TABLE)
            logger.info('create table %s success',config.UPLOAD_FILE_TABLE)
        except sqlite3.OperationalError,e:
            if str(e).find(table_already_exist_flag) == -1:
                print e
                return 

    def get_file_id_id_by_hash(self,file_hash):
        '''
            通过文件hash值获取文件id
        '''
        query_sql = '''
                select id from file where hash='%s'
            ''' % (file_hash)

        result = self.fetchone(query_sql)
        if not result:
            return None
        return result[0]
    
    def get_upload_id(self,s3_upload_id):
        '''
            通过s3上的upload_id获取数据库里面自增的upload_id
        '''
        query_sql = '''
            select id from upload where s3_upload_id='%s'
        ''' % (s3_upload_id)

        result = self.fetchone(query_sql)
        if not result:
            return None
        return result[0]
  
    def get_upload_id_by_fileid(self,file_id):
        '''
            通过文件id获取上传id
        '''
        query_sql = '''
            select id from upload where file_id=%d
        ''' % (file_id)

        result = self.fetchone(query_sql)
        if not result:
            return None
        return result[0]

    def get_upload_size(self,file_id):
        
        query_sql = '''
            select upload_size from upload where id=%d
        ''' % (file_id)

        result = self.fetchone(query_sql)
        return result[0]

    def delete_upload(self,file_id):
        '''
            删除该上传相关联的所有表
        '''
        delete_sql = '''
            delete from file where id=%d
        ''' % (file_id)
        self.delete(delete_sql)
        upload_id = self.get_upload_id_by_fileid(file_id)

        #删除上传信息时，删除s3上保留的分块信息
        query_sql = '''
            select bucket,key,s3_upload_id from upload where id=%d
        ''' % (upload_id)
        bucket,key,s3_upload_id = self.fetchone(query_sql)
        try:
            client.abort_multipart_upload(
                Bucket=bucket,Key=key,UploadId=s3_upload_id,
            )
        except Exception,e:
            logger.warn("%s",e)

        delete_sql = '''
            delete from part where upload_id=%d
        ''' % (upload_id)
        self.delete(delete_sql)

        delete_sql = '''
            delete from upload where file_id=%d
        ''' % (file_id)
        self.delete(delete_sql)
    
    def set_upload_status(self,status,upload_id):

        update_sql = '''
            update upload set status=%d where id=%d
        ''' % (status,upload_id)

        self.update(update_sql)

class S3DownloadDb(BaseDb):
    '''
        下载文件数据库类
    '''

    #表示该类是单例类
    __metaclass__ = singleton.Singleton

    def __init__(self):
        
        db_dir = get_db_path()
        db_path = os.path.join(db_dir,config.DATA_DB_NAME)
        super(S3DownloadDb,self).__init__(db_path)
        self.init_download_db()

    @classmethod
    def get_db(cls):
        return S3DownloadDb()

    def init_download_db(self):

        table_already_exist_flag = 'already exists'

        #创建download表，表存在时不抛异常
        try:
            self.create_table(sql.CREATE_DOWNLOAD_TABLE_SQL,config.DOWNLOAD_TABLE)
            logger.info('create table %s success',config.DOWNLOAD_TABLE)
        except sqlite3.OperationalError,e:
            if str(e).find(table_already_exist_flag) == -1:
                print e
                return 

        #创建range表，表存在时不抛异常
        try:
            self.create_table(sql.CREATE_DOWNLOAD_RNAGE_TABLE_SQL,config.DOWNLOAD_RANGE_TABLE)
            logger.info('create table %s success',config.DOWNLOAD_RANGE_TABLE)
        except sqlite3.OperationalError,e:
            if str(e).find(table_already_exist_flag) == -1:
                print e
                return 

    def get_download_id(self,bucket,key):

        query_sql = '''
            select id from download where bucket=? and key=?
        ''' 

        data = (bucket,key)
        result = self.fetchone(query_sql,data)
        if not result:
            return None
        return result[0]
    
    def get_download_info(self,id):

        query_sql = '''
            select download_size,tmp_file_path,is_download from download where id=%d
        ''' % (id)
        result = self.fetchone(query_sql)
        return result
    
    def delete_download(self,id):
        '''
            删除该下载相关联的所有表
        '''
        
        query_sql = '''
            select tmp_file_path from download where id=%d
        ''' % (id)
        tmp_file_path = self.fetchone(query_sql)[0]
        #重新下载时，删除上次下载产生的临时文件
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

        delete_sql = '''
            delete from download where id=%d
        ''' % (id)
        self.delete(delete_sql)
       
        delete_sql = '''
            delete from range where download_id=%d
        ''' % (id)
        self.delete(delete_sql)

    def get_download_size(self,download_id):
        
        query_sql = '''
            select download_size from download where id=%d
        ''' % (download_id)

        result = self.fetchone(query_sql)
        return result[0]
    
    def reset_download_size(self,download_size,download_id):

        update_sql = '''
            update download set download_size=%d where id=%d
        ''' % (download_size,download_id)

        self.update(update_sql)

    def get_download_status(self,download_id):
        
        query_sql = '''
            select status from download where id=%d
        ''' % (download_id)

        result = self.fetchone(query_sql)
        return result[0]

    def set_download_status(self,status,download_id):

        update_sql = '''
            update download set status=%d where id=%d
        ''' % (status,download_id)

        self.update(update_sql)
    
    def get_range_number(self,download_id):
        
        query_sql = '''
            select range_num from download where id=%d
        ''' % (download_id)

        result = self.fetchone(query_sql)
        return result[0]
  
    def get_range_download_size(self,range_id):
        
        query_sql = '''
            select download_size from range where id=%d
        ''' % (range_id)

        result = self.fetchone(query_sql)
        return result[0]
  
