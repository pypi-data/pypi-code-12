import logging

import helper
import log
import command_runner


REQUIRED_ATTRIBUTES = ['s3_endpoint', 'cloudfront_distribution_id', ]
ACTION = 'CloudFront update'


def set_command_line_options(subparsers):
    """
    Command line options for the CloudFront distribution updates

    :param subparsers: argparse - The parser object
    """

    parser = subparsers.add_parser('cfupdate',
                                   description='Update the CloudFront'
                                               ' distribution for an existing'
                                               ' s3 website',
                                   add_help=False,
                                   )

    meg = parser.add_mutually_exclusive_group()

    meg.add_argument('--enable',
                     action='store_true',
                     help='Enable the CloudFront distribution',
                     required=False,
                     default=False,
                     )

    meg.add_argument('--disable',
                     action='store_true',
                     help='Disable the CloudFront distribution',
                     required=False,
                     default=False,
                     )

    parser.set_defaults(func=main)


@helper.required_configuration(REQUIRED_ATTRIBUTES)
def main(**kwargs):
    """
    Update an existing CloudFront distribution fronting an s3 website

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

    enable = args.enable
    disable = args.disable

    cname = helper.get_configuration_attribute('cloudfront_cname',
                                               s3_website_config)
    comment = helper.get_configuration_attribute('cloudfront_comment',
                                                 s3_website_config)
    root_object = helper.get_configuration_attribute('cloudfront_root_object',
                                                     s3_website_config)
    no_access_logging = helper.get_configuration_attribute(
        'cloudfront_no_access_logging',
        s3_website_config)

    cloudfront_distribution = helper.add_cf_prefix(
        s3_website_config.cloudfront_distribution_id)

    s3_endpoint = s3_website_config.s3_endpoint

    logger.info("Updating CloudFront distribution '%s'" %
                cloudfront_distribution)
    command = ['cfmodify', ]

    if enable:
        command.extend(['--enable'])
    if disable:
        command.extend(['--disable'])
    if cname:
        command.extend(['--cf-add-cname=%s' % cname])
    if comment:
        command.extend(['--cf-comment=%s' % comment])
    if root_object:
        command.extend(['--cf-default-root-object=%s' % root_object])
    if no_access_logging:
        command.extend(['--no-access-logging'])

    command.extend([cloudfront_distribution], )

    return command_runner.run(logger=logger,
                              command=command,
                              operation=ACTION,
                              s3cmd_config_path=s3_cmd_config,
                              access_key=access_key,
                              secret_key=secret_key,
                              region=s3_endpoint,
                              )
