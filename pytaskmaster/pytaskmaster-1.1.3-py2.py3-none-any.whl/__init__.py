"""PyTaskmaster -- python library for create build scripts."""
# -*- coding: utf-8 -*-

import time
import subprocess
import json
import os
import sys
import collections

from string import Template

from . import version

def generator(in_file_name, out_file_name, config):
    sys.stdout.write(
        "Generate '{}' to '{}'...".format(in_file_name, out_file_name)
    )
    template_string = ""
    with open(in_file_name, 'r') as in_file:
        template_string = in_file.read()
    template = Template(template_string)
    template = template.safe_substitute(config.get_dict())
    out_file_content = ""
    if os.path.isfile(out_file_name):
        with open(out_file_name, 'r') as out_file_read:
            out_file_content = out_file_read.read()
    if out_file_content != template:
        with open(out_file_name, 'w') as out_file:
            out_file.write(template)
        print(" DONE")
    else:
        print(" SKIP")


class Config:
    def __init__(self, name="master.json"):
        self._name = name
        self._config = dict()

    def set(self, key, value):
        self._config[key] = value

    def get(self, key, default=""):
        if key in self._config:
            return self._config[key]
        else:
            return default

    def set_default(self, key, value):
        if key not in self._config:
            self._config[key] = value

    def load(self):
        if os.path.isfile(self._name):
            with open(self._name, 'r') as configfile:
                self._config.update(json.load(configfile))
            return True
        return False

    def save(self):
        with open(self._name, 'w') as configfile:
            json.dump(self._config, configfile, indent=4)

    def get_dict(self):
        return self._config.copy()


def shell(command, ignore_code=False):
    print("Run: `{}`".format(command))
    code = subprocess.call(command, shell=True)
    if code and not ignore_code:
        exit(code)
    return code

def show_tasks(module):
    print("Tasks:")
    for key in collections.OrderedDict(sorted(module.items())):
        task = key.split("_", 1)
        if "task" in task and len(task) > 1:
            help_info = "  {}".format(task[1])
            if module[key].__doc__:
                help_info = "{}\t-- {}".format(help_info, module[key].__doc__)
            print(help_info)


def run_task(module, name, args=None):
    if args is None:
        args = []
    task_name = "task_{}".format(name)
    if task_name in module:
        module[task_name](args)
    else:
        return False
    return True


def bench(function):
    def bench_wrapper(*args, **kwargs):
        time_began = time.time()
        result = function(*args, **kwargs)
        time_finish = time.time()
        print('Done {}: {:F} sec'.format(function.__name__, float(time_finish-time_began)))
        return result
    bench_wrapper.__doc__ = function.__doc__
    return bench_wrapper
