from __future__ import print_function

from globus_cli.helpers import (
    outformat_is_json, cliargs, CLIArg, print_json_response,
    print_table)
from globus_cli.services.transfer.helpers import get_client
from globus_cli.services.transfer.activation import autoactivate


@cliargs('List the contents of a directory on an Endpoint',
         CLIArg('endpoint-id', required=True, help='ID of the Endpoint'),
         CLIArg('long', default=False, action='store_true',
                help=('For text output only. Do long form output, kind '
                      'of like `ls -l`')),
         CLIArg('path', default='/~/',
                help='Path on the remote endpoint to list. Defaults to "/~/"'))
def op_ls(args):
    """
    Executor for `globus transfer ls`
    """
    client = get_client()
    autoactivate(client, args.endpoint_id, if_expires_in=60)

    res = client.operation_ls(args.endpoint_id, path=args.path)
    if outformat_is_json(args):
        print_json_response(res)
    else:
        if not args.long:
            for item in res:
                print(item['name'])
        else:
            def max_keylen(key):
                return max(len(str(f[key])) for f in res)

            print_table(res, [('permissions', 'permissions'), ('user', 'user'),
                              ('group', 'group'), ('size', 'size'),
                              ('last_modified', 'last_modififed'),
                              ('file type', 'type'), ('filename', 'name')])


@cliargs('Make a directory on an Endpoint',
         CLIArg('endpoint-id', required=True, help='ID of the Endpoint'),
         CLIArg('path', required=True,
                help='Path on the remote Endpoint to create'))
def op_mkdir(args):
    """
    Executor for `globus transfer mkdir`
    """
    client = get_client()
    autoactivate(client, args.endpoint_id, if_expires_in=60)

    res = client.operation_mkdir(args.endpoint_id, path=args.path)

    if outformat_is_json(args):
        print_json_response(res)
    else:
        print(res['message'])


@cliargs('Rename a file or directory on an Endpoint',
         CLIArg('endpoint-id', required=True, help='ID of the Endpoint'),
         CLIArg('old-path', required=True,
                help='Path to the file/dir to rename'),
         CLIArg('new-path', required=True,
                help='Desired location of the file/dir after rename'))
def op_rename(args):
    """
    Executor for `globus transfer rename`
    """
    client = get_client()
    autoactivate(client, args.endpoint_id, if_expires_in=60)

    res = client.operation_rename(args.endpoint_id, oldpath=args.old_path,
                                  newpath=args.new_path)

    if outformat_is_json(args):
        print_json_response(res)
    else:
        print(res['message'])
