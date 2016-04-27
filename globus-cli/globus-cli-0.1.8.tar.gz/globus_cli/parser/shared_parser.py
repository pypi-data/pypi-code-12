import argparse

from globus_cli.version import __version__
from globus_cli.helpers import JSON_FORMAT, TEXT_FORMAT


def _str_to_outformat(s):
    s = s.lower()
    if s == 'json':
        return JSON_FORMAT
    elif s == 'text':
        return TEXT_FORMAT
    else:
        ValueError('Invalid Output Format Specified')


class GlobusCLISharedParser(argparse.ArgumentParser):
    """
    A base parser type from which all other command parsers inherit. Provides
    shared arguments, top level description, and other common attributes.
    """
    def __init__(self, *args, **kwargs):
        # this is marginally nicer than trying to stuff explicit kwargs
        # inbetween *args and **kwargs in the initializer invocation below
        newkwargs = {
            'prog': 'globus',
            'formatter_class': argparse.RawTextHelpFormatter
        }
        newkwargs.update(kwargs)
        argparse.ArgumentParser.__init__(self, *args, **newkwargs)

        # shared arguments

        # output format -- all commands must support these, although they
        # are free to implement the TEXT format however they see fit
        self.add_argument(
            '-F', '--format', dest='outformat',
            default=TEXT_FORMAT, choices=[JSON_FORMAT, TEXT_FORMAT],
            type=_str_to_outformat, help=('Output format for stdout. '
                                          'Defaults to TEXT'))

        # version of globus cli -- ignores all other passed arguments and
        # prints the version
        self.add_argument('--version', action='version',
                          version='%(prog)s ' + __version__,
                          help='Show Globus CLI version and exit')
