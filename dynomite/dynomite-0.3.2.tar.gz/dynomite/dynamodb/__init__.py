import json
import boto.datapipeline
import boto.s3
import boto.s3.connection
import boto.iam
import yaml
from string import Template
from retrying import retry
import os
from multiprocessing import current_process
from dynomite import *
import uuid


class BackupNotCompleteError(Exception):
    def __init__(self, msg):
        self.msg = msg


class BackupComponentCreationError(Exception):
    def __init__(self, msg):
        self.msg = msg


def get_tables_from_stack_definition(stack_definition, exclude_tables_str):
    tables = []

    try:
        exclude_tables = exclude_tables_str.split(',')
    except AttributeError:
        exclude_tables = []

    with open(stack_definition, 'r') as f:
        config = yaml.load(f.read())

    for table in config['aws']['dynamodb']:
        if 'delete' not in config['aws']['dynamodb'][table]:
            tables.append(table)

    for excluded_table in exclude_tables:
        if excluded_table in tables:
            tables.remove(excluded_table)

    return tables


def __create_pipeline_definition__(region, table, action,
                                   bucket_name, backup=None):
    path = os.path.dirname(os.path.realpath(__file__))
    with open(
        '%s/templates/%s_pipeline_def.json' % (path, action), 'r'
    ) as f:
        pipeline_definition = f.read()

    d = dict(region=region,
             table=table,
             bucket_name=bucket_name,
             backup=backup)

    s = Template(pipeline_definition)

    return json.loads(s.safe_substitute(d))


def worker(work_queue, done_queue):
    for pipeline_options in iter(work_queue.get, 'STOP'):
        status = create_pipeline(pipeline_options)
        done_queue.put("%s - %s" % (current_process().name, status))

    return True


def create_pipeline((dp_conn, dynamodb_conn, s3_conn_dest, s3_conn_src,
                     region, table, action, read_pt_increase,
                     write_pt_increase, date, backup_bucket, debug)):
    logger = set_logging(level=debug)
    backup = None
    backup_status = True

    logger.info('Executing %s of table %s' % (action, table))
    if action == 'restore':
        if __check_pt_decreases__:
            original_pt = __get_pt__(dynamodb_conn, table)
            increased_pt = __increase_pt__(
                dynamodb_conn,
                table,
                original_pt,
                debug,
                write_increase_percentage=write_pt_increase
            )
        else:
            logger.info(
                'Not increasing read PT due to too '
                'many decreases on table: %s' % (table)
            )
        backup = __get_backup__(
            s3_conn_src, region, backup_bucket, table, date, debug
        )
        tmp_bucket_name = tmp_bucket_name = str(uuid.uuid4())
        source_path = 'data/%s/%s/%s' % (region, table, backup)
        copy_backup_from_source(s3_conn_dest,
                                backup_bucket,
                                tmp_bucket_name,
                                debug,
                                source_path=source_path)

        backup_bucket = tmp_bucket_name

        if not backup:
            logger.info('No backup exists on %s for table %s' % (date, table))
            backup_status = False

    elif action == 'backup':
        if __check_pt_decreases__:
            original_pt = __get_pt__(dynamodb_conn, table)
            increased_pt = __increase_pt__(
                dynamodb_conn,
                table,
                original_pt,
                debug,
                read_increase_percentage=read_pt_increase
            )
        else:
            logger.info(
                'Not increasing read PT due to too '
                'many decreases on table: %s' % (table)
            )
        try:
            s3_conn_src.create_bucket(backup_bucket, location='EU')
        except boto.exception.S3CreateError:
            logger.debug('Backup bucket creation '
                         'failed, %s exists' % backup_bucket)

    pipeline_definition = __create_pipeline_definition__(region,
                                                         table,
                                                         action,
                                                         backup_bucket,
                                                         backup)

    logger.debug(
        'Pipeline definition for action:%s and table:%s' % (action, table)
    )
    logger.debug(pipeline_definition)

    pipelines = dp_conn.list_pipelines()['pipelineIdList']
    logger.debug('Pipelines in account: %s' % pipelines)
    if len(pipelines) == 0:
        logger.debug('No pipelines returned from list pipeline function call')
    for pipeline in pipelines:
        if pipeline['name'] == '%s-%s' % (table, action):
            logger.info('Pipeline with name %s-%s exists' % (table, action))
            dp_conn.delete_pipeline(pipeline['id'])
            logger.info('Pipeline with name %s-%s deleted' % (table, action))

    response = dp_conn.create_pipeline('%s-%s' % (table, action), table, None)
    pipeline_id = response['pipelineId']
    dp_conn.put_pipeline_definition(pipeline_definition,
                                    response['pipelineId'])

    try:
        dp_conn.activate_pipeline(pipeline_id)
    except:
        logger.error(
            'Unable to create pipline %s-%s due to errors '
            'in the definition' % (table, action)
        )
        backup_status = False

    logger.info('Created pipeline for table: %s' % table)

    status = __check_status__(dp_conn, pipeline_id, table, action, debug)

    if status == 'success':
        logger.info('Deleting pipeline for table: %s' % table)
        dp_conn.delete_pipeline(pipeline_id)
        backup_status = True
    else:
        backup_status = False

    __restore_pt__(dynamodb_conn, table, original_pt, increased_pt, debug)

    if action == 'restore':
        logger.info('Deleting temporary bucket %s' % tmp_bucket_name)
        b = boto.s3.bucket.Bucket(connection=s3_conn_dest,
                                  name=tmp_bucket_name)
        for k in b:
            k.delete()
        b.delete()

    return backup_status


