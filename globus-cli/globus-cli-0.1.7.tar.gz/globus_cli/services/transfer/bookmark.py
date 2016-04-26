from __future__ import print_function
import sys

from globus_cli.helpers import (
    outformat_is_json, cliargs, CLIArg, print_json_response,
    colon_formatted_print, print_table)
from globus_cli.services.transfer.helpers import (
    print_json_from_iterator, get_client)


@cliargs('List Bookmarks for the current user')
def bookmark_list(args):
    """
    Executor for `globus transfer bookmark list`
    """
    client = get_client()

    bookmark_iterator = client.bookmark_list()

    if outformat_is_json(args):
        print_json_from_iterator(bookmark_iterator)
    else:
        print_table(bookmark_iterator, [
            ('Name', 'name'), ('Endpoint ID', 'endpoint_id'),
            ('Bookmark ID', 'id'), ('Path', 'path')])


def _validate_show_args(args, parser):
    if args.bookmark_id is None and args.bookmark_name is None:
        parser.error('show requires either --bookmark-id or --bookmark-name')
    elif args.bookmark_id is not None and args.bookmark_name is not None:
        parser.error('show cannot take both --bookmark-id and --bookmark-name')


@cliargs('Show a Bookmark by either name or ID',
         CLIArg('bookmark-id', help='ID of the Bookmark'),
         CLIArg('bookmark-name', help='Name of the Bookmark'),
         arg_validator=_validate_show_args)
def bookmark_show(args):
    """
    Executor for `globus transfer bookmark show`
    """
    client = get_client()

    if args.bookmark_id is not None:
        res = client.get_bookmark(args.bookmark_id)
    elif args.bookmark_name is not None:
        res = None
        for res in client.bookmark_list():
            if res['name'] == args.bookmark_name:
                break
            else:
                res = None
        if res is None:
            print('No bookmark found with name {}'.format(args.bookmark_name),
                  file=sys.stderr)
            return
    else:
        raise ValueError('Trying to lookup bookmark without ID or Name')

    if outformat_is_json(args):
        print_json_response(res)
    else:
        fields = (('ID', 'id'), ('Name', 'name'),
                  ('Endpoint ID', 'endpoint_id'), ('Path', 'path'))
        colon_formatted_print(res, fields)


@cliargs('Create a Bookmark for the current user',
         CLIArg('endpoint-id', required=True,
                help='ID of the endpoint on which to add a Bookmark'),
         CLIArg('path', required=True,
                help='Path on the endpoint for the Bookmark'),
         CLIArg('name', required=True, help='Name for the Bookmark'))
def bookmark_create(args):
    """
    Executor for `globus transfer bookmark create`
    """
    client = get_client()

    submit_data = {
        'endpoint_id': args.endpoint_id,
        'path': args.path,
        'name': args.name
    }

    res = client.create_bookmark(submit_data)

    if outformat_is_json(args):
        print_json_response(res)
    else:
        print('Bookmark ID: {}'.format(res['id']))


@cliargs('Change a Bookmark\'s name',
         CLIArg('bookmark-id', required=True, help='ID of the Bookmark'),
         CLIArg('name', required=True, help='New name for the Bookmark'))
def bookmark_rename(args):
    """
    Executor for `globus transfer bookmark rename`
    """
    client = get_client()

    submit_data = {
        'name': args.name
    }

    res = client.update_bookmark(args.bookmark_id, submit_data)

    if outformat_is_json(args):
        print_json_response(res)
    else:
        print('Success')


@cliargs('Delete a Bookmark',
         CLIArg('bookmark-id', required=True, help='ID of the Bookmark'))
def bookmark_delete(args):
    """
    Executor for `globus transfer bookmark delete`
    """
    client = get_client()

    res = client.delete_bookmark(args.bookmark_id)

    if outformat_is_json(args):
        print_json_response(res)
    else:
        print(res['message'])
