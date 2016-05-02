from __future__ import print_function
import click

from globus_cli.helpers import (
    common_options, outformat_is_json, print_json_response)
from globus_cli.services.transfer.helpers import get_client


@click.command('delete', help='Delete a Bookmark')
@common_options
@click.option('--bookmark-id', required=True, help='ID of the Bookmark')
def bookmark_delete(bookmark_id):
    """
    Executor for `globus transfer bookmark delete`
    """
    client = get_client()

    res = client.delete_bookmark(bookmark_id)

    if outformat_is_json():
        print_json_response(res)
    else:
        print(res['message'])
