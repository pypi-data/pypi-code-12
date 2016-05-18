import boto.s3
from dynomite import *


def create_backup_bucket(backup_s3_conn, debug):
    logger = set_logging(level=debug)
    backup_bucket_name = 'socotra-document-backups'
    try:
        backup_s3_conn.create_bucket(backup_bucket_name,
                                     location='EU')
        logger.debug('Created bucket: %s' % backup_bucket_name)
    except boto.exception.S3CreateError:
        logger.debug('Destination bucket already exists')

    return backup_bucket_name


def cleanup_destination(backup_s3_conn, bucket, path):
    try:
        b = backup_s3_conn.get_bucket(bucket)
    except boto.exception.S3ResponseError:
        pass
    else:
        for k in b.list(prefix=path):
            k.delete()
