from __future__ import print_function
import click

from globus_cli.helpers import (
    common_options, outformat_is_json, print_json_response)
from globus_cli.services.transfer.helpers import get_client


@click.command('create', help='Create a Bookmark for the current user')
@common_options
@click.option('--endpoint-id', required=True,
              help='ID of the endpoint on which to add a Bookmark')
@click.option('--path', required=True,
              help='Path on the endpoint for the Bookmark')
@click.option('--name', required=True,
              help='Name for the Bookmark')
def bookmark_create(name, path, endpoint_id):
    """
    Executor for `globus transfer bookmark create`
    """
    client = get_client()

    submit_data = {
        'endpoint_id': endpoint_id,
        'path': path,
        'name': name
    }

    res = client.create_bookmark(submit_data)

    if outformat_is_json():
        print_json_response(res)
    else:
        print('Bookmark ID: {}'.format(res['id']))
