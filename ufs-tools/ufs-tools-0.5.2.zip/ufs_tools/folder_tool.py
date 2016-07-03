import inspect
import os
import datetime
from inspect_utils import get_parent_frame_file

__author__ = 'weijia'


def find_root_path(file_path, root_folder_name):
    in_file_path = file_path
    folder_name = None
    while folder_name != root_folder_name:
        folder_name = os.path.basename(file_path)
        # log.error("find_root_path:"+folder_name)
        last_file_path = file_path
        file_path = os.path.dirname(file_path)
        if last_file_path == file_path:
            print "find root path failed, last_file_path: %s, file_path: " \
                  "%s, folder_name: %s, root_folder_name: %s" % (
                      last_file_path,
                      file_path, folder_name, root_folder_name)
            raise "No root path found"
    found_path = os.path.join(file_path, root_folder_name)
    # log.error("returning:"+found_path)
    return os.path.abspath(found_path)


def find_root(root_name, caller_level=1):
    """
    This will not work in frozen app, as the get_parent_frame is getting the absolute path of the file when frozen
    :param caller_level:
    :param root_name:
    """
    frame = inspect.getouterframes(inspect.currentframe())
    caller_frame = frame[caller_level]
    caller_file = os.path.abspath(caller_frame[1])
    return find_root_path(caller_file, root_name)


def get_file_folder(file_path):
    folder = os.path.abspath(os.path.dirname(file_path))
    return folder


def get_absolute_path_for_relative_path(relative_path):
    """
    This will not work in frozen app, as the get_parent_frame is getting the absolute path of the file when frozen
    :param relative_path:
    """
    caller_file = get_parent_frame_file()
    if (caller_file[-1] == "/") or (caller_file[-1] == "\\"):
        caller_file = caller_file[0:-1]
    folder = get_file_folder(caller_file)
    return os.path.abspath(os.path.join(folder, relative_path))


def get_root_sub_folder(file_path, root_name, sub_folder):
    root_path = find_root_path(file_path, root_name)
    return os.path.abspath(os.path.join(root_path, sub_folder))


def ensure_dir(full_path):
    if not os.path.exists(full_path):
        os.makedirs(full_path)


def get_parent_folder_for_folder(folder_path):
    return os.path.abspath(os.path.join(folder_path, ".."))


def get_grand_parent(folder_path):
    return get_parent_folder_for_folder(get_parent_folder_for_folder(folder_path))


def find_root_path_from_pkg(package_info):
    return find_root_path(package_info.file_path, package_info.package_root_name)


def get_year_month_dir(root_path, year=None, month=None):
    now_value = datetime.datetime.now()
    if year is None:
        year = now_value.strftime('%Y')
    if month is None:
        month = now_value.strftime('%m')
    data_dir = os.path.join(root_path, "%s%s%s" % (year, os.sep, month))

    ensure_dir(data_dir)
    return data_dir


def get_file_basename(file_path):
    default_name = os.path.basename(file_path).replace(".py", "").replace(".exe", "")
    return default_name
