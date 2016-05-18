import sys
import logging
import boto.iam
import boto.s3
import boto.dynamodb2
from string import Template
import os


def dp_connect_to_region(region, access_key_id, secret_access_key_id):
    return boto.datapipeline.connect_to_region(
        region,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key_id
    )


def dynamodb_connect_to_region(region, access_key_id, secret_access_key_id):
    return boto.dynamodb2.connect_to_region(
        region,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key_id
    )


def s3_connect_to_region(region, access_key_id, secret_access_key_id):
    return boto.s3.connect_to_region(
        region,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key_id
    )


def set_permissions_for_user(bucket_name,
                             iam_conn,
                             s3_conn,
                             debug):
    logger = set_logging(level=debug)

    logger.info('Setting permissions on bucket')

    user_info = \
        iam_conn.get_user()['get_user_response']['get_user_result']['user']

    logger.debug(user_info)

    try:
        user_name = user_info['user_name']
    except KeyError:
        logger.info('There is no username associated with the'
                    'dynamo account keys provided')
        sys.exit(1)
    user_arn = user_info['arn']

    b = boto.s3.bucket.Bucket(
        connection=s3_conn,
        name=bucket_name
    )

    path = os.path.dirname(os.path.realpath(__file__))
    with open('%s/templates/bucket_policy.json' % (path), 'r') as f:
        bucket_policy = f.read()

    logger.debug('Bucket name being passed to bucket '
                 'policy creation: %s' % bucket_name)
    d = dict(user_arn=user_arn,
             bucket_name=bucket_name)

    s = Template(bucket_policy)
    logger.debug('Bucket policy: %s' % s.safe_substitute(d))
    policy = s.safe_substitute(d)
    b.set_policy(policy)
    logger.debug('User policy for %s' % user_name)
    logger.debug(s.safe_substitute(d))

    logger.info('Setting permissions for user')
    with open('%s/templates/user_policy.json' % (path), 'r') as f:
        user_policy = f.read()

    s = Template(user_policy)

    user_policy = iam_conn.put_user_policy(
        user_name,
        '%s-%s-policy' % (user_name, bucket_name),
        s.safe_substitute(d))


def set_logging(level='info'):
    logger = logging.getLogger('dynomite')
    if not len(logger.handlers):
        if level == 'info':
            logger.setLevel(logging.INFO)
        elif level == 'debug':
            logger.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    return logger


def copy_backup_from_source(s3_conn, source_bucket_name,
                            destination_bucket_name,
                            debug, region='eu-west-1',
                            source_path=None,
                            destination_path=None):
    logger = set_logging(level=debug)

    try:
        dst_bucket = s3_conn.create_bucket(
            destination_bucket_name,
            location='EU'
        )
    except boto.exception.S3CreateError:
        dst_bucket = s3_conn.get_bucket(destination_bucket_name)
    src_bucket = s3_conn.get_bucket(source_bucket_name)

    logger.info('Copying backup data from %s to local bucket %s' % (
        source_bucket_name,
        destination_bucket_name)
    )

    if not source_path:
        prefix = ''
    else:
        prefix = source_path

    logger.debug(source_path)
    for k in src_bucket.list(prefix=prefix):
        if not source_path:
            source_path = k.key
        else:
            source_path = '%s/%s' % (source_path, k.key)
        if not destination_path:
            destination_path = k.key
        else:
            destination_path = '%s/%s' % (destination_path, k.key)

        logger.debug(
            'Copying %s/%s to %s/%s' % (source_bucket_name,
                                        source_path,
                                        destination_bucket_name,
                                        destination_path)
        )

        dst_bucket.copy_key(k.key, source_bucket_name, k.key)
