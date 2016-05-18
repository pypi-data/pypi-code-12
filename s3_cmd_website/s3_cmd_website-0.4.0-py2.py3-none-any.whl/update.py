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

        local_match = helper.get_configuration_key('match', rule, '*')

        local_exclude = helper.get_configuration_key('exclude', rule, '*')

        local_public = helper.get_configuration_key('public', rule)

        command.extend(['--exclude', local_exclude, '--include',
                        local_match], )

        age_string = '--add-header=Cache-Control:max-age'

        if 'maxage' in rule and rule['maxage']:
            maxage = helper.maxage_in_seconds(rule['maxage'])
        elif maxage:
            maxage = helper.maxage_in_seconds(maxage)

        command.extend(['%s=%s' % (age_string, maxage)])

        gzip_string = '--add-header=Content-Encoding:gzip'
        if 'gzip' in rule:
            if rule['gzip']:
                command.extend([gzip_string], )
        elif gzip:
            command.extend([gzip_string], )

        if guess_mime_type:
            command.extend(['--guess-mime-type', '--no-mime-magic'], )

        if local_public is not None:
            if local_public:
                command.extend(['--acl-public'], )
            else:
                command.extend(['--acl-private'], )
        else:
            if public or public is None:
                command.extend(['--acl-public'], )
            else:
                command.extend(['--acl-private'], )

        command.extend([site, s3_bucket])
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
