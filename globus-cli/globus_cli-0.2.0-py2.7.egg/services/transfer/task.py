from __future__ import print_function
import sys
import time

from globus_cli.helpers import (
    outformat_is_json, cliargs, CLIArg, print_json_response,
    print_table)
from globus_cli.services.transfer.helpers import (
    print_json_from_iterator, get_client)


@cliargs('List Tasks for the current user')
def task_list(args):
    """
    Executor for `globus transfer task-list`
    """
    client = get_client()

    task_iterator = client.task_list(num_results=10,
                                     filter='type:TRANSFER,DELETE')

    if outformat_is_json(args):
        print_json_from_iterator(task_iterator)
    else:
        print_table(task_iterator, [
            ('Task ID', 'task_id'), ('Status', 'status'), ('Type', 'type'),
            ('Source Display Name', 'source_endpoint_display_name'),
            ('Dest Display Name', 'destination_endpoint_display_name'),
            ('Label', 'label')])


@cliargs('List Events for a given Task',
         CLIArg('task-id', required=True,
                help='ID of the Task for which you want to list Events'))
def task_event_list(args):
    """
    Executor for `globus transfer task-event-list`
    """
    client = get_client()

    event_iterator = client.task_event_list(args.task_id)

    if outformat_is_json(args):
        print_json_from_iterator(event_iterator)
    else:
        print_table(event_iterator, [
            ('Time', 'time'), ('Code', 'code'), ('Is Error', 'is_error'),
            ('Details', 'details')])


@cliargs('Cancel a specific task, owned by the current user',
         CLIArg('task-id', required=True,
                help='ID of the Task which you want to cancel'))
def cancel_task(args):
    """
    Executor for `globus transfer task cancel`
    """
    client = get_client()

    res = client.cancel_task(args.task_id)

    if outformat_is_json(args):
        print_json_response(res)
    else:
        print(res['message'])


@cliargs('Update label and/or deadline on an active Task',
         CLIArg('task-id', required=True,
                help='ID of the Task which you want to cancel'),
         CLIArg('label', default=None, help='New Label for the Task'),
         CLIArg('deadline', default=None, help='New Deadline for the Task'))
def update_task(args):
    """
    Executor for `globus transfer task update`
    """
    client = get_client()

    task_doc = {
        'DATA_TYPE': 'task'
    }

    if args.label:
        task_doc['label'] = args.label
    if args.deadline:
        task_doc['deadline'] = args.deadline

    res = client.update_task(args.task_id, task_doc)

    if outformat_is_json(args):
        print_json_response(res)
    else:
        print('Success')


@cliargs('Show detailed information about a specific Task',
         CLIArg('task-id', required=True,
                help='ID of the Task which you want to examine'))
def show_task(args):
    """
    Executor for `globus transfer task show`
    """
    client = get_client()

    res = client.get_task(args.task_id)

    print_json_response(res)


@cliargs('Show detailed info about pause rules that are applied to a Task',
         CLIArg('task-id', required=True, help='ID of the Task'))
def task_pause_info(args):
    """
    Executor for `globus transfer task pause-info`
    """
    client = get_client()

    res = client.task_pause_info(args.task_id)

    print_json_response(res)


@cliargs('Wait for a Task to complete',
         CLIArg('task-id', required=True,
                help='ID of the Task to wait on'),
         CLIArg('timeout', default=None, type=int, metavar='N',
                help=('Wait N seconds. If the Task does not terminate by '
                      'then, exit with status 0')),
         CLIArg('polling-interval', default=1, type=int,
                help=('Number of seconds between Task status checks. '
                      'Defaults to 1')),
         CLIArg('heartbeat', '-H', default=False, action='store_true',
                help=('Every polling interval, print "." to stdout to '
                      'indicate that task wait is till active')))
def task_wait(args):
    """
    Executor for `globus transfer task wait`
    """
    client = get_client()

    def timed_out(waited_time):
        if args.timeout is None:
            return False
        else:
            return waited_time > args.timeout

    waited_time = 0
    while not timed_out(waited_time):
        if args.heartbeat:
            print('.', end='')

        task = client.get_task(args.task_id)

        status = task['status']
        if status != 'ACTIVE':
            if args.heartbeat:
                print()
            sys.exit(1)

        waited_time += args.polling_interval
        time.sleep(args.polling_interval)
