#
# Canopy product code
#
# (C) Copyright 2013-2015 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#
import json
import os

import click
from tabulate import tabulate

from hatcher.core.utils import NameVersionPairSorter
from ..repository_actions import runtimes
from ..utils import (
    pass_repository, HTTPErrorHandlingUploadCommand,
    upload_context_table
)


@runtimes.command('list', api_version=1)
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@pass_repository
def list_runtimes_v1(repository, platform):
    """List all runtimes in a repository.
    """
    sort_key = lambda runtime: NameVersionPairSorter(*runtime)
    runtimes = sorted(
        repository.platform(platform).list_runtimes(),
        key=sort_key)
    headers = ['Runtime', 'Version']
    click.echo(tabulate(runtimes, headers=headers))


@runtimes.command('upload', help='Upload a single runtime to a repository.',
                  cls=HTTPErrorHandlingUploadCommand, api_version=1)
@click.argument('organization')
@click.argument('repository')
@click.argument('filename')
@click.option('--force', default=False, is_flag=True)
@click.option('--verify/--no-verify', default=False)
@click.pass_context
def upload_runtime_v1(ctx, organization, repository, filename, force, verify):
    repo = ctx.obj.organization(organization).repository(repository)
    context = upload_context_table(ctx, 'Runtime', filename, repo)
    click.echo(tabulate(context, tablefmt='plain'))
    repo.upload_runtime(filename, overwrite=force, verify=verify)


@runtimes.command('download', api_version=1)
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@click.argument('implementation')
@click.argument('version')
@click.argument('destination', required=False)
@pass_repository
def download_runtime_v1(repository, platform, implementation, version,
                        destination=None):
    """Download a runtime archive.
    """

    if destination is None:
        destination = os.getcwd()

    length, iterator = repository.platform(platform).iter_download_runtime(
        implementation, version, destination)

    with click.progressbar(length=length) as bar:
        for chunk_size in iterator:
            bar.update(chunk_size)


@runtimes.command('metadata', help='Get the metadata for a single runtime.',
                  api_version=1)
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@click.argument('implementation')
@click.argument('version')
@pass_repository
def runtime_metadata_v1(repository, platform, implementation, version):
    metadata = repository.platform(platform).runtime_metadata(
        implementation, version)
    click.echo(json.dumps(metadata, sort_keys=True, indent=2))
