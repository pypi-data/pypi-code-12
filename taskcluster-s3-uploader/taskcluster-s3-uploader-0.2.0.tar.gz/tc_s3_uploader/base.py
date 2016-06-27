import os
import boto3

from taskcluster.sync import Auth


class TC_S3_Uploader():
    _BUCKET = 'tc-gp-public-31d'

    def __init__(self, bucket_prefix, region='us-west-2'):
        '''It helps upload files to a short term storage S3 bucket using TaskCluster auth.'''
        # This is to make sure that you have set TASKCLUSTER_CLIENT_ID and
        # TASKCLUSTER_ACCESS_TOKEN as environment variables.
        #
        # The TaskCluster client you're referring to should contain this scope:
        #     auth:aws-s3:read-write:tc-gp-public-31d/%(bucket_prefix)s/*
        os.environ['TASKCLUSTER_CLIENT_ID']
        os.environ['TASKCLUSTER_ACCESS_TOKEN']

        self.bucket_prefix = bucket_prefix
        self.region = region

        # Obtain temporary S3 credentials via TaskCluster's API
        # https://docs.taskcluster.net/reference/platform/auth/api-docs#awsS3Credentials
        credentials = Auth().awsS3Credentials(
            level='read-write',
            bucket=self._BUCKET,
            prefix=bucket_prefix,
        )

        self.s3_client = boto3.client(
            service_name='s3',
            region_name=self.region,
            aws_access_key_id=credentials['credentials']['accessKeyId'],
            aws_secret_access_key=credentials['credentials']['secretAccessKey'],
            aws_session_token=credentials['credentials']['sessionToken'],
        )

    def upload(self, filepath):
        '''Upload file to AWS S3 bucket and key specified.'''
        remote_file_path = os.path.join(self.bucket_prefix, filepath.split('/')[-1])

        with open(filepath, 'r') as file:
            # Upload the file to S3
            # http://boto3.readthedocs.io/en/latest/reference/services/s3.html#S3.Client.upload_file
            self.s3_client.upload_file(
                Filename=filepath,
                Bucket=self._BUCKET,
                Key=remote_file_path,
                ExtraArgs={'ContentType': "application/json"}
            )

        return "https://{}.s3-{}.amazonaws.com/{}".format(
            self._BUCKET,
            self.region,
            remote_file_path
        )
