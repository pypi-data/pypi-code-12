from __future__ import print_function

import boto3
import botocore.exceptions


def shorten_region_name(s):
    alternatives = {
        'use1': {'us-east-1', },
        'usw1': {'us-west-1', },
        'usw2': {'us-west-2', },
        'sae1': {'sa-east-1', },
        'apn1': {'ap-northeast-1', },
        'apn2': {'ap-northeast-2', },
        'aps1': {'ap-southeast-1', },
        'ap22': {'ap-southeast-2', },
        'euw1': {'eu-west-1', },
        'euc1': {'eu-central-1', },
    }

    s = s.lower()

    for sn, candidates in alternatives.items():
        if s in candidates:
            return sn

    return s


class S3(object):
    AUTOMATION_BUCKET_FORMAT = "e104-automation-%s"

    def automation_bucket_name(self):
        return self.AUTOMATION_BUCKET_FORMAT % shorten_region_name(self.get_region())

    def __init__(self, s3_resource=None):
        self._s3r = s3_resource or boto3.resource('s3')

    def get_region(self):
        return getattr(self._s3r.meta.client, '_client_config').region_name

    def safe_create_bucket(self, bucket_name, region=None):
        try:
            return self._s3r.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    "LocationConstraint": region or self.get_region()
                }
            )
        except botocore.exceptions.ClientError:
            pass

        return self._s3r.Bucket(bucket_name)

    def upload(self, source, bucket_name, s3_key):
        """
        :param str source: file path or body
        :param bucket_name:
        :param s3_key:
        :return:
        """
        obj = self.safe_create_bucket(bucket_name).Object(s3_key)

        with open(source, 'rb') as fp:
            obj.put(Body=fp)

        return s3_key

    def cleanup_bucket(self, bucket_name):
        print("  * Cleaning up bucket `%s`" % bucket_name)
        bucket = self._s3r.Bucket(bucket_name)

        bucket.delete_objects(
            Delete={
                "Objects": [
                    {"Key": obj.key} for obj in bucket.objects.all()
                ]
            }
        )
