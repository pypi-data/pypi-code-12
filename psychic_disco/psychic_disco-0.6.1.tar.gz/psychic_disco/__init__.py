import sys
import os
import re
import config

EntryPoints = []
Api = {}

def lambda_entry_point(entry_point):
    meta_info = dict()
    meta_info["func"] = entry_point.__name__
    meta_info["module"] = entry_point.__module__
    meta_info["full_name"] = "%s.%s" % (meta_info["module"] , meta_info["func"])
    EntryPoints.append(meta_info)
    return entry_point

def api_method(verb="GET", path="/"):
    key = "%s %s" % (verb, path)
    def install_api_method(func):
        func = lambda_entry_point(func)
        Api[key] = EntryPoints[-1]
        return lambda_entry_point(func)
    return install_api_method

def entry_points():
    return EntryPoints

def convert_path_to_module(path):
    m = re.match(r"\.?\.?/?(.*)\.py", path)
    return ".".join(m.group(1).split("/"))

def attempt_import(module_name):
    try:
        __import__(module_name, fromlist=["path"])
    except:
        pass

def discover_entrypoints(repo):
    for (dirpath, dirnames, filenames) in os.walk(repo):
        for dirname in dirnames:
            if dirname.startswith("."):
                dirnames.remove(dirname) # Don't visit hidden directories
        for filename in filenames:
            if filename.endswith(".py") and not filename.startswith("."): # Don't mess with hidden files
                full_path = os.path.join(dirpath, filename)
                relative_path = full_path.replace(repo,'',1)
                module_name = convert_path_to_module(relative_path)
                attempt_import(module_name)
