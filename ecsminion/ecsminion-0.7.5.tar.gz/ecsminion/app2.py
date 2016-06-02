"""

Buckets can be inserted into bucket_stats_info owned by DEFAULT_NO_OWNER
when ecr doesn't receive a response in time back from ecs.

In these cases, we need to:
- Identify the DEFAULT_NO_OWNER records in bucket_stats_info
- For each record, query ecs to find if the bucket does actually exist
- If it does, insert the owner record to object_user_bucket_owner
- Update bucket_stats_info and bucket_stats_hourly with the correct owner

Usage:
    reconcile.py [--conf <conf>] [--start <start> --end <end>]
    [--verbose]

Options:
    -h --help           Show this screen.
    --version           Script version.
    --verbose           Turn on verbose logging
    --start             When to reconcile from (int hours prior to now)
    --conf=<conf>       Location of the YAML config
                        [default: /etc/silenus/config.yaml]
"""

# Standard lib imports
import logging

# Third-party imports
import docopt
from tendo import singleton
import sqlalchemy
from psycopg2 import errorcodes as pg_errorcodes
from sqlalchemy import (
    exc as sa_exc,
)

# Project-level imports
from silenus import config
from silenus import (
    database_repo_factory as db_repos
)
from silenus.api import errors
from ecsminion import ECSMinion, ECSMinionException


LOG = logging.getLogger(__name__)


def load_config(config_path):
    """
    Load and parse YAML file.
    """
    config.register_defaults()
    config.load_config_from_file(config_path)

    return config.get_config()


def find_bucket_owner(app_config, bucket_name):
    """"
    Lookup the owner of an bucket in ECS if it exists

    Returns the string name of the owner or None if not found or
    an error occurs
    """
    if not bucket_name:
        return None

    try:
        app_settings = app_config['flask']['SILENUS']['vipr_api']
        namespace = app_config['flask']['SILENUS']['fixed_namespace']

        ecs_minion = ECSMinion(username=app_settings['username'],
                               password=app_settings['password'],
                               token_endpoint=app_settings['token_endpoint'],
                               ecs_endpoint=app_settings['ecs_endpoint'],
                               request_timeout=app_settings['request_timeout'])

        json_bucket_metadata = ecs_minion.bucket.get_bucket_info(
            bucket_name=bucket_name,
            namespace=namespace
        )

        if json_bucket_metadata:
            return json_bucket_metadata['owner']

    except ECSMinionException as ecsminion_ex:
        LOG.error('ECS API Message: {0} Status Code: {1}'.format(
            ecsminion_ex.ecs_message, ecsminion_ex.http_status_code)
        )
    except Exception as ex:
        LOG.error(ex.message)

    return None


def retrieve_info_buckets_with_missing_owners(db_repo, hours):
    """
    Query to find existing info buckets with DEFAULT_NO_OWNER
    """
    missing_buckets = db_repo['bucket_stats_info'].missing_owner_query(hours)
    return missing_buckets


def check_and_insert_object_user(db_repo, bucket_owner, bucket_name):
    # Check if we need to insert a new user
    object_user = retrieve_object_user(db_repo, bucket_owner)
    if not object_user:
        tenant_admin_id = retrieve_tenant_admin_id(db_repo,
                                                   bucket_owner, bucket_name)
        # Object user has never been created before
        if tenant_admin_id:
            object_user = db_repo['object_user'].insert_record(
                user_name=bucket_owner,
                tenant_admin=tenant_admin_id
            )
        else:
            LOG.warn('Unable to retrieve tenant admin in order to insert '
                     'bucket_owner:{0}, bucket_name: '
                     '{1}'.format(bucket_owner, bucket_name))

    return object_user


def insert_owner_association(db_repo, bucket_owner, bucket_name):
    object_user = check_and_insert_object_user(db_repo, bucket_owner,
                                               bucket_name)
    if not object_user:
        return

    inserted_record = None

    try:
        inserted_record = db_repo['bucket_owner'].insert_record(
            object_user_name=bucket_owner,
            bucket_name=bucket_name,
        )

    except sa_exc.IntegrityError as exc:
        _handle_integrity_exception(exc)

    if inserted_record:
        db_repo['object_user'].increment_bucket_count(
            inserted_record.object_user_name)

        LOG.debug('Inserted owner association:{0}, bucket_name:{1}'
                  'to object_user_bucket_owner'
                  .format(inserted_record.object_user_name,
                          inserted_record.bucket_name,
                          inserted_record.bucket_location,
                          inserted_record.bucket_location_owner))
    return inserted_record

def retrieve_object_user(db_repo, bucket_owner):
    object_user = db_repo['object_user'].retrieve_record(
        user_name=bucket_owner)
    return object_user


def retrieve_tenant_admin_id(db_repo, bucket_owner, bucket_name):
    model = db_repo['bucket_stats_info'].get_model()
    info_record = db_repo['bucket_stats_info'].retrieve_record(
        bucket_owner=bucket_owner, bucket_name=bucket_name)
    tenant_admin_id = None
    if info_record:
        tenant_admin_id = model.tenant_admin_id
    return tenant_admin_id


