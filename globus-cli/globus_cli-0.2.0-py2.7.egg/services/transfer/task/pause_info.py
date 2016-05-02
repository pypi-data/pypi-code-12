from __future__ import print_function
import click

from globus_cli.helpers import common_options, print_json_response
from globus_cli.services.transfer.helpers import get_client
from globus_cli.services.transfer.task.helpers import task_id_option


@click.command('pause-info',
               help=('Show detailed info about pause rules that '
                     'are applied to a Task'))
@common_options
@task_id_option()
def task_pause_info(task_id):
    """
    Executor for `globus transfer task pause-info`
    """
    client = get_client()

    res = client.task_pause_info(task_id)

    print_json_response(res)