@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000)
def __check_pt_decreases__(conn, table):
    t = dynamodb_conn.describe_table(table)
    n_decreases_today = \
        t['Table']['ProvisionedThroughput']['NumberOfDecreasesToday']

    return n_decreases_today < 3


@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000)
def __get_pt__(conn, table):
    t = conn.describe_table(table)
    read_pt = t['Table']['ProvisionedThroughput']['ReadCapacityUnits']
    write_pt = t['Table']['ProvisionedThroughput']['WriteCapacityUnits']

    return dict(read=read_pt, write=write_pt)


@retry(wait_exponential_multiplier=1000,
       wait_exponential_max=10000,
       stop_max_attempt_number=7)
def __increase_pt__(conn,
                    table,
                    original_pt,
                    debug,
                    read_increase_percentage=None,
                    write_increase_percentage=None):
    logger = set_logging(level=debug)

    increase_factor = {}

    if not read_increase_percentage and not write_increase_percentage:
        logger.info('Not increasing throughput')
        return None
    try:
        increase_factor['read'] = \
            original_pt['read'] * float(read_increase_percentage)
    except TypeError:
        increase_factor['read'] = 0
        logger.info('Not increasing read throughput for table %s' % table)
    try:
        increase_factor['write'] = \
            original_pt['write'] * float(write_increase_percentage)
    except TypeError:
        increase_factor['write'] = 0
        logger.info('Not increasing write throughput for table %s' % table)

    updated_pt = dict(
        read=int(original_pt['read'] + increase_factor['read']),
        write=int(original_pt['write'] + increase_factor['write'])
    )

    logger.info(
        'Increasing read PT from %d to %d' % (original_pt['read'],
                                              updated_pt['read'])
    )

    logger.info(
        'Increasing write PT from %d to %d' % (original_pt['write'],
                                               updated_pt['write'])
    )

    throughput = {'ReadCapacityUnits': updated_pt['read'],
                  'WriteCapacityUnits': updated_pt['write']}

    conn.update_table(table, provisioned_throughput=throughput)

    return updated_pt


@retry(wait_exponential_multiplier=1000,
       wait_exponential_max=10000,
       stop_max_attempt_number=7)
def __restore_pt__(conn, table, original_pt, increased_pt, debug):
    logger = set_logging(level=debug)

    if not increased_pt:
        logger.info('Not decreasing throughput for table %s' % (table))
        return None

    logger.info('Restoring read pt from %s to %s for table: %s' % (
                increased_pt['read'],
                original_pt['read'],
                table))

    logger.info('Restoring write pt from %s to %s for table: %s' % (
                increased_pt['write'],
                original_pt['write'],
                table))

    throughput = {'ReadCapacityUnits': original_pt['read'],
                  'WriteCapacityUnits': original_pt['write']}

    conn.update_table(table, provisioned_throughput=throughput)


@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000)
def __check_status__(conn, pipeline_id, table, action, debug):
    logger = set_logging(level=debug)

    pipeline_metadata = conn.describe_pipelines([pipeline_id])
    for d in pipeline_metadata['pipelineDescriptionList'][0]['fields']:
        if d['key'] == '@pipelineState':
            state = d['stringValue']
        if d['key'] == '@healthStatus':
            health_status = d['stringValue']

    if state == 'FINISHED' and health_status == 'ERROR':
        status = 'fail'
        logger.error('%s %s failed' % (table, action))
    elif state != 'FINISHED':
        raise BackupNotCompleteError('Backup still running')
    else:
        status = 'success'
        logger.info('%s %s finished' % (table, action))

    return status


def __get_backup__(s3_conn, region, bucket_name, table, date, debug):
    logger = set_logging(level=debug)
    logger.info('Getting path to the latest backup')

    b = boto.s3.bucket.Bucket(connection=s3_conn, name=bucket_name)

    for k in b.list(prefix='data/%s/%s/%s' % (region, table, date)):
        logger.debug('Latest backup is %s' % (k.key))
        backup = k.key.split('/')[3]
        return backup


