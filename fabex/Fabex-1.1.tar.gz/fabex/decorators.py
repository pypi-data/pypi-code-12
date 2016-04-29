from __future__ import absolute_import

from sys import modules
from os.path import basename, splitext
from functools import wraps
from collections import defaultdict
from fabric.api import task, roles, env
from fabric.decorators import serial, _wrap_as_new

from fabex.exceptions import FabexRunError
from fabex.tasks import RoleTask, TaskGroup


def _get_fabmodule():
    try:
        return modules[splitext(basename(env.fabfile))[0]]
    except Exception as e:
        raise FabexRunError("error locating fabfile {}: {}".format(env.fabfile, e))


def task_roles(*args, **kwargs):
    invoked = bool(kwargs)
    roles_attach = roles(*args)
    group = kwargs.pop('group', None)
    def attach(func):
        task_wrapper = task(task_class=RoleTask, **kwargs)
        task_ = task_wrapper(roles_attach(func))
        if group:
            fabmodule = _get_fabmodule()
            if not hasattr(fabmodule, group):
                setattr(fabmodule, group, TaskGroup(group))
            getattr(fabmodule, group).append(task_)
        return task_
    return attach

_host_func_return_value = {}

def runs_once_per_host(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if (env.host, func) in _host_func_return_value:
            role = ":{role}".format(**env) if env.role else ""
            print("[{host}{}] Already executed '{command}' on this host".format(role, **env))
        else:
            _host_func_return_value[(env.host, func)] = func(*args, **kwargs)
        return _host_func_return_value[(env.host, func)]
    decorated = _wrap_as_new(func, decorated)
    # Mark as serial (disables parallelism) and return
    return serial(decorated)
