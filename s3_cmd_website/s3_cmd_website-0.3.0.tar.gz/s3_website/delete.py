import logging
import log
import helper
import command_runner


REQUIRED_ATTRIBUTES = ['s3_bucket', 's3_endpoint', ]
ACTION = 'website deletion'


def set_command_line_options(subparsers):
    """
    Command line options for s3 website deletion

    :param subparsers: argparse - The parser object
    """

    parser = subparsers.add_parser('delete',
                                   description='Delete an s3 website',
                                   add_help=False,
                                   )

    parser.add_argument('-d', '--delete_bucket',
                        action='store_true',
                        help='Delete the bucket the website existed in s3',
                        required=False,
                        )

    parser.set_defaults(func=main)


@helper.required_configuration(REQUIRED_ATTRIBUTES)
def main(**kwargs):
    """
    Delete an s3 website and bucket if specified

    :param **kwargs -
        args: argparse - Arguments required for the website info
        s3_website_config: dict - Configuration for the website creation
    """

    logger = logging.getLogger(log.ROOT_LOGGER_NAME)
    logger.debug('Executing %s' % ACTION)

    args = kwargs['args']
    s3_website_config = kwargs['s3_website_config']

    s3_cmd_config = args.s3_cmd_config
    access_key = args.access_key
    secret_key = args.secret_key

    delete_bucket = args.delete_bucket

    s3_bucket = helper.add_s3_prefix(s3_website_config.s3_bucket)

    s3_endpoint = s3_website_config.s3_endpoint

    logger.info("Deleting website '%s'" % s3_bucket)
    command = [helper.s3cmd_path(), 'ws-delete', s3_bucket, ]
    result = command_runner.run(logger, command, ACTION, s3_cmd_config,
                                access_key, secret_key, s3_endpoint, )
    if result != 0:
        return result

    if delete_bucket:
        logger.info("Removing '%s'" % s3_bucket)
        delete_bucket = [helper.s3cmd_path(), 'rb', s3_bucket, ]
        result = command_runner.run(logger, delete_bucket, ACTION,
                                    s3_cmd_config, access_key, secret_key,
                                    s3_endpoint, )

    return result
