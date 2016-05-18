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

    s3_bucket = helper.add_s3_prefix(s3_website_config.s3_bucket)
    s3_endpoint = s3_website_config.s3_endpoint
    public = s3_website_config.public
    index_file = s3_website_config.index_file
    error_file = s3_website_config.error_file

    if make_bucket:
        logger.info("Creating bucket '%s'" % s3_bucket)
        create_bucket = ['mb', s3_bucket, ]
        result = command_runner.run(logger=logger,
                                    command=create_bucket,
                                    operation=ACTION,
                                    s3cmd_config_path=s3_cmd_config,
                                    access_key=access_key,
                                    secret_key=secret_key,
                                    region=s3_endpoint,
                                    )
        if result != 0:
            return result
    else:
        logger.debug("Skipping creation of bucket '%s'" % s3_bucket)

    logger.info("Creating website '%s'" % s3_bucket)
    command = ['ws-create', ]

    command.extend(['--ws-index=%s' % index_file], )
    command.extend(['--ws-error=%s' % error_file], )

    if public or public is None:
        command.extend(['--acl-public'], )
    else:
        command.extend(['--acl-private'], )

    command.extend([s3_bucket])
    return command_runner.run(logger=logger,
                              command=command,
                              operation=ACTION,
                              s3cmd_config_path=s3_cmd_config,
                              access_key=access_key,
                              secret_key=secret_key,
                              region=s3_endpoint,
                              )
