import logging
import command_runner

import helper
import log
import exitcodes


REQUIRED_ATTRIBUTES = ['site', 's3_bucket', 's3_endpoint', ]
ACTION = 'website update'


def set_command_line_options(subparsers):
    """
    Command line options for s3 website updates

    :param subparsers: argparse - The parser object
    """

    parser = subparsers.add_parser('update',
                                   description='Update the contents of an'
                                               ' existing s3 website',
                                   add_help=False,
                                   )

    meg = parser.add_mutually_exclusive_group()

    meg.add_argument('--sync_only',
                     action='store_true',
                     help='Only perform a sync of files, do not modify the'
                          ' metadata of existing or unchanged file',
                     required=False,
                     default=False,
                     )

    meg.add_argument('--metadata_only',
                     action='store_true',
                     help='Only perform a metadata update of existing files'
                          ' and do not sync new or updated files',
                     required=False,
                     default=False,
                     )

    parser.set_defaults(func=main)


@helper.required_configuration(REQUIRED_ATTRIBUTES)
def main(**kwargs):
    """
    Update an existing s3 website

    :param **kwargs -
      s3_website_config: dict - Configuration for the website creation
    """

    logger = logging.getLogger(log.ROOT_LOGGER_NAME)
    logger.debug('Executing %s' % ACTION)

    args = kwargs['args']
    s3_cmd_config = args.s3_cmd_config
    access_key = args.access_key
    secret_key = args.secret_key

    sync_only = args.sync_only
    metadata_only = args.metadata_only

    s3_website_config = kwargs['s3_website_config']

    site = s3_website_config.site
    s3_bucket = helper.add_s3_prefix(s3_website_config.s3_bucket)
    s3_endpoint = s3_website_config.s3_endpoint

    guess_mime_type = helper.get_configuration_attribute('guess_mime_type',
                                                         s3_website_config)
    public = helper.get_configuration_attribute('public',
                                                s3_website_config)

    gzip = helper.get_configuration_attribute('gzip', s3_website_config)

    maxage = helper.get_configuration_attribute('maxage', s3_website_config)

    cache_rules = helper.get_configuration_attribute('cache_rules',
                                                     s3_website_config)

    for rule in cache_rules:

        command = ['sync', ]
        modify_command = ['modify', '--recursive', ]
        options = []

        local_match = helper.get_configuration_key('match', rule, '*')

        local_exclude = helper.get_configuration_key('exclude', rule, '*')

        local_public = helper.get_configuration_key('public', rule)

        options.extend(['--exclude', local_exclude, '--include',
                        local_match], )

        age_string = '--add-header=Cache-Control:max-age'

        if 'maxage' in rule and rule['maxage']:
            maxage = helper.maxage_in_seconds(rule['maxage'])
        elif maxage:
            maxage = helper.maxage_in_seconds(maxage)

        options.extend(['%s=%s' % (age_string, maxage)])

        gzip_string = '--add-header=Content-Encoding:gzip'
        if 'gzip' in rule:
            if rule['gzip']:
                options.extend([gzip_string], )
        elif gzip:
            options.extend([gzip_string], )

        if guess_mime_type:
            options.extend(['--guess-mime-type', '--no-mime-magic'], )

        if local_public is not None:
            if local_public:
                options.extend(['--acl-public'], )
            else:
                options.extend(['--acl-private'], )
        else:
            if public or public is None:
                options.extend(['--acl-public'], )
            else:
                options.extend(['--acl-private'], )

        modify_command.extend(options)
        modify_command.append(s3_bucket)

        if not sync_only:
            result = command_runner.run(logger=logger,
                                        command=modify_command,
                                        operation=ACTION,
                                        s3cmd_config_path=s3_cmd_config,
                                        access_key=access_key,
                                        secret_key=secret_key,
                                        region=s3_endpoint,
                                        )
            if result != 0:
                return result

        if not metadata_only:
            command.extend(options)
            command.extend([site, s3_bucket], )
            result = command_runner.run(logger=logger,
                                        command=command,
                                        operation=ACTION,
                                        s3cmd_config_path=s3_cmd_config,
                                        access_key=access_key,
                                        secret_key=secret_key,
                                        region=s3_endpoint,
                                        )
            if result != 0:
                return result

    return exitcodes.EX_OK
