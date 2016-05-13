"""
TODO:
1. Monitor change of files in path
2. Upload change to github
"""
import logging

import click as click
from bb8.script.mon import mon_and_run
from bb8.script.sync import sync_files
from bb8.script.up import cmd_up


@click.group(context_settings=dict(help_option_names=['-h', '--help']))
def cli():
    pass


cli.add_command(sync_files)
cli.add_command(mon_and_run)
cli.add_command(cmd_up)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    cli()
