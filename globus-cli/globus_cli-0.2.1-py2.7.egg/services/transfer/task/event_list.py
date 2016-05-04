from __future__ import print_function
import click

from globus_cli.helpers import common_options, outformat_is_json, print_table
from globus_cli.services.transfer.helpers import (
    print_json_from_iterator, get_client)
from globus_cli.services.transfer.task.helpers import task_id_option


@click.command('event-list', help='List Events for a given Task')
@common_options
@task_id_option(help='ID of the Task for which you want to list Events')
def task_event_list(task_id):
    """
    Executor for `globus transfer task-event-list`
    """
    client = get_client()

    event_iterator = client.task_event_list(task_id)

    if outformat_is_json():
        print_json_from_iterator(event_iterator)
    else:
        print_table(event_iterator, [
            ('Time', 'time'), ('Code', 'code'), ('Is Error', 'is_error'),
            ('Details', 'details')])
