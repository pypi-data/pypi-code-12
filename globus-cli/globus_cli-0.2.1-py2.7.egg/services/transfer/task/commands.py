import click

from globus_cli.helpers import common_options

from globus_cli.services.transfer.task.list import task_list
from globus_cli.services.transfer.task.show import show_task
from globus_cli.services.transfer.task.update import update_task
from globus_cli.services.transfer.task.cancel import cancel_task

from globus_cli.services.transfer.task.event_list import task_event_list
from globus_cli.services.transfer.task.pause_info import task_pause_info
from globus_cli.services.transfer.task.wait import task_wait


@click.group(name='task', help='Manage asynchronous Tasks')
@common_options
def task_command():
    pass


task_command.add_command(task_list)
task_command.add_command(show_task)
task_command.add_command(update_task)
task_command.add_command(cancel_task)
task_command.add_command(task_event_list)
task_command.add_command(task_pause_info)
task_command.add_command(task_wait)
