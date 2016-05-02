from __future__ import print_function
import click
import sys
import time

from globus_cli.helpers import common_options
from globus_cli.services.transfer.helpers import get_client
from globus_cli.services.transfer.task.helpers import task_id_option


@click.command('wait', help='Wait for a Task to complete')
@common_options
@task_id_option(help='ID of the Task to wait on')
@click.option('--timeout', type=int, metavar='N',
              help=('Wait N seconds. If the Task does not terminate by '
                    'then, exit with status 0'))
@click.option('--polling-interval', default=1, type=float, show_default=True,
              help=('Number of seconds between Task status checks. '
                    'Can be a fraction of a second in decimal notation'))
@click.option('--heartbeat', '-H', is_flag=True,
              help=('Every polling interval, print "." to stdout to '
                    'indicate that task wait is till active'))
def task_wait(heartbeat, polling_interval, timeout, task_id):
    """
    Executor for `globus transfer task wait`
    """
    client = get_client()

    def timed_out(waited_time):
        if timeout is None:
            return False
        else:
            return waited_time >= timeout

    waited_time = 0
    while not timed_out(waited_time):
        if heartbeat:
            print('.', end='')
            sys.stdout.flush()

        task = client.get_task(task_id)

        status = task['status']
        if status != 'ACTIVE':
            if heartbeat:
                print()
            sys.exit(1)

        waited_time += polling_interval
        time.sleep(polling_interval)

    # add a trailing newline to heartbeats
    if heartbeat:
        print()
