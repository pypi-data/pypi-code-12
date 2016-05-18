import argparse
import sys
from os.path import expanduser

from s3_website import cfcreate
from s3_website import cfdelete
from s3_website import cfupdate
from s3_website import create
from s3_website import delete
from s3_website import exitcodes
from s3_website import helper
from s3_website import information
from s3_website import log
from s3_website import update
from s3_website import version
from s3_website.S3WebsiteConfig import S3WebsiteConfig


def global_options(parser):
    """
    Setting up the global arguments

    :param parser: argprase - Top level argparser to add the arguments to
    """

    parser.add_argument('-c', '--s3_cmd_config',
                        action='store',
                        default='%s/.s3cfg' % expanduser("~"),
                        help='The location of the s3 cmd config file.'
                             ' Default: %(default)s',
                        )

    parser.add_argument('-s', '--s3_website_config',
                        action='store',
                        default='.s3_website_cfg.yml',
                        help='The location of the s3 website config file.'
                             ' Default: %(default)s',
                        )

    parser.add_argument('--access_key',
                        action='store',
                        default=None,
                        help='Override the AWS access key used to override the'
                             ' configuration files.'
                             ' Default: %(default)s',
                        )

    parser.add_argument('--secret_key',
                        action='store',
                        default=None,
                        help='Override the AWS secret key used to override the'
                             ' configuration files.'
                             ' Default: %(default)s',
                        )

    parser.add_argument('-L', '--log_level',
                        default='info',
                        help='Log level for script. Default: %(default)s',
                        )


def main():
    """
    Main driver for the s3_cmd_website
    """
    parser = argparse.ArgumentParser(description='Manage a s3 website and'
                                                 ' CloudFront distribution via'
                                                 ' the s3cmd',
                                     )

    subparsers = parser.add_subparsers(title='s3_cmd_website actions',
                                       description='Actions that can be'
                                                   ' performed to the website',
                                       )

    global_options(parser)

    create.set_command_line_options(subparsers)
    cfcreate.set_command_line_options(subparsers)
    cfdelete.set_command_line_options(subparsers)
    cfupdate.set_command_line_options(subparsers)
    delete.set_command_line_options(subparsers)
    update.set_command_line_options(subparsers)
    information.set_command_line_options(subparsers)
    version.set_command_line_options(subparsers)

    args = parser.parse_args()

    logger = log.setup_logger(args.log_level)

    s3_cmd_config = args.s3_cmd_config
    s3_website_config = args.s3_website_config

    if not args.func.__name__ == 'version':

        if not helper.file_exists(s3_cmd_config):
            logger.error("s3cmd config file not found at '%s'"
                         % s3_cmd_config)
            sys.exit(exitcodes.EX_CONFIG_FILE_NOT_FOUND)

    s3_website_config = S3WebsiteConfig.load_configuration(s3_website_config,
                                                           logger)

    if not s3_website_config:
        sys.exit(exitcodes.EX_CONFIG_FILE_NOT_FOUND)

    exit_code = args.func(args=args, s3_website_config=s3_website_config)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
