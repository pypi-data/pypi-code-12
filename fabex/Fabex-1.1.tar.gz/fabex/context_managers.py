from __future__ import absolute_import

from contextlib import contextmanager
from fabric.api import env, settings
from .exceptions import FabexConfigError

@contextmanager
def role_settings(role, **kwargs):
    """Inject env.roleenvs[role], plus settings from kwargs"""

    new_settings = kwargs.copy()
    roledict = env.roleenvs.get(role)
    if not roledict:
        raise FabexConfigError("role {} not found in target roleenvs".format(role))
    new_settings.update(roledict)
    new_settings['role'] = role
    with settings(**new_settings):
        yield

@contextmanager
def host_settings(host, **kwargs):
    """Inject env.hostenvs[role], plus settings from kwargs"""

    new_settings = kwargs.copy()
    hostdict = env.hostenvs.get(host)
    if not hostdict:
        raise FabexConfigError("host {} not found in target hostenvs".format(host))
    new_settings.update(hostdict)
    with settings(**new_settings):
        env.host_string = env.get('ssh_host', env.host)
        if 'ssh_user' in env:
            env.host_string = env['ssh_user'] + '@' + env.host_string
        yield
