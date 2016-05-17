import logging
import log
import helper
import command_runner


REQUIRED_ATTRIBUTES = ['s3_bucket', 's3_endpoint', ]
ACTION = 'website creation'


def set_command_line_options(subparsers):
    """
    Command line options for s3 website creation

    :param subparsers: argparse - The parser object
    """

    parser = subparsers.add_parser('create',
                                   description='Create an s3 website',
                                   add_help=False,
                                   )

    parser.add_argument('-m', '--make_bucket',
                        action='store_true',
                        default=False,
                        help='Create the website bucket in s3',
                        required=False,
                        )

    parser.add_argument('-P', '--acl_public',
                        action='store_true',
                        help='Make the website public',
                        default=False,
                        required=False,
                        )

    parser.add_argument('--index_file',
                        action='store',
                        default='index.html',
                        help='The index file used by the website '
                             'Default: %(default)s',
                        )

    parser.add_argument('--error_file',
                        action='store',
                        default='404.html',
                        help='The error file used by the website '
                             'Default: %(default)s',
                        )

    parser.set_defaults(func=main)


@helper.required_configuration(REQUIRED_ATTRIBUTES)
def main(**kwargs):
    """
    Create an s3 website and required bucket if specified

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

    make_bucket = args.make_bucket
    index_file = args.index_file
    error_file = args.error_file
    acl_public = args.acl_public

    s3_bucket = helper.add_s3_prefix(s3_website_config.s3_bucket)
    s3_endpoint = s3_website_config.s3_endpoint

    if make_bucket:
        logger.info("Creating bucket '%s'" % s3_bucket)
        create_bucket = [helper.s3cmd_path(), 'mb', s3_bucket, ]
        result = command_runner.run(logger, create_bucket, ACTION,
                                    s3_cmd_config, access_key, secret_key,
                                    s3_endpoint, )
        if result != 0:
            return result
    else:
        logger.debug("Skipping creation of bucket '%s'" % s3_bucket)

    logger.info("Creating website '%s'" % s3_bucket)
    command = [helper.s3cmd_path(), 'ws-create', ]

    command.extend(['--ws-index=%s' % index_file], )
    command.extend(['--ws-error=%s' % error_file], )

    if acl_public:
        logger.debug("Website will be public")
        command.extend(['--acl-public'], )

    command.extend([s3_bucket])
    return command_runner.run(logger, command, ACTION, s3_cmd_config,
                              access_key, secret_key, s3_endpoint, )
