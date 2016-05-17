import logging
import command_runner
import log
import helper


REQUIRED_ATTRIBUTES = ['s3_bucket', ]
ACTION = 'website information lookup'


def set_command_line_options(subparsers):
    """
    Command line options for s3 website information display

    :param subparsers: argparse - The parser object
    """

    parser = subparsers.add_parser('information',
                                   description='Display the information of an'
                                               ' s3 website',
                                   add_help=False,
                                   )

    parser.set_defaults(func=main)


@helper.required_configuration(REQUIRED_ATTRIBUTES)
def main(**kwargs):
    """
    Display information for an an s3 website

    :param **kwargs -
        args: argparse - Arguments required for the website info
        s3_website_config: dict - Configuration for the website creation
    """

    logger = logging.getLogger(log.ROOT_LOGGER_NAME)
    logger.debug('Executing %s' % ACTION)

    args = kwargs['args']
    s3_cmd_config = args.s3_cmd_config
    access_key = args.access_key
    secret_key = args.secret_key

    s3_website_config = kwargs['s3_website_config']
    s3_bucket = helper.add_s3_prefix(s3_website_config.s3_bucket)
    s3_endpoint = s3_website_config.s3_endpoint

    logger.info("Information for website '%s'" % s3_bucket)

    command = [helper.s3cmd_path(), 'ws-info', s3_bucket, '--verbose', ]
    return command_runner.run(logger, command, ACTION, s3_cmd_config,
                              access_key, secret_key, s3_endpoint, )
