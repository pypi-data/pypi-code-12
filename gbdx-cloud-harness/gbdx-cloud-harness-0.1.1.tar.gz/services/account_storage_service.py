import os
import boto3
from boto3.s3.transfer import S3Transfer

from gbdx_auth import gbdx_auth
from utils.printer import printer


class AccountStorageService(object):
    """
    Provides an interface to a Users Account Storage (S3). To be used when accessing
    the users account storage. All access is through the GBDX temporary credentials service.
    """

    def __init__(self, session=None):

        endpoint = 'https://geobigdata.io/s3creds/v1/prefix'

        if session is None:
            session = gbdx_auth.get_session()

            response = session.get('%s?duration=3600' % endpoint)

            if response.status_code != 200:
                raise Exception('%s: %s' % (response.status_code, response.content))

            secret_key = response.json()['S3_secret_key']
            access_key = response.json()['S3_access_key']
            session_token = response.json()['S3_session_token']

            session = boto3.session.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                aws_session_token=session_token
            )

            self.bucket = response.json()['bucket']
            self.prefix = response.json()['prefix']

        else:
            # session is not None, meaning it is being overridden.
            # Testing purposes.
            self.bucket = "not_provided"
            self.prefix = "not_provided"

        self.client = session.client('s3')
        self.s3 = S3Transfer(self.client)

    @property
    def location(self):
        return 's3://%s/%s' % (self.bucket, self.prefix)

    def upload(self, source_files, s3_folder=None):
        """
        Upload a list of files to a users account location
        :param source_files: list of files to upload, or single file name
        :param s3_folder: the user location to upload to.
        """

        if s3_folder is None:
            folder = self.prefix
        else:
            folder = '%s/%s' % (self.prefix, s3_folder)

        if isinstance(source_files, list):
            for file_tuple in source_files:
                self.__upload_file(file_tuple, folder)
        elif isinstance(source_files, tuple):
            self.__upload_file(source_files, folder)
        else:
            raise ValueError("Source Files must be a tuple or list of tuples: (filename, keyname)")

    def __upload_file(self, file_tuple, folder):
        key_name = '%s/%s' % (folder, file_tuple[1])
        printer('%s uploaded to location %s' % (file_tuple[0], file_tuple[1]))
        self.s3.upload_file(file_tuple[0], self.bucket, key_name)

    def download(self, local_port_path, key_names):
        """
        download all files from a users account location
        :param local_port_path: the local path where the data is to download to
        :param key_name: can start with self.prefix or taken as relative to prefix.

        Example:
            local_port_path = /home/user/myworkflow/input_images/ (sync all data in this folder)
            s3_folder = myworkflow/input_images/ (location on s3 that will be synced to local path)
        """

        if not os.path.isdir(local_port_path):
            raise ValueError("Download path does not exist: %s" % local_port_path)

        if not isinstance(key_names, list):
            key_names = [key_names]

        for key_name in key_names:
            is_folder = key_name.endswith('/')

            # strip leading and trailing slashes
            key_name = key_name.lstrip('/').rstrip('/')
            key_parts = key_name.split('/')

            # Key names from the list function will include the account prefix
            # and any folder namespace.
            if key_parts[0] == self.prefix:
                path = os.path.join(local_port_path, *key_parts[1:])
                if not is_folder:
                    folder_path = os.path.join(local_port_path, *key_parts[1:-1])
                get_key_name = key_name
            else:
                path = os.path.join(local_port_path, *key_parts)
                if not is_folder:
                    folder_path = os.path.join(local_port_path, *key_parts[:-1])
                get_key_name = '%s/%s' % (self.prefix, key_name)

            if is_folder and not os.path.isdir(path):
                # A directory that doesn't exist
                os.makedirs(path)
            else:
                if not os.path.isdir(folder_path):
                    os.makedirs(folder_path)
                # Assume it is a file
                self.__download_file(path, get_key_name)

    def __download_file(self, filename, key_name):
        self.client.download_file(self.bucket, key_name, filename)

    def list(self, s3_folder='', full_key_data=False):
        """Get a list of keys for the accounts"""
        if not s3_folder.startswith('/'):
            s3_folder = '/' + s3_folder

        s3_prefix = self.prefix + s3_folder

        bucket_data = self.client.list_objects(Bucket=self.bucket, Prefix=s3_prefix)

        if full_key_data:
            return bucket_data['Contents']
        else:
            return [k['Key'] for k in bucket_data['Contents']]
