from ubackup import settings
from ubackup import log
from ubackup.utils import merge_settings
from ubackup.bucket import BUCKETS
from ubackup.manager import Manager
from ubackup.cli import actions
from ubackup.cli.utils import dropbox_token_flow
import click

import logging
logger = logging.getLogger(__name__)


@click.group(cls=actions.Actions)
@click.version_option(settings.VERSION)
@click.pass_context
@click.option(
    '--settings-path',
    help='Path to your settings which will be merged with the app settings.')
@click.option(
    '--bucket',
    help='The bucket you want to use.',
    type=click.Choice(BUCKETS.keys()),
    required=True)
@click.option(
    '--log-level',
    help='The log level you want to capture.',
    type=click.Choice(log.level_names()),
    default='INFO')
def cli(ctx, settings_path, bucket, log_level):
    # Merge settings and init logging
    merge_settings(settings_path)
    log.set_level(log_level)

    ctx.obj['bucket'] = bucket
    ctx.obj['manager'] = Manager(BUCKETS[bucket]())


@cli.command()
@click.pass_context
def configure(ctx):
    if ctx.obj['bucket'] == 'dropbox':
        dropbox_token_flow()
    else:
        click.echo('nothing to configure')

# -----


def main():
    log.set_config(settings.LOGGING)
    try:
        cli(obj={})
    except Exception as e:
        logger.error(e, exc_info=True)
