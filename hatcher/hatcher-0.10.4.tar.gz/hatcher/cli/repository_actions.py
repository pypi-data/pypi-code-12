#
# Canopy product code
#
# (C) Copyright 2013-2015 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#
from __future__ import absolute_import, print_function

import json
import os.path

import click
from tabulate import tabulate

from ..core.utils import (
    EggNameSorter,
    AppSorter,
)
from .main import hatcher
from .utils import (
    pass_organization, pass_repository, HTTPErrorHandlingUploadCommand,
    upload_context_table
)


@hatcher.group('repositories', api_versions=[0, 1])
def repositories():
    """Perform operations on repositories.
    """


@hatcher.group('apps', api_versions=[0, 1])
def apps():
    """Perform operations on apps.
    """


@hatcher.group('eggs', api_versions=[0, 1])
def eggs():
    """Perform operations on eggs.
    """


@hatcher.group('runtimes', api_versions=[0, 1])
def runtimes():
    """Perform operations on runtimes.
    """


@repositories.command(
    'list', api_versions=[0, 1],
    help='List all of the repositories from a given organization.')
@click.argument('organization')
@pass_organization
def list_repositories(organization):
    for repository in sorted(organization.list_repositories()):
        print(repository)


@repositories.command('create', help='Create a new repository.',
                      api_versions=[0, 1])
@click.argument('organization')
@click.argument('repository')
@click.argument('description')
@pass_organization
def create_repository(organization, repository, description):
    organization.create_repository(repository, description)


@repositories.command('delete', help='Delete a repository.',
                      api_versions=[0, 1])
@click.argument('organization')
@click.argument('repository')
@click.option('--force', default=False, is_flag=True)
@pass_repository
def delete_repository(repository, force):
    repository.delete(force=force)


@apps.command('list', api_versions=[0, 1])
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@pass_repository
def list_apps(repository, platform):
    """List all apps in a repository.
    """
    sort_key = lambda app: AppSorter(*app)
    apps = repository.platform(platform).list_apps()
    sorted_apps = sorted(apps, key=sort_key)
    headers = ['App Name', 'Version', 'Python Tag']
    click.echo(tabulate(sorted_apps, headers=headers, floatfmt='f'))


@apps.command('upload', help='Upload a single app to a repository.',
              cls=HTTPErrorHandlingUploadCommand, api_versions=[0, 1])
@click.argument('organization')
@click.argument('repository')
@click.argument('filename')
@click.option('--force', default=False, is_flag=True)
@click.pass_context
def upload_app(ctx, organization, repository, filename, force):
    repo = ctx.obj.organization(organization).repository(repository)
    context = upload_context_table(ctx, 'App', filename, repo)
    click.echo(tabulate(context, tablefmt='plain'))
    repo.upload_app(filename, overwrite=force)


@apps.command('metadata', help='Get the metadata for a single app.',
              api_versions=[0, 1])
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@click.argument('python_tag')
@click.argument('app_id')
@click.argument('version')
@pass_repository
def app_metadata(repository, platform, python_tag, app_id, version):
    metadata = repository.platform(platform).app_metadata(
        python_tag, app_id, version)
    print(json.dumps(metadata, sort_keys=True, indent=2))


@eggs.command('metadata', api_versions=[0, 1])
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@click.argument('python_tag')
@click.argument('name')
@click.argument('version')
@pass_repository
def egg_metadata(repository, platform, python_tag, name, version):
    """Get the metadata for a single egg.
    """
    metadata = repository.platform(platform).egg_metadata(
        python_tag, name, version)
    click.echo(json.dumps(metadata, sort_keys=True, indent=2))


@eggs.command('download', api_versions=[0, 1])
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@click.argument('python_tag')
@click.argument('name')
@click.argument('version')
@click.argument('destination', required=False)
@pass_repository
def download_egg(repository, platform, python_tag, name, version,
                 destination=None):
    """Download an egg.
    """
    if destination is None:
        destination = os.getcwd()

    length, iterator = repository.platform(platform).iter_download_egg(
        python_tag, name, version, destination)

    with click.progressbar(length=length) as bar:
        for chunk_size in iterator:
            bar.update(chunk_size)


@eggs.command('delete', api_versions=[0, 1])
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@click.argument('python_tag')
@click.argument('name')
@click.argument('version')
@pass_repository
def delete_egg(repository, platform, python_tag, name, version):
    """Delete an egg.
    """
    repository.platform(platform).delete_egg(python_tag, name, version)


@eggs.command('upload', help='Upload a single egg to a repository.',
              cls=HTTPErrorHandlingUploadCommand, api_versions=[0, 1])
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@click.argument('filename')
@click.option('--force', default=False, is_flag=True)
@click.option('--verify/--no-verify', default=False)
@click.pass_context
def upload_egg(ctx, organization, repository, platform, filename, force,
               verify):
    repo = ctx.obj.organization(organization).repository(repository)
    repo_plat = repo.platform(platform)
    context = upload_context_table(
        ctx, 'Egg', filename, repo, platform=platform)
    click.echo(tabulate(context, tablefmt='plain'))
    repo_plat.upload_egg(filename, overwrite=force, verify=verify)


@eggs.command('batch-upload', api_versions=[0, 1],
              cls=HTTPErrorHandlingUploadCommand)
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@click.argument('eggs', nargs=-1, type=click.Path(exists=True, dir_okay=False))
@click.option('--force', default=False, is_flag=True)
@click.option('--index/--no-index', default=True,
              help='Control automatic indexing of new eggs after upload')
@click.pass_context
def batch_upload_eggs(ctx, organization, repository, platform, eggs, force,
                      index):
    """Upload a batch of eggs.

    The upload will terminate on the first failure, and the indexing will be
    'transactionaly' in the sense that it will happen exactly once, once all
    the files have been successfully uploaded.
    """
    repo = ctx.obj.organization(organization).repository(repository)
    platform_repository = repo.platform(platform)

    egg_count = len(eggs)
    egg_count_text = '{0} egg{1} to upload'.format(
        egg_count, 's' if egg_count != 1 else '')
    context = upload_context_table(
        ctx, 'Batch egg', egg_count_text, repo, platform=platform)
    click.echo(tabulate(context, tablefmt='plain'))

    with click.progressbar(eggs) as bar:
        for filename in bar:
            try:
                platform_repository.upload_egg(
                    filename, overwrite=force, enabled=False, verify=True)
            except Exception:
                # Move to the line after the progress bar
                click.echo('', err=True)
                click.echo(
                    click.style(
                        'Error uploading {0}'.format(filename), fg='red'),
                    err=True)
                raise

    if index:
        platform_repository.reindex(eggs)


@eggs.command('update-index', api_versions=[0, 1])
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@click.argument('eggs', nargs=-1, type=click.Path(exists=True, dir_okay=False))
@pass_repository
def index_eggs(repository, platform, eggs):
    """Enable a batch of eggs and re-index the repository.
    """
    repository.platform(platform).reindex(eggs)


@eggs.command('list', help='List all eggs in a repository',
              api_versions=[0, 1])
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@click.argument('python_tag')
@pass_repository
def list_eggs(repository, platform, python_tag):
    eggs_iter = sorted(repository.platform(platform).list_eggs(python_tag),
                       key=lambda egg: EggNameSorter(egg['name'].lower()))
    eggs = [(egg['name'], egg['python_tag']) for egg in eggs_iter]
    headers = ['Egg Name', 'Python Tag']
    click.echo(tabulate(eggs, headers=headers))
