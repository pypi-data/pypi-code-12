import os
import sys
from filetools import format_path


def include_file_folder(file_path):
    include(os.path.dirname(file_path))


def direct_insert_folder_to_top_of_sys_path(folder):
    sys.path.insert(0, folder)


def include(folder):
    if is_folder_in_sys_path(folder):
        direct_insert_folder_to_top_of_sys_path(folder)


def is_folder_in_sys_path(folder):
    formatted_sys_path = []
    for folder in sys.path:
        formatted_sys_path.append(format_path(folder))
    return format_path(folder) in formatted_sys_path


def append(folder):
    folder = os.path.abspath(folder)
    if not (folder in sys.path):
        sys.path.append(folder)


def include_in_folder(folder, sub_folder_name):
    include(os.path.join(folder, sub_folder_name))


def remove_folder_in_sys_path(folder):
    formatted_folder = format_path(folder)
    for folder_in_sys_path in sys.path:
        if formatted_folder == format_path(folder_in_sys_path):
            sys.path.remove(folder_in_sys_path)
            return
    raise "Folder not found"