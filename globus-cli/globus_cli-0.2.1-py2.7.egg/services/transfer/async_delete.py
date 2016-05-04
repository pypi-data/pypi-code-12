from __future__ import print_function
import click

from globus_sdk import DeleteData


from globus_cli.helpers import (
    common_options, outformat_is_json, print_json_response)
from globus_cli.services.transfer.helpers import get_client
from globus_cli.services.transfer.activation import autoactivate


@click.command('async-delete', short_help='Submit a Delete Task',
               help=('Delete a file or directory from one Endpoint as an '
                     'asynchronous task.'))
@common_options
@click.option('--endpoint-id', required=True,
              help='ID of the Endpoint from which to delete file(s)')
@click.option('--path', required=True, help='Path to the file/dir to delete')
@click.option('--recursive', is_flag=True, help='Recursively delete dirs')
@click.option('--ignore-missing', is_flag=True,
              help="Don't throw errors if the file or dir is absent")
def async_delete_command(ignore_missing, recursive, path, endpoint_id):
    """
    Executor for `globus transfer submit-delete`
    """
    client = get_client()
    autoactivate(client, endpoint_id, if_expires_in=60)

    delete_data = DeleteData(client, endpoint_id,
                             label='globus-cli delete',
                             recursive=recursive,
                             ignore_missing=ignore_missing)
    delete_data.add_item(path)

    res = client.submit_delete(delete_data)

    if outformat_is_json():
        print_json_response(res)
    else:
        print(res['message'])
