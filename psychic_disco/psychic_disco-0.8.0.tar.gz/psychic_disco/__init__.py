import re
import config
import deployment_package
import lambda_function
import api_gateway_config
import util

__all__ = [
        "config",
        "deployment_package",
        "lambda_function",
        "api_gateway_config"]

Api = {}


def lambda_entry_point(entry_point):
    lambda_function.LambdaFunction(
            entry_point.__name__,
            entry_point.__module__)
    return entry_point


def api_method(verb="GET", path="/"):
    key = "%s %s" % (verb, path)

    def install_api_method(func):
        func = lambda_entry_point(func)
        Api[key] = entry_points()[-1]
        return func
    return install_api_method


def entry_points():
    return lambda_function.declared_functions()


def convert_path_to_module(path):
    m = re.match(r"\.?\.?/?(.*)\.py", path)
    return ".".join(m.group(1).split("/"))


def attempt_import(module_name):
    try:
        __import__(module_name)
    except:
        pass


def discover_entrypoints(repo):
    for full_path in util.py_files_in_directory("."):
        relative_path = full_path.replace(repo, '', 1)
        module_name = convert_path_to_module(relative_path)
        attempt_import(module_name)
