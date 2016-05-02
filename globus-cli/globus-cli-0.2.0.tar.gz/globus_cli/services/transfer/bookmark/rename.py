from __future__ import print_function
import click

from globus_cli.helpers import (
    common_options, outformat_is_json, print_json_response)
from globus_cli.services.transfer.helpers import get_client


@click.command('rename', help='Change a Bookmark\'s name')
@common_options
@click.option('--bookmark-id', required=True, help='ID of the Bookmark')
@click.option('--name', required=True, help='New name for the Bookmark')
def bookmark_rename(name, bookmark_id):
    """
    Executor for `globus transfer bookmark rename`
    """
    client = get_client()

    submit_data = {
        'name': name
    }

    res = client.update_bookmark(bookmark_id, submit_data)

    if outformat_is_json():
        print_json_response(res)
    else:
        print('Success')
