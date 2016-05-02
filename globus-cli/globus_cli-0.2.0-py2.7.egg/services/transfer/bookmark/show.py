from __future__ import print_function
import click
import sys

from globus_cli.helpers import (
    common_options, outformat_is_json, print_json_response,
    colon_formatted_print)
from globus_cli.services.transfer.helpers import get_client


@click.command('show', help='Show a Bookmark by either name or ID')
@common_options
@click.option('--bookmark-id', help='ID of the Bookmark')
@click.option('--bookmark-name', help='Name of the Bookmark')
def bookmark_show(bookmark_name, bookmark_id):
    """
    Executor for `globus transfer bookmark show`
    """
    if bookmark_id is None and bookmark_name is None:
        raise click.UsageError(
            'bookmark show requires either --bookmark-id or --bookmark-name')
    elif bookmark_id is not None and bookmark_name is not None:
        raise click.UsageError(
            'bookmark show cannot take both --bookmark-id and --bookmark-name')

    client = get_client()

    if bookmark_id is not None:
        res = client.get_bookmark(bookmark_id)
    elif bookmark_name is not None:
        res = None
        for res in client.bookmark_list():
            if res['name'] == bookmark_name:
                break
            else:
                res = None
        if res is None:
            print('No bookmark found with name {}'.format(bookmark_name),
                  file=sys.stderr)
            return
    else:
        # this should be impossible, but just in case arg validation gets
        # broken someday...
        raise ValueError('Trying to lookup bookmark without ID or Name')

    if outformat_is_json():
        print_json_response(res)
    else:
        fields = (('ID', 'id'), ('Name', 'name'),
                  ('Endpoint ID', 'endpoint_id'), ('Path', 'path'))
        colon_formatted_print(res, fields)
