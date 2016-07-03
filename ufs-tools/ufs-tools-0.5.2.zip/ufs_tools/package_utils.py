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


# Ref: http://stackoverflow.com/questions/1668223/how-to-de-import-a-python-module
def delete_module(modname, paranoid=None):
    from sys import modules
    try:
        this_module = modules[modname]
    except KeyError:
        raise ValueError(modname)
    these_symbols = dir(this_module)
    if paranoid:
        try:
            paranoid[:]  # sequence support
        except:
            raise ValueError('must supply a finite list for paranoid')
        else:
            these_symbols = paranoid[:]
    del modules[modname]
    for mod in modules.values():
        try:
            delattr(mod, modname)
        except AttributeError:
            pass
        if paranoid:
            for symbol in these_symbols:
                if symbol[:2] == '__':  # ignore special symbols
                    continue
                try:
                    delattr(mod, symbol)
                except AttributeError:
                    pass
