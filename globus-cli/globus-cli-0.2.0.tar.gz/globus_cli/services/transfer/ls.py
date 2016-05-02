from __future__ import print_function
import click

from globus_cli.helpers import (
    common_options, outformat_is_json, print_json_response, print_table)
from globus_cli.services.transfer.helpers import get_client, endpoint_id_option
from globus_cli.services.transfer.activation import autoactivate


@click.command('ls', help='List the contents of a directory on an Endpoint',
               short_help='List Endpoint directory contents')
@common_options
@endpoint_id_option
@click.option('--long', is_flag=True,
              help=('For text output only. Do long form output, kind '
                    'of like `ls -l`'))
@click.option('--path', default='/~/', show_default=True,
              help='Path on the remote endpoint to list.')
def ls_command(path, long, endpoint_id):
    """
    Executor for `globus transfer ls`
    """
    client = get_client()
    autoactivate(client, endpoint_id, if_expires_in=60)

    res = client.operation_ls(endpoint_id, path=path)
    if outformat_is_json():
        print_json_response(res)
    else:
        if not long:
            for item in res:
                print(item['name'])
        else:
            def max_keylen(key):
                return max(len(str(f[key])) for f in res)

            print_table(res, [('permissions', 'permissions'), ('user', 'user'),
                              ('group', 'group'), ('size', 'size'),
                              ('last_modified', 'last_modified'),
                              ('file type', 'type'), ('filename', 'name')])
