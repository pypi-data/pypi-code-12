import os
from basic_lib_tool import append
from ufs_tools import is_package_root
from inspect_utils import get_parent_frame_file, get_inspection_frame
from folder_tool import get_file_folder


def include_all_ext_packages(folder_name, lib_checker=is_package_root):
    caller_file = get_inspection_frame(3)
    if (caller_file[-1] == "/") or (caller_file[-1] == "\\"):
        caller_file = caller_file[0:-1]
    folder_path = os.path.join(get_file_folder(caller_file), folder_name)
    for i in os.listdir(folder_path):
        full_path = os.path.abspath(os.path.join(folder_path, i))
        if lib_checker(full_path):
            append(full_path)


def include_all_ex(folder_name):
    include_all_ext_packages(folder_name)