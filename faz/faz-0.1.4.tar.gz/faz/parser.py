# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import re
import copy
import logging


from faz.task import Task


TASK_PATTERN = r"^#[ ]*(?P<outputs>[a-zA-Z0-9, \.\$_\-\[\]\*]+)*[ ]*<-[ ]*(?P<inputs>[a-zA-Z0-9, \.\$_\-\[\]\*]+)*[ ]*[:]*[ ]*(?P<options>[a-zA-Z0-9, \.\$_\-\[\]\*]+)*"


def split_task_parameters(line):
    """ Split a string of comma separated words."""
    if line is None:
        result = []
    else:
        result = [parameter.strip() for parameter in line.split(",")]
    return result


def find_tasks(lines):
    """
    Find task lines and corresponding line numbers in a list of lines.
    """
    tasks = []
    linenumbers = []
    pattern = re.compile(TASK_PATTERN)
    for n, line in enumerate(lines):
        if "#" in line and "<-" in line:
            m = pattern.match(line)
            if m is not None:
                groupdict = m.groupdict()
                linenumbers.append(n)
                for key in groupdict:
                    groupdict[key] = split_task_parameters(groupdict[key])
                    logging.debug(
                        "{0}: {1}".format(key, ", ".join(groupdict[key])))
                tasks.append(groupdict)
    linenumbers.append(len(lines))
    return tasks, linenumbers


def create_environment(preamble):
    """
    Create a dictionary of variables obtained from the preamble of
    the task file and the environment the program is running on.
    """
    environment = copy.deepcopy(os.environ)
    for line in preamble:
        logging.debug(line)
        if "=" in line and not line.startswith("#"):
            tmp = line.split("=")
            key = tmp[0].strip()
            value = tmp[1].strip()
            logging.debug(
                "Found variable {} with value {}".format(key, value))
            environment.update({key: value})
    logging.debug("Env {}".format(environment))
    return environment


def parse_input_file(text, variables=None):
    """ Parser for a file with syntax somewhat similar to Drake."""
    lines = text.splitlines()
    tasks, linenumbers = find_tasks(lines)
    preamble = [line for line in lines[:linenumbers[0]]]
    logging.debug("Preamble:\n{}".format("\n".join(preamble)))
    if variables is not None:
        preamble += "\n" + "\n".join(variables)
    environment = create_environment(preamble)
    code_sections = []
    for n in range(len(linenumbers) - 1):
        code_sections.append((linenumbers[n], linenumbers[n+1]))
    for n, task in zip(code_sections, tasks):
        task["code"] = lines[n[0]: n[1]]
        task["environment"] = environment
    clean_tasks = []
    for task in tasks:
        clean_tasks.append(Task(**task))
    return clean_tasks
