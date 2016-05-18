import logging
import exitcodes
import pkginfo
import helper
import log


ACTION = 'package version'


def set_command_line_options(subparsers):
    """
    Command line options for displaying the version information

    :param subparsers: argparse - The parser object
    """

    parser = subparsers.add_parser('version',
                                   description='Show %s version and exit'
                                               % pkginfo.package,
                                   add_help=False,
                                   )

    parser.set_defaults(func=main)


def main(**kwargs):
    """
    Display version information for this package

    :param **kwargs - Not used
    """

    logger = logging.getLogger(log.ROOT_LOGGER_NAME)
    logger.debug('Executing %s' % ACTION)

    helper.output(u"%s version %s" % (pkginfo.package, pkginfo.version))

    return exitcodes.EX_OK
