#!/usr/bin/env python
"""cli module."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import click
import traceback
import importlib

from . import version

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('modulename')
@click.option('--debug', default=False, help='')
@click.version_option(version.__version__, '--version')
def cli(**kwargs):
    modulename = kwargs['modulename']
    module = importlib.import_module(modulename)
    try:
        version = module.__version__
    except:
        version = ''

    click.secho("{} == ".format(modulename), nl=False)
    click.secho("{}".format(version), fg='green', bold=True)

if __name__ == '__main__':
    cli()


