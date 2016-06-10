#!/usr/bin/python
import os
import re
import termcolor as tc
from . import util
import termcolor
from .date import DateParser
from wunderlist import Wunderlist
import json


class GiTo:
    def __init__(self):
        self.TODO = "TODO:"
        self.RE_AFTER_TODO = "TODO\:(.*)"
        self._path = os.getcwd()
        self._dir_name = self._path.split(os.sep).pop()
        self.all_todos = {}

    def _get_todo(self, line):
        if self.TODO in line:
            todo = re.search(self.RE_AFTER_TODO, line).group(1)
            if todo.strip():
                d_parser = DateParser(line)
                due_message = d_parser.parse()
                date = d_parser.get_date().isoformat() if d_parser.get_date() is not None else None
                return {'todo': todo,
                        'due': due_message if due_message != None else '',
                        'date': date}

    def _get_all_todos(self):
        for path, dirs, files in os.walk(self._path):
            for f_name in files:
                todos = []
                f_path = path + '/' + f_name
                if util.istext(f_path):
                    f_object = open(f_path, 'r')
                    for line in f_object.readlines():
                        todo = self._get_todo(line)
                        if todo is not None:
                            todos.append(todo)
                    f_object.close()
                    if todos:
                        self.all_todos[f_path] = todos

    def print_todo(self):
        self._get_all_todos()
        if self.all_todos:
            print tc.colored('TODO`s:\n', attrs=['bold', 'underline'])
            for label in self.all_todos:
                print tc.colored(label, attrs=['bold'])
                for item in enumerate(self.all_todos[label]):
                    print "\t", str(item[0] + 1) + '.' + ' ' + item[1]['due'] + \
                                item[1]['todo'].capitalize()
                print "\n"

    def upload_todos(self):
        self._get_all_todos()
        if self.all_todos:
            wl_ob = Wunderlist()
            if wl_ob.list_exists(self._dir_name):
                print termcolor.colored(
                    "[WARNING]",
                    "yellow"), " - List name(%s) exists." % self._dir_name
                print termcolor.colored("[WARNING]",
                                        "yellow"), " - Renaming to %s_" % self._dir_name
                response = wl_ob.create_list(self._dir_name + "_")
                list_id = json.loads(response.text)['id']
            else:
                response = wl_ob.create_list(self._dir_name)
                list_id = json.loads(response.text)['id']
            for label in self.all_todos:
                for item in enumerate(self.all_todos[label]):
                    print "Syncing task - " + item[1]['todo']
                    resp = wl_ob.create_task(list_id, item[1]['todo'], item[1]['date'])
                    if resp:
                        print termcolor.colored("[DONE]", "green")