def set_iam_roles(iam_conn, debug):
    logger = set_logging(level=debug)

    logger.info('Creating IAM roles')
    path = os.path.dirname(os.path.realpath(__file__))

    try:
        iam_conn.remove_role_from_instance_profile(
            'DataPipelineDefaultResourceRole',
            'DataPipelineDefaultResourceRole'
        )
    except boto.exception.BotoServerError, e:
        logger.debug('Failed to remove role: DataPipelineDefaultResourceRole '
                     'from instance profile: DataPipelineDefaultResourceRole')
        logger.debug(e)
    else:
        logger.debug('Removed role: DataPipelineDefaultResourceRole '
                     'from instance profile: DataPipelineDefaultResourceRole')

    try:
        iam_conn.delete_role_policy('DataPipelineDefaultResourceRole',
                                    'AmazonEC2RoleforDataPipelineRole')
    except boto.exception.BotoServerError, e:
        logger.debug('Failed to remove policy: '
                     'AmazonEC2RoleforDataPipelineRole '
                     'from role: DataPipelineDefaultResourceRole')
        logger.debug(e)
    else:
        logger.debug('Removed policy: AmazonEC2RoleforDataPipelineRole '
                     ' from role: DataPipelineDefaultResourceRole')

    try:
        iam_conn.delete_role_policy('DataPipelineDefaultRole',
                                    'AWSDataPipelineRole')
    except boto.exception.BotoServerError, e:
        logger.debug('Failed to remove policy: AWSDataPipelineRole  '
                     'from role: DataPipelineDefaultRole')
        logger.debug(e)
    else:
        logger.debug('Removed policy: AWSDataPipelineRole '
                     ' from role: DataPipelineDefaultRole')

    try:
        iam_conn.delete_role('DataPipelineDefaultResourceRole')
    except boto.exception.BotoServerError, e:
        logger.debug('Attempt to delete'
                     'DataPipelineDefaultResourceRole role failed')
        logger.debug(e)
    else:
        logger.debug('Deleted DataPipelineDefaultResourceRole role')

    try:
        iam_conn.delete_role('DataPipelineDefaultRole')
    except boto.exception.BotoServerError, e:
        logger.debug('Attempt to delete DataPipelineDefaultRole role failed')
        logger.debug(e)
    else:
        logger.debug('Deleted DataPipelineDefaultRole role')

    try:
        iam_conn.delete_instance_profile('DataPipelineDefaultResourceRole')
    except boto.exception.BotoServerError:
        logger.debug('Attempt to delete DataPipelineDefaultResourceRole '
                     'instance profile failed')
        logger.debug(e)
    else:
        logger.debug('Deleted DataPipelineDefaultResourceRole '
                     'instance profile')

    try:
        iam_conn.create_instance_profile('DataPipelineDefaultResourceRole')
        logger.debug('Created instance profile: '
                     'DataPipelineDefaultResourceRole')
    except boto.exception.BotoServerError, e:
        logger.debug('Failed to create instance profile '
                     'DataPipelineDefaultResourceRole')
        logger.debug(e)
    else:
        logger.debug('Created instance profile: '
                     'DataPipelineDefaultResourceRole')

    try:
        with open('%s/templates/data_pipeline_default_'
                  'resource_role_policy.json' % (path), 'r') as f:
            policy_document = f.read()
        iam_conn.create_role('DataPipelineDefaultResourceRole',
                             assume_role_policy_document=policy_document)
        logger.debug('Created role: DataPipelineDefaultResourceRole')
    except boto.exception.BotoServerError, e:
        logger.error('Failed to create role: DataPipelineDefaultsourceRole')
        logger.error(e)
        sys.exit(1)
    else:
        with open('%s/templates/data_pipeline'
                  '_default_resource_role.json' % (path), 'r') as f:
            policy_document = f.read()
        iam_conn.put_role_policy('DataPipelineDefaultResourceRole',
                                 'AmazonEC2RoleforDataPipelineRole',
                                 policy_document)
        iam_conn.add_role_to_instance_profile(
            'DataPipelineDefaultResourceRole',
            'DataPipelineDefaultResourceRole'
        )
        logger.debug('Added role: DataPipelineDefaultResourceRole to instance '
                     'profile: DataPipelineDefaultResourceRole')

    try:
        with open('%s/templates/data_pipeline_'
                  'default_role_policy.json' % (path), 'r') as f:
            policy_document = f.read()
        iam_conn.create_role('DataPipelineDefaultRole',
                             assume_role_policy_document=policy_document)
        logger.debug('Created role: DataPipelineDefaultRole')
    except boto.exception.BotoServerError:
        logger.error('Failed to create role: DataPipelineDefaultRole')
        sys.exit(1)
    else:
        with open('%s/templates/data_pipeline_'
                  'default_role.json' % (path), 'r') as f:
            policy_document = f.read()
        iam_conn.put_role_policy('DataPipelineDefaultRole',
                                 'AWSDataPipelineRole',
                                 policy_document)


def restore():
    pass
