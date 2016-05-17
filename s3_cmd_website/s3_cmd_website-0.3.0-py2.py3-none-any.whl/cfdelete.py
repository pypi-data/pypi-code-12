import logging
import log
import helper
import command_runner


REQUIRED_ATTRIBUTES = ['cloudfront_distribution_id', 's3_endpoint', ]
ACTION = 'CloudFront deletion'


def set_command_line_options(subparsers):
    """
    Command line options for CloudFront distribution deletion

    :param subparsers: argparse - The parser object
    """

    parser = subparsers.add_parser('cfdelete',
                                   description='Delete the CloudFront'
                                               ' distribution for the s3'
                                               ' website',
                                   add_help=False,
                                   )

    parser.set_defaults(func=main)


@helper.required_configuration(REQUIRED_ATTRIBUTES)
def main(**kwargs):
    """
    Delete a CloudFront distribution fronting an s3 website

    :param **kwargs -
        s3_website_config: dict - Configuration for the website creation
    """

    logger = logging.getLogger(log.ROOT_LOGGER_NAME)
    logger.debug('Executing %s' % ACTION)

    s3_website_config = kwargs['s3_website_config']

    args = kwargs['args']
    s3_cmd_config = args.s3_cmd_config
    access_key = args.access_key
    secret_key = args.secret_key

    cloudfront_distribution = helper.add_cf_prefix(
        s3_website_config.cloudfront_distribution_id)

    s3_endpoint = s3_website_config.s3_endpoint

    logger.info("Deleting CloudFront distribution '%s'" %
                cloudfront_distribution)
    command = [helper.s3cmd_path(), 'cfdelete', ]

    command.extend([cloudfront_distribution])
    return command_runner.run(logger, command, ACTION, s3_cmd_config,
                              access_key, secret_key, s3_endpoint, )