def _handle_integrity_exception(exc):
    # Handle duplicate value exceptions separately, so that a
    # 409 CONFLICT can be returned.
    if exc.orig.pgcode == pg_errorcodes.UNIQUE_VIOLATION:
        LOG.warn(
            'The bucket ownership relation already exists'
        )

    else:
        LOG.warn(
            'Error inserting association: {0}'.format(exc.message)
        )


def update_info_details(db_repo, bucket_name, bucket_owner):
    LOG.debug('Updating bucket_stats_info with bucket {0}, owner {1}'
              .format(bucket_name, bucket_owner))
    model = db_repo['bucket_stats_info'].get_model()
    try:
        db_repo['bucket_stats_info'].update_record(
            attributes={
                'bucket_owner': bucket_owner,
            },
            constraints=[
                model.bucket_name == bucket_name
            ]
        )
    # pylint: disable=W0703
    except Exception as ex:
        # No matter the error we want to log it
        LOG.error(
            'Error updating bucket_stats_info: {0}'.format(ex.message)
        )


def update_hourly_details(db_repo, bucket_name, bucket_owner):
    LOG.debug('Updating bucket_stats_hourly with bucket {0}, owner {1}'
              .format(bucket_name, bucket_owner))
    model = db_repo['bucket_stats_hourly'].get_model()
    try:
        db_repo['bucket_stats_hourly'].update_record(
            attributes={
                'bucket_owner': bucket_owner,
            },
            constraints=[
                model.bucket_name == bucket_name
            ]
        )
    # pylint: disable=W0703
    except Exception as ex:
        # No matter the error we want to log it
        LOG.error(
            'Error updating bucket_stats_hourly: {0}'.format(ex.message)
        )


def process(db_repo, app_config, hours):
    missing_buckets = ['testbucket-3dcfac67-dd4c-404f-82ab-235587417228'] #retrieve_info_buckets_with_missing_owners(db_repo, hours)
    if not missing_buckets:
        return
    LOG.info('Buckets no owners: {0}'.format(missing_buckets))

    buckets_to_be_added = {}
    for bucket_name in missing_buckets:
        LOG.debug('Querying ecs for bucket: ' + str(bucket_name))
        found_bucket_owner = find_bucket_owner(app_config, bucket_name)
        if found_bucket_owner:
            buckets_to_be_added[bucket_name] = found_bucket_owner

    LOG.info('These buckets and owners were found in ecs: ')
    for bucket_name, bucket_owner in buckets_to_be_added.items():
        LOG.info('bucket_name: {0} '
                 'bucket_owner: {1}'.format(bucket_name, bucket_owner))
    LOG.info('About to update silenus with the correct owners: ')

    for bucket_name, bucket_owner in buckets_to_be_added.items():
        """
        For records which exist in ecs, but have the wrong owner in silenus:
            1. Insert the owner record to object_user_bucket_owner
            2. Update bucket_stats_info with the correct owner
            3. Update bucket_stats_hourly with the correct owner
        """
        inserted = insert_owner_association(db_repo, bucket_owner, bucket_name)
        if inserted:
            update_info_details(db_repo, bucket_owner, bucket_name)
            update_hourly_details(db_repo, bucket_owner, bucket_name)


def main():
    # Exit if another version of this script is already running
    app_instance = singleton.SingleInstance()

    # Parse command line options and load config
    arguments = docopt.docopt(__doc__, version='Gouda Reconcile 1.0')
    app_config = load_config(arguments['--conf'])
    app_settings = app_config['reconcile']
    ecs_app_settings = app_config['flask']

    # Logging settings
    log_level = app_settings['logging']['log_level']
    log_file = app_settings['logging']['log_file']

    # If verbose is requested, switch log level to debug
    if arguments['--verbose']:
        log_level = logging.DEBUG

    config.configure_logger(LOG, log_level, log_file)

    # Create SQLAlchemy session
    engine = sqlalchemy.create_engine(
        app_config['flask']['SQLALCHEMY_DATABASE_URI'],
        pool_recycle=app_config['flask']['SQLALCHEMY_POOL_RECYCLE']
    )

    scoped_session = sqlalchemy.orm.scoped_session(
        sqlalchemy.orm.sessionmaker(bind=engine)
    )
    session = scoped_session()

    repo_factory = db_repos.DatabaseRepoFactory(session)
    db_repo = {
        'bucket_stats_info': repo_factory.get_repo('bucket_stats_info'),
        'bucket_stats_hourly': repo_factory.get_repo('bucket_stats_hourly'),
        'object_user': repo_factory.get_repo('object_user'),
        'bucket_owner': repo_factory.get_repo('bucket_owner')
    }

    LOG.info("Lock file located at: {0}".format(app_instance.lockfile))

    start = arguments['--start']
    if not start:
        # Default to 1 day in the past
        start = 24

    LOG.info("Starting reconciliation of buckets in ecs")
    process(db_repo, app_config, start)
    LOG.info("Reconciliation of buckets in ecs has completed")


if __name__ == "__main__":
    main()
