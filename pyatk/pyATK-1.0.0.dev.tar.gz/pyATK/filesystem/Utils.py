#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import os
import fnmatch
from pyATK.utils.misc import if_else


###
# List files within folder tree (generator)
#
def walk_through_files(top_dir, folder_filter="", file_filter=""):
    for dir_path, _, file_names in os.walk(top_dir):
        if folder_filter in dir_path:
            pass
        else:
            continue
        for file_name in file_names:
            if file_filter == "":
                yield os.path.join(dir_path, file_name)
            else:
                if fnmatch.fnmatch(file_name, file_filter) is True:
                    yield os.path.join(dir_path, file_name)


###
# List child folders of top directory (generator)
#
def walk_through_folders(top_dir, folder_filter=""):
    for dir_path, _, _ in os.walk(top_dir):
        if folder_filter in dir_path:
            pass
        else:
            yield dir_path


###
# Returns the size of a folder's content. Returns 0 if the argument is not a folder
#
def folder_size(top_dir):
    if os.path.isdir(top_dir) is False:
        return 0
    else:
        total_size = 0
        for filename in walk_through_files(top_dir):
            total_size += os.path.getsize(filename)
        return total_size


def get_absolute_path(relative_path):
    return os.path.abspath(relative_path)


def compare_files(left, right):
    if not os.path.isfile(left):
        raise FileNotFoundError(str(left) + ": No such file or directory")
    if not os.path.isfile(right):
        raise FileNotFoundError(str(right) + ": No such file or directory")

    if os.path.getsize(left) == os.path.getsize(right):
        return 0
    else:
        with open(right, 'r') as right_file:
            right_content = right_file.read()
        with open(left, 'r') as left_file:
            left_content = left_file.read()

        if right_content > left_content:
            return 1
        return -1


def replace_in_file(file_path, pattern, replace_by_string, case_sensitive=True):
    output = ""
    abs_path = get_absolute_path(file_path)
    if os.path.isfile(abs_path):
        file = open(abs_path, 'r')
    else:
        raise IOError(abs_path + " is not a valid file")

    for line in file:
        print("reading line " + line)
        output = output + re.sub(pattern, replace_by_string, line, if_else(case_sensitive, None, re.IGNORECASE)) + os.linesep

    file.close()
    file = open(abs_path, 'w')
    if file:
        file.write(output)
    file.close()


def read_file_content(path, remove_empty_lines=False, encoding="utf-8"):
    abs_path = get_absolute_path(path)
    file = open(abs_path, mode="r", encoding=encoding)
    if file:
        content = ""
        for line in file:
            if remove_empty_lines is True:
                if line != "":
                    content += line
            else:
                content += line
    else:
        raise FileNotFoundError(abs_path + "No such file or directory")
    return content

if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
