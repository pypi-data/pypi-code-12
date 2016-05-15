#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import inspect
import logging
from filetools import get_sibling_folder
from inspect_utils import get_parent_frame_file
from folder_tool import find_root_path, get_file_folder
from basic_lib_tool import include, append, include_in_folder

log = logging.getLogger(__name__)


def include_root_path(file_path, root_folder_name):
    include(find_root_path(file_path, root_folder_name))


def include_sub_folder_in_root_path(file_path, root_folder_name, folder_name):
    root_folder_path = find_root_path(file_path, root_folder_name)
    include_in_folder(root_folder_path, folder_name)


def include_sub_folder(package_info, folder_name):
    root_folder_path = find_root_path(package_info)
    include_in_folder(root_folder_path, folder_name)


def include_folders(lib__full_path_list):
    for i in lib__full_path_list:
        include(i)


def include_file_sibling_folder(file_path, sub_folder_name):
    if (file_path[-1] == "/") or (file_path[-1] == "\\"):
        file_path = file_path[0:-1]
    folder = get_file_folder(file_path)
    include_in_folder(folder, sub_folder_name)


def exclude(folder):
    folder = os.path.abspath(folder)
    if folder in sys.path:
        sys.path.remove(folder)


def get_parent_of_folder_containing_file(file_path):
    # print "parent:"+os.path.abspath(os.path.join(os.path.dirname(file_path),".."))
    return os.path.abspath(os.path.join(os.path.dirname(file_path), ".."))


def include_all_direct_subfolders(folder_path):
    for i in os.listdir(folder_path):
        full_path = os.path.abspath(os.path.join(folder_path, i))
        if os.path.isdir(full_path):
            append(full_path)


def include_all_direct_sub_folders_in_sibling(file_path, folder_name):
    include_all_direct_subfolders(get_sibling_folder(file_path, folder_name))


def is_package_root(full_path):
    return os.path.isdir(full_path) or ".zip" in full_path


def include_all_ext_packages(folder_path, lib_checker=is_package_root):
    for i in os.listdir(folder_path):
        full_path = os.path.abspath(os.path.join(folder_path, i))
        if lib_checker(full_path):
            append(full_path)


def include_all(file_path, folder_name):
    include_all_ext_packages(get_sibling_folder(file_path, folder_name))


def get_current_path():
    frame = inspect.getouterframes(inspect.currentframe())
    caller_frame = frame[1]
    dir_path = os.path.abspath(os.path.dirname(caller_frame[1]))
    return dir_path


def include_sub_folder_in_root_path_ex(root_folder_name, folder_name):
    frame = inspect.getouterframes(inspect.currentframe())
    caller_frame = frame[1]
    caller_file = caller_frame[1]
    root_folder_path = find_root_path(caller_file, root_folder_name)
    include_in_folder(root_folder_path, folder_name)


def include_file_sibling_folder_ex(sub_folder_name):
    caller_file = get_parent_frame_file()
    if (caller_file[-1] == "/") or (caller_file[-1] == "\\"):
        caller_file = caller_file[0:-1]
    folder = get_file_folder(caller_file)
    include_in_folder(folder, sub_folder_name)


def include_sibling_file(file_path, filename):
    if (file_path[-1] == "/") or (file_path[-1] == "\\"):
        file_path = file_path[0:-1]
    folder = get_file_folder(file_path)
    include(os.path.join(folder, filename))


# noinspection SpellCheckingInspection
def add_path_to_python_path_env(full_path):
    full_path = full_path.replace("\\", "/")
    original = os.environ.get("PYTHONPATH", "")
    separator = ";"  # Only for windows, TODO: need to add cross platform support
    original_paths = original.split(separator)
    for original_path in original_paths:
        formatted_original = original_path.replace("\\", "/")
        if full_path == formatted_original:
            return
    original_paths.append(full_path)
    os.environ["PYTHONPATH"] = separator.join(original_paths)
