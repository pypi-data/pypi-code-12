from __future__ import print_function
import click

from globus_cli.helpers import (
    common_options, outformat_is_json, print_table)
from globus_cli.services.transfer.helpers import (
    print_json_from_iterator, get_client)


@click.command('list', help='List Tasks for the current user')
@common_options
def task_list():
    """
    Executor for `globus transfer task-list`
    """
    client = get_client()

    task_iterator = client.task_list(num_results=10,
                                     filter='type:TRANSFER,DELETE')

    if outformat_is_json():
        print_json_from_iterator(task_iterator)
    else:
        print_table(task_iterator, [
            ('Task ID', 'task_id'), ('Status', 'status'), ('Type', 'type'),
            ('Source Display Name', 'source_endpoint_display_name'),
            ('Dest Display Name', 'destination_endpoint_display_name'),
            ('Label', 'label')])
