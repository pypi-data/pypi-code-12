from __future__ import print_function
import click

from globus_cli.helpers import (
    common_options, outformat_is_json, print_table)
from globus_cli.services.transfer.helpers import (
    print_json_from_iterator, get_client)


@click.command('list', help='List Bookmarks for the current user')
@common_options
def bookmark_list():
    """
    Executor for `globus transfer bookmark list`
    """
    client = get_client()

    bookmark_iterator = client.bookmark_list()

    if outformat_is_json():
        print_json_from_iterator(bookmark_iterator)
    else:
        print_table(bookmark_iterator, [
            ('Name', 'name'), ('Endpoint ID', 'endpoint_id'),
            ('Bookmark ID', 'id'), ('Path', 'path')])
