#!/usr/bin/env python
"""A command line client for Google Tasks

It's done by following the tutorials in Google Developers:
https://developers.google.com/google-apps/tasks/quickstart/python.

In order to use this script, please look at the "Using scripts involve Google
App API" section of the sorno-py-scripts README (can be found in
https://github.com/hermantai/sorno-scripts/tree/master/sorno-py-scripts). The
API needed for this script is "Tasks API" with the scope
'https://www.googleapis.com/auth/tasks'.

Examples:

    To print tasks for all of your task lists:

        $ sorno_gtasks.py get_tasks

    To print task only for your task list "list1" and "list2":

        $ sorno_gtasks.py get_tasks list1 list2


    Copyright 2014 Heung Ming Tai

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import argparse
import httplib2
import logging
import os
import pprint
import re
import subprocess
import sys

from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
from oauth2client import tools

from sorno import consoleutil
from sorno import loggingutil
from sorno import stringutil

# The oauth scope needed for Google Tasks API
OAUTH_SCOPE = 'https://www.googleapis.com/auth/tasks'

# The file path that stores the access token returned by Google from oauth
# authentication
CREDENTIALS_FILE = os.path.expanduser("~/.sorno_gtasks-google-drive-api.cred")

_log = logging.getLogger()
_plain_logger = None  # will be created in main()
_plain_error_logger = None  # will be created in main()


class GoogleTasksConsoleApp(object):
    """The controller of the sorno_gtasks script"""

    # error codes
    EXIT_CODE_USER_ABORT = 2
    EXIT_CODE_USER_INPUT_ERROR = 3

    def __init__(
        self,
    ):
        self.tasks_service = None

    def auth(self, flags, use_credentials_cache=True):
        """
        Authenticates either by an existing credentials or by prompting the
        user to grant permissions. If succeeds, set self.tasks_service to the
        service client that can call tasks api. Otherwise, it aborts the
        script.

        Args:
            flags (argparse.Namespace): The flags for this script.
            use_credentials_cache (Optional[bool]): If true, uses the
                credentials stored in ``CREDENTIALS_FILE``.
        """
        # Copy your credentials from the console
        client_id = os.getenv('GOOGLE_APP_PROJECT_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_APP_PROJECT_CLIENT_SECRET')

        if not client_id:
            _log.info(
                "Please set the environment variable"
                " GOOGLE_APP_PROJECT_CLIENT_ID"
            )
            sys.exit(1)

        if not client_secret:
            _log.info(
                "Please set the environment variable"
                " GOOGLE_APP_PROJECT_CLIENT_SECRET"
            )
            sys.exit(1)

        # Run through the OAuth flow and retrieve credentials
        flow = OAuth2WebServerFlow(
            client_id,
            client_secret,
            OAUTH_SCOPE,
        )

        # Indicate we need the user to grant us permissions and give the auth
        # code or not
        need_get_code = True

        storage = Storage(CREDENTIALS_FILE)
        if os.path.exists(CREDENTIALS_FILE) and use_credentials_cache:
            credentials = storage.get()
            _log.debug("Use old credentials")
            need_get_code = False

        if need_get_code:
            credentials = tools.run_flow(flow, storage, flags)

        # Create an httplib2.Http object and authorize it with our credentials
        http = httplib2.Http()
        http = credentials.authorize(http)

        self.tasks_service = build('tasks', 'v1', http=http)

    def copy_tasks_action(self, args):
        self.auth(args, use_credentials_cache=args.use_credentials_cache)

        # ask the user to choose a task list that contains the tasks

        tasklists = self.get_tasklists()
        for index, tasklist in enumerate(tasklists, 1):
            print(
                "{0}) {1} (id: {2})".format(
                    index,
                    tasklist['title'],
                    tasklist['id'],
                )
            )

        ans = consoleutil.input(
            "Please choose the list that contains the tasks: "
        )

        intvs = consoleutil.parse_intervals(ans)
        list_number = intvs[0].start
        chosen_tasklist = tasklists[list_number - 1]

        _plain_logger.info("")
        # ask the user to choose the tasks from the chosen task list

        tasks = self.get_tasks_from_tasklist(chosen_tasklist['id'])

        _plain_logger.info(
            "Tasklist [%s] has the following tasks:",
            chosen_tasklist['title'],
        )
        self._print_tasks_with_ids(tasks)

        ans = consoleutil.input(
            "Please choose the tasks that you want to copy over: "
        )

        intvs = consoleutil.parse_intervals(ans)

        chosen_tasks = []
        for intv in intvs:
            chosen_tasks.extend(
                # the start and end in interals are one-based, so need to
                # reduce them each by 1
                tasks[intv.start - 1:intv.end]
            )

        dups = self._get_duplicated_items(chosen_tasks)
        if dups:
            _plain_logger.error(
                "The following tasks are chosen more than once:"
            )
            self._print_tasks_with_ids(dups, ref=tasks)
            return GoogleTasksConsoleApp.EXIT_CODE_USER_INPUT_ERROR

        _plain_logger.info("Chosen tasks:")
        self._print_tasks_with_ids(chosen_tasks, ref=tasks)

        _plain_logger.info("")
        # ask the user to choose the destination task list

        ans = consoleutil.input(
            "Please choose the destination task list:"
        )

        intvs = consoleutil.parse_intervals(ans)
        dest_list_number = intvs[0].start
        chosen_dest_tasklist = tasklists[dest_list_number - 1]

        if chosen_tasklist == chosen_dest_tasklist:
            _plain_error_logger.error(
                "Source and destination lists cannot be the same."
            )
            return GoogleTasksConsoleApp.EXIT_CODE_USER_INPUT_ERROR

        _plain_logger.info("")
        # ask the user to confirm
        confirm_msg = re.sub(
            r"\s+",
            " ",
            """
            Are you sure you want to copy the chosen tasks from task list
            [{0}] to task list [{1}]
            """.strip().format(
                chosen_tasklist['title'],
                chosen_dest_tasklist['title'],
            ),
        )

        if not consoleutil.confirm(confirm_msg):
            _plain_error_logger.error("Aborted")
            return GoogleTasksConsoleApp.EXIT_CODE_USER_ABORT

        # copy the tasks

        for task in chosen_tasks:
            self.insert_task(
                chosen_dest_tasklist['id'],
                task,
            )

        return 0

    def insert_task(self, tasklist_id, task):
        """Inserts a task.

        Args:
            tasklist_id (str): The tasklist that contains the task.
            task (dict): The representation of a task. See
                https://developers.google.com/google-apps/tasks/v1/reference/tasks#resource-representations.
        """
        t = task.copy()
        t.pop('id', ' ')
        self.tasks_service.tasks().insert(
            tasklist=tasklist_id,
            body=t,
        ).execute()

    def delete_task(self, tasklist_id, task_id):
        """Deletes a task.

        Args:
            tasklist_id (str): The id of the tasklist that contains the task.
            task_id (str): The id of the task inside the tasklist that is to
                be deleted.
        """
        self.tasks_service.tasks().delete(
            tasklist=tasklist_id,
            task=task_id,
        ).execute()

    def delete_tasks_action(self, args):
        self.auth(args, use_credentials_cache=args.use_credentials_cache)

        # ask the user to choose a task list that contains the tasks

        tasklists = self.get_tasklists()
        for index, tasklist in enumerate(tasklists, 1):
            print(
                "{0}) {1} (id: {2})".format(
                    index,
                    tasklist['title'],
                    tasklist['id'],
                )
            )

        ans = consoleutil.input(
            "Please choose the list that contains the tasks: "
        )

        intvs = consoleutil.parse_intervals(ans)
        list_number = intvs[0].start
        chosen_tasklist = tasklists[list_number - 1]

        _plain_logger.info("")
        # ask the user to choose the tasks from the chosen task list

        tasks = self.get_tasks_from_tasklist(chosen_tasklist['id'])

        _plain_logger.info(
            "Tasklist [%s] has the following tasks:",
            chosen_tasklist['title'],
        )
        self._print_tasks_with_ids(tasks)

        ans = consoleutil.input(
            "Please choose the tasks that you want to delete: "
        )

        intvs = consoleutil.parse_intervals(ans)

        chosen_tasks = []
        for intv in intvs:
            chosen_tasks.extend(
                # the start and end in interals are one-based, so need to
                # reduce them each by 1
                tasks[intv.start - 1:intv.end]
            )

        dups = self._get_duplicated_items(chosen_tasks)
        if dups:
            _plain_logger.error(
                "The following tasks are chosen more than once:"
            )
            self._print_tasks_with_ids(dups, ref=tasks)
            return GoogleTasksConsoleApp.EXIT_CODE_USER_INPUT_ERROR

        _plain_logger.info("Chosen tasks:")
        self._print_tasks_with_ids(chosen_tasks, ref=tasks)

        _plain_logger.info("")

        # ask the user to confirm
        confirm_msg = re.sub(
            r"\s+",
            " ",
            """
            Are you sure you want to delete the chosen tasks from task list?
            [{0}]
            """.strip().format(
                chosen_tasklist['title'],
            ),
        )

        if not consoleutil.confirm(confirm_msg):
            _plain_error_logger.error("Aborted")
            return GoogleTasksConsoleApp.EXIT_CODE_USER_ABORT

        # delete the tasks

        for task in chosen_tasks:
            self.delete_task(chosen_tasklist['id'], task['id'])

        return 0

    def _print_tasks_with_ids(self, tasks, ref=None):
        """Print tasks along with their id's.

        Args:
            tasks (sequence[task]): Tasks to be printed out.
            ref (Optional[sequence[task]]): By default, this method simply
                prints the sequence numbers of the tasks according to the
                position of the task in the given tasks (one-based). If ref is
                provided, the position of the task in ref is used instead
                (one-based). If the task cannot be found in ref, ValueError is
                thrown.

        Raises:
            ValueError: If ref is given but a task cannot be found in ref.
        """
        if ref:
            for task in tasks:
                index = ref.index(task)
                if index == -1:
                    raise ValueError(
                        "Task [{0}] cannot be found in {1}".format(
                            task,
                            ref,
                        )
                    )

                print(
                    "{0}) {1} (id: {2})".format(
                        index + 1,
                        task['title'],
                        task['id'],
                    )
                )
        else:
            for index, task in enumerate(tasks, 1):
                print(
                    "{0}) {1} (id: {2})".format(
                        index,
                        task['title'],
                        task['id'],
                    )
                )

    def _get_duplicated_items(self, items):
        seen = []
        duplicated = []
        for item in items:
            # TODO(htaihm): optimize this
            if item in seen:
                duplicated.append(item)
            else:
                seen.append(item)

        return duplicated

    def get_tasks_action(self, args):
        """Handle the subcommand get_tasks

        Print out the tasks for the task lists specified from the flags of the
        script.

        Args:
            args (argparse.Namespace): The flags of the script.
        """
        self.auth(args, use_credentials_cache=args.use_credentials_cache)

        tasklists_names = args.tasklist or []
        tasklists = self.get_tasklists()
        tasklists_to_show = []

        tasklists_map = {
            tasklist['title']: tasklist for tasklist in tasklists
        }

        if not tasklists_names:
            # assume all the task lists if no task lists are provided
            tasklists_to_show.extend(tasklists)
        else:
            for tasklist_name in tasklists_names:
                if tasklist_name not in tasklists_map:
                    _plain_error_logger.error(
                        "Task list [%s] does not exist. Avaliable task lists"
                            " are:",
                        tasklist_name,
                    )
                    for index, tasklist in enumerate(tasklists, 1):
                        if args.detail:
                            s = pprint.pformat(tasklist)
                        else:
                            s = tasklist['title']
                        _plain_logger.error("%d) %s", index, s)
                    return 1
                tasklists_to_show.append(tasklists_map[tasklist_name])

        for tasklist_to_show in tasklists_to_show:
            tasklist_id = tasklist_to_show['id']

            if args.detail:
                s = pprint.pformat(tasklist_to_show)
            else:
                s = "[%s]:" % tasklist_to_show['title']

            _plain_logger.info(
                "Tasks for the list %s",
                s,
            )
            tasks = self.get_tasks_from_tasklist(tasklist_id)
            for index, task in enumerate(tasks, 1):
                if args.detail:
                    s = pprint.pformat(task)
                else:
                    try:
                        s = stringutil.format_with_default_value(
                            lambda k: "<%s:null>" % k,
                            args.task_format,
                            task,
                        )
                    except KeyError as ex:
                        s = "KeyError: %s, task: %s" % (
                            ex,
                            pprint.pformat(task),
                        )

                if args.list_with_chars is not None:
                    _plain_logger.info("%s%s", args.list_with_chars, s)
                else:
                    _plain_logger.info("%d) %s", index, s)

                if args.show_notes:
                    _plain_logger.info("Notes: %s", task.get('notes', ""))
                elif args.show_notes_if_presence:
                    if task.get('notes'):
                        _plain_logger.info("Notes: %s", task['notes'])

        return 0


    def get_tasklists(self):
        """Retrieve the task lists of the user

        Returns:
            A list of dictionaries each represents a Tasklist resource. The
            exact representation is in
            https://developers.google.com/google-apps/tasks/v1/reference/tasklists#resource-representations
            Currently it is:

                {
                  "kind": "tasks#taskList",
                  "id": string,
                  "etag": string,
                  "title": string,
                  "updated": datetime,
                  "selfLink": string
                }
        """

        results = self.tasks_service.tasklists().list().execute()
        return results.get('items', [])

    def get_tasks_from_tasklist(self, tasklist_id):
        """Retrieves a list of tasks for a Tasklist

        Args:
            tasklist_id (string): The ID of the Tasklist.

        Returns:
            A list of dictionaries each represents a Task resource. The exact
            representation is in
            https://developers.google.com/google-apps/tasks/v1/reference/tasks#resource-representations
            Currently it is:

                {
                  "kind": "tasks#task",
                  "id": string,
                  "etag": etag,
                  "title": string,
                  "updated": datetime,
                  "selfLink": string,
                  "parent": string,
                  "position": string,
                  "notes": string,
                  "status": string,
                  "due": datetime,
                  "completed": datetime,
                  "deleted": boolean,
                  "hidden": boolean,
                  "links": [
                    {
                      "type": string,
                      "description": string,
                      "link": string
                    }
                  ]
                }
        """
        results = self.tasks_service.tasks().list(
            tasklist=tasklist_id
        ).execute()
        return results.get('items', [])


def parse_args(app_obj, cmd_args):
    description = __doc__.split("Copyright 2014")[0].strip()

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[tools.argparser],
    )
    parser.add_argument(
        "--no-credentials-cache",
        dest="use_credentials_cache",
        action="store_false",
        default=True,
        help="If specified, old credentials are not reused and you have to"
            " follow the instruction from this script to get the code every"
            " time you use this script.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
    )

    subparsers = parser.add_subparsers(
        title="Subcommands",
        description="Some description for subcommands",
    )

    get_tasks_description = """Print tasks for your task lists.

