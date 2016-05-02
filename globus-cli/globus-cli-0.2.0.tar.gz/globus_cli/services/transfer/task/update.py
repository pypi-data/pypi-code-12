from __future__ import print_function
import click

from globus_cli.helpers import (
    common_options, outformat_is_json, print_json_response)
from globus_cli.services.transfer.helpers import (
    get_client, assemble_generic_doc)
from globus_cli.services.transfer.task.helpers import task_id_option


@click.command('update', short_help='Update a Task',
               help='Update label and/or deadline on an active Task')
@common_options
@task_id_option(help='ID of the Task which you want to cancel')
@click.option('--label', help='New Label for the Task')
@click.option('--deadline', help='New Deadline for the Task')
def update_task(deadline, label, task_id):
    """
    Executor for `globus transfer task update`
    """
    client = get_client()

    task_doc = assemble_generic_doc(
        'task', label=label, deadline=deadline)

    res = client.update_task(task_id, task_doc)

    if outformat_is_json():
        print_json_response(res)
    else:
        print('Success')
