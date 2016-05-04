from __future__ import print_function
import click

from globus_cli.helpers.param_types import CaseInsensitiveChoice
from globus_cli.version import __version__


# Format Enum for output formatting
# could use a namedtuple, but that's overkill
JSON_FORMAT = 'json'
TEXT_FORMAT = 'text'


def outformat_is_json():
    """
    Only safe to call within a click context.
    """
    ctx = click.get_current_context()
    return ctx.obj['format'] == JSON_FORMAT


def outformat_is_text():
    """
    Only safe to call within a click context.
    """
    ctx = click.get_current_context()
    return ctx.obj['format'] == TEXT_FORMAT


def common_options(f):
    f = click.version_option(__version__)(f)
    f = click.help_option('-h', '--help')(f)

    def format_callback(ctx, param, value):
        ctx.obj['format'] = value or ctx.obj.get('format')

        return ctx.obj['format']

    f = click.option('-F', '--format',
                     type=CaseInsensitiveChoice([JSON_FORMAT, TEXT_FORMAT]),
                     help=('Output format for stdout. Defaults to text'),
                     expose_value=False,
                     callback=format_callback)(f)

    return f