Examples:

    To print tasks for all of your task lists:

        $ sorno_gtasks.py get_tasks

    To print task only for your task list "list1" and "list2":

        $ sorno_gtasks.py get_tasks list1 list2

By default, get_tasks only prints the titles of your tasks. You can use
--show-notes option to print the notes as well. Use the --detail option to
show details.

Examples:

    To show the details for all tasks and all task lists.

        $ sorno_gtasks.py get_tasks --detail
    """

    parser_get_tasks = subparsers.add_parser(
        "get_tasks",
        help="Print your tasks",
        description=get_tasks_description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser_get_tasks.add_argument(
        "--show-notes",
        action="store_true",
        help="shows the notes for each task",
    )
    parser_get_tasks.add_argument(
        "--show-notes-if-presence",
        action="store_true",
        help="shows the notes for tasks with notes",
    )
    parser_get_tasks.add_argument(
        "--task-format",
        help="The format for printing out a task, default is '%(default)s'."
        " You can use --detail to get all the field names for tasks. If a key"
        " specified in the format is missing, it is printed with the"
        " form: <key:null>, in which the key is the actual name of the key.",
        default="{title}",
    )
    parser_get_tasks.add_argument(
        "--list-with-chars",
        help="instead of numerating the tasks, use the characters specified in"
        " this option instead"
    )
    parser_get_tasks.add_argument(
        "--detail",
        action="store_true",
        help="see the details for all tasks and task lists",
    )
    parser_get_tasks.add_argument(
        "tasklist",
        nargs="*",
        help="The tasks in which to be printed out. If not specified, "
        " assume all tasks in all task lists.",
    )
    parser_get_tasks.set_defaults(func=app_obj.get_tasks_action)

    parser_copy_tasks = subparsers.add_parser(
        "copy_tasks",
        description="Copy tasks from one task list to another."
            " Simply follow the prompt instructions to finish the action.",
        help="Copy tasks from one task list to another.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser_copy_tasks.set_defaults(func=app_obj.copy_tasks_action)

    parser_delete_tasks = subparsers.add_parser(
        "delete_tasks",
        description="Delete tasks in a task list."
            " Simply follow the prompt instructions to finish the action.",
        help="Delete tasks in a task list.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser_delete_tasks.set_defaults(func=app_obj.delete_tasks_action)

    args = parser.parse_args(cmd_args)
    return args


def main():
    global _plain_logger, _plain_error_logger

    app = GoogleTasksConsoleApp()
    args = parse_args(app, sys.argv[1:])

    loggingutil.setup_logger(_log, debug=args.debug)
    _plain_logger = loggingutil.create_plain_logger(
        "PLAIN",
        debug=args.debug,
    )
    _plain_error_logger = loggingutil.create_plain_logger(
        "PLAIN_ERROR",
        debug=args.debug,
        stdout=False,
    )
    args.func(args)


if __name__ == '__main__':
    main()
