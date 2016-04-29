import yaml
from os.path import isabs, join
from collections import defaultdict
from fabric.api import env, task, runs_once, require, execute
from fabric.tasks import WrappedCallableTask, Task
from fabric import state

from fabex.exceptions import FabexConfigError
from fabex.context_managers import role_settings, host_settings
from .crypt import AESCipher


__all__ = ['dryrun', 'verbose', 'target', 'roles', 'password', 'encrypt']

env.dryrun = False
env.verbose = True

__cipher = None

@task
@runs_once
def dryrun(dryrun="yes"):
    """Fabex: Set dryrun for no execution of commands"""
    env.dryrun = dryrun.lower() in ('y', 'yes', 't', 'true')


@task
@runs_once
def verbose(verbose="yes"):
    """Fabex: Shows running and output of tasks if =yes"""
    env.verbose = verbose.lower() in ('y', 'yes', 't', 'true')


@task
@runs_once
def quiet(quiet="yes"):
    """Fabex: Hides running and output of tasks if =yes"""
    env.verbose = not quiet.lower() in ('y', 'yes', 't', 'true')

@task
@runs_once
def password(pw):
    """Fabex: password:pw, set the encryption password for encrypt and yaml !decrypt"""
    global __cipher
    __cipher = AESCipher(pw)

@task
@runs_once
def encrypt(text):
    """Fabex: encrypt:text, must call password task first"""

    if not __cipher:
        raise FabexConfigError("password:pw required for encrypt task")
    print(__cipher.encrypt(text))

def decrypt_constructor(loader, node):
    """for !decrypt('encrypted-string') in yaml"""
    if not __cipher:
        raise yaml.YAMLError("target uses !decrypt but password:pw not called")
    etext = loader.construct_scalar(node)
    text = __cipher.decrypt(etext)
    if not text:
        raise yaml.YAMLError("{} could not be decrypted".format(etext))
    return text

yaml.add_constructor(u'!decrypt', decrypt_constructor)

@task
@runs_once
def target(name):
    """Fabex: target:name, read the name.yaml configuration"""

    require('fabex_config')

    target_path = name
    if not isabs(target_path) and 'target_dir' in env.fabex_config:
        target_path = join(env.fabex_config['target_dir'], target_path)
    if not target_path.endswith('.yaml'):
        target_path += '.yaml'
    with open(target_path) as f:
        env.update(yaml.load(f))
    env.target = name

    hostroles = defaultdict(set)
    for role, hosts in env.roledefs.items():
        for host in hosts:
            hostroles[host].add(role)
    env.hostroles = dict(hostroles)

    # Alongside env.hosts is env.roles (not to be confused with env.roledefs!)
    # which, if given, will be taken as a list of role names to look up in env.roledefs.
    #
    # We accept a preset env.roles list, from command line or otherwise before this task
    # executes. However, an empty roles list means all roles from target role_settings.
    # Also, assert that all roles in use have an entry in env.roledefs.
    if not set(env.roles).issubset(env.roledefs.keys()):
        raise FabexConfigError("roles in {} not found in roledefs: {}"
                               .format(','.join(env.roles), ','.join(env.roledefs.keys())))

    # Handle 'extends' in role_settings
    for role, settings in env.roleenvs.items():
        extends = settings.get('extends')
        if not extends:
            continue
        extends = extends if isinstance(extends, list) else [extends]
        settings_backup = settings.copy()
        for parent in extends:
            if parent not in env.roledefs:
                raise FabexConfigError("extends refers to nonexistant role: "
                                       "{} in role_settings for {}".format(parent, role))
            settings.update(env.roleenvs.get(parent, {}))
        # child settings always override parent
        settings.update(settings_backup)

    env.verbose = env.get('verbose', True)


class TaskGroup(Task):
    def __init__(self, name, *args, **kwargs):
        self.tasks = []
        self.roles = []
        self.__doc__ = "Fabex group: ".format(name)
        super(TaskGroup, self).__init__(name=name, *args, **kwargs)

    def append(self, task):
        if not env.roles or set(task.wrapped.roles).intersection(env.roles):
            # don't add to group if --roles= and task does not have requested role
            self.tasks.append(task)
            self.__doc__ += ("" if self.__doc__.endswith(" ") else ", ") + task.name
            self.roles.extend([r for r in task.wrapped.roles if r not in self.roles])

    def run(self, *args, **kwargs):
        task_role_filter = lambda t: env.hostroles[env.host].intersection(t.wrapped.roles)
        task_filter = ((lambda t: task_role_filter(t).intersection(env.roles)) if env.roles
                       else task_role_filter)
        tasks = filter(task_filter, self.tasks)
        return {task.name: execute(task, *args, host=env.host, **kwargs) for task in tasks}

    def __repr__(self):
        return "TaskGroup({},[{}])".format(self.name, ','.join(map(str, self.tasks)))


class RoleTask(WrappedCallableTask):
    def run(self, *args, **kwargs):
        ret = {}
        roles_requested = env.roles or env.hostroles[env.host]
        roles = filter(lambda r: r in roles_requested and env.host in env.roledefs[r], self.roles)
        for role in roles:
            with role_settings(role), host_settings(env.host):
                if state.output.running and not hasattr(self, 'return_value'):
                    print("[{host}:{role}] Executing role task '{command}'".format(**env))
                ret[role] = super(RoleTask, self).run(*args, **kwargs)
        return ret

    def __repr__(self):
        return "RoleTask({},[{}])".format(self.name, ','.join(self.roles))
