import boto3
from botocore.exceptions import ClientError

from simplefsabstraction.interface import SimpleFS


class S3FS(SimpleFS):
    class BucketNotFoundError(Exception):
        def __init__(self, bucket_name):
            super().__init__('Bucket "{}" does not exist'.format(bucket_name))

    def __init__(self, bucket_name):
        self._s3 = boto3.resource('s3')
        self.bucket_name = bucket_name
        print(boto3.client('s3').list_buckets())

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

    def save(self, source_file, dest_name):
        if not self._bucket_exists(self.bucket_name):
            raise S3FS.BucketNotFoundError(self.bucket_name)

        self._s3.Object(self.bucket_name, dest_name).put(Body=open(source_file, 'rb'))
