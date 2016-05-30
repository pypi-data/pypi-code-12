#Author: Partha

import os, shutil, tempfile
from sftp_api import SFTApi
from boto.s3.connection import S3Connection,Key

class SyncFtpS3(object):

    sftp = None

    def __init__(self, *args, **kwargs):
        ## Initialize remote ftp/sftp connection
        self.sftp = SFTApi(FTP_DOMAIN = kwargs['FTP_DOMAIN'],
                           FTP_PORT = kwargs['FTP_PORT'],
                           FTP_USERNAME = kwargs['FTP_USERNAME'], 
                           FTP_PASSWORD = kwargs['FTP_PASSWORD'])
        
        ## Initialize s3 connection
        self.AWS_ACCESS_KEY_ID = kwargs['AWS_ACCESS_KEY_ID']
        self.AWS_SECRET_ACCESS_KEY = kwargs['AWS_SECRET_ACCESS_KEY']
        self.S3_BUCKET = kwargs['S3_BUCKET']
        self._aws_s3()

    def _aws_s3(self):
        """ Connect to s3 with the given credentials """
        try:
            conn = S3Connection(self.AWS_ACCESS_KEY_ID, self.AWS_SECRET_ACCESS_KEY)
            self._bucket = conn.get_bucket(self.S3_BUCKET)
        except:
            print "Connection Error"


    def _downloadFromFtp(self, *args, **kwargs):
        """ It will download the contents from FTP Server and will place into _temp_location """
        self.sftp.download(type = kwargs['type'], 
            source = kwargs['source'], 
            destination = kwargs['destination'] + "/")

    def _uploadToS3(self, local_path, to_file_path, to_file_name, s3_path):
        """ It will upload each file into s3 """
        try:
            to_file_path = to_file_path.replace(local_path, "")
            if to_file_path.endswith("/"):
                to_file_path = to_file_path + "/"
            ## Write to s3            
            k = Key(self._bucket)
            k.key = s3_path + to_file_path + '/' + to_file_name
            f = open(local_path + to_file_path + "/" + to_file_name, 'r')
            k.set_contents_from_string(f.read())
            f.close()
        except:
            print "Fail:", local_path,to_file_path,to_file_name

    def sync(self, source = None, destination = None, _type = None):
        ## Temparory directory to work with
        self._temp_location = tempfile.mkdtemp()

        ## 1. Download files from ftp server to local_server
        self._downloadFromFtp(type = _type, 
            source = source, 
            destination = self._temp_location)
        
        ## 2. File by file upload to the s3 and then cloud
        for subdir, dirs, files in os.walk(self._temp_location):
            for file in files:
                self._uploadToS3(self._temp_location, subdir, file, destination)
        
        #3. Remove temperaroy directory & recreate with empty content
        try:
            shutil.rmtree(self._temp_location)
        except:
            pass

        



