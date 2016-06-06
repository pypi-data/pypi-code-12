import boto3
from botocore.exceptions import ClientError

from simplefsabstraction.interface import SimpleFS


class S3FS(SimpleFS):
    class BucketNotFoundError(Exception):
        def __init__(self, bucket_name):
            super().__init__('Bucket "{}" does not exist'.format(bucket_name))

    def __init__(self, bucket_name, credentials=None):
        """
        :param bucket_name: the bucket to use
        :param credentials: a dictionary containing the credentials (keys:4 access_key and secret_key) (optional)
        """
        if credentials:
            self._session = boto3.Session(
                    aws_access_key_id=credentials['access_key'],
                    aws_secret_access_key=credentials['secret_key'],
            )
        else:
            self._session = boto3.Session()

        self._s3 = self._session.resource('s3')
        self.bucket_name = bucket_name

    def _bucket_exists(self, bucket_name):
        """
        Check whether a bucket exists or not
        :param bucket_name: the bucket name
        :return: False if the bucket does not exist, True otherwise
        """
        try:
            self._s3.meta.client.head_bucket(Bucket=bucket_name)
        except ClientError as e:
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                return False
            else:
                raise e
        return True

    def exists(self, file_name):
        if not self._bucket_exists(self.bucket_name):
            raise S3FS.BucketNotFoundError(self.bucket_name)

        try:
            self._s3.Object(self.bucket_name, file_name).load()
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                # File does not exist
                return False
            else:
                raise e
        return True

    def save(self, source_file, dest_name, randomize=False, extensions=None):
        if extensions and not self._check_extension(dest_name, extensions):
            raise SimpleFS.BadExtensionError()

        filename = self._random_filename() if randomize else dest_name

        if not self._bucket_exists(self.bucket_name):
            raise S3FS.BucketNotFoundError(self.bucket_name)

        # If the source file is a file name
        if type(source_file) is str:
            with open(source_file, 'rb') as body:
                self._s3.Object(self.bucket_name, filename).put(Body=body)
        # If it is already a file
        else:
            source_file.seek(0)
            self._s3.Object(self.bucket_name, filename).put(Body=source_file)

        return filename
