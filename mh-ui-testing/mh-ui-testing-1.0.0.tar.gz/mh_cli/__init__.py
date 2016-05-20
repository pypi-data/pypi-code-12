import os
import click
from mh_cli.common import ClickState, pass_state

click.disable_unicode_literals_warning = True

__version__ = '1.0.0'


@click.group()
@click.option('--working-dir', help='change to this dir before executing cmds')
@click.pass_context
def cli(ctx, working_dir):
    ctx.ensure_object(ClickState)
    if working_dir is not None:
        os.chdir(working_dir)

from gi import gi
from inbox import inbox
from rec import rec
from series import series
