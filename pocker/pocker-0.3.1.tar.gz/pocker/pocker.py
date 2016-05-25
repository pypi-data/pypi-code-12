#!/usr/bin/python
# encoding: utf-8
from subprocess import Popen, PIPE
import collections
import warnings
import os
import shlex

from .utils import required_version, Ver
from .parsers import (parse_top, parse_ps, parse_build, parse_id, parse_port,
                      parse_images, parse_history, parse_inspect, parse_diff,
                      parse_colon, parse_version, parse_wait, parse_network_ls,
                      parse_name, parse_volume_ls)
from .exceptions import (PockerException, PEnvVarsError, PDockerLauncherError,
                         PNotYetImplemented, PUnsupportedOption, PExitNonZero,
                         PRejectedOption)


def castval(value):
    if value is True:
        return 'true'
    elif value is False:
        return 'false'
    else:
        return value


def castkey(key):
    return key.replace('_', '-')


def getopts(**opts):
    docker_opts = []
    for key, value in opts.iteritems():
        if value is None:
            continue
        if key.startswith('_'): #internal kwarg
            continue

        if callable(value):
            value = value()
        if isinstance(value, basestring):
            values = (value,)
        elif isinstance(value, collections.Sequence):
            values = tuple(value)
        else:
            values = (value,)

        tmpl = "-{0}={1}" if (len(key) == 1) else "--{0}={1}"
        for value in values:
            docker_opts.append(tmpl.format(castkey(key), castval(value)))

    return docker_opts


def reject_opts(opts, *args):
    for key in opts.keys():
        if key in args:
            raise PRejectedOption(
                u"You are trying to use unsuppoerted option: '{0}'. ".format(key) +
                u"Provide custom parser('_parser' kwarg) if you really need it."
            )

def get_result(call_result, stdout_parser=None, suppress_excp=False):
    stdout_raw, stderr_raw, exit_code = call_result
    stdout_parser = (lambda _: None) if (stdout_parser is None) else stdout_parser
    result = stdout_parser(stdout_raw) if stdout_raw else None
    return PockerResp(stdout_raw, stderr_raw, exit_code, result, suppress_excp)


class PockerResp(object):
    def __init__(self, stdout_raw, stderr_raw,
                 exit_code, result, suppress_excp=False):
        self.stdout_raw = stdout_raw
        self.stdout_lines = stdout_raw.split('\n') if stdout_raw else None
        self.stderr_raw = stderr_raw
        self.stderr_lines = stderr_raw.split('\n') if stderr_raw else None
        self.exit_code = exit_code
        self.result = result
        if not suppress_excp:
            if exit_code != 0:
                raise PExitNonZero(self)

    def __getitem__(self, key):
        return getattr(self, key)

    def keys(self):
        return ['stdout_raw', 'stdout_lines', 'stderr_raw',
                'stderr_lines', 'exit_code', 'result']

    def __str__(self):
        return "<PockerResp:exit_code={0}, result={1}>".format(self.exit_code, self.result)



class Docker(object):
    def __init__(self, _launcher='docker', _envvars=None, _merge_sys_envvars=True,
                 _required_versions=None, _suppress_excp=False, **opts):
        """
        KwArgs:
            host (str)
        """
        self.docker_opts = opts
        self.launcher = _launcher
        self.suppress_excp = _suppress_excp
        self.envvars = self._get_envvars(_envvars, _merge_sys_envvars)
        self.current_version = self._check_and_get_version(_required_versions)

    def _get_envvars(self, _envvars, _merge_sys_envvars):
        for key, val in (_envvars or {}).iteritems():
            if not isinstance(val, basestring):
                raise PEnvVarsError(u"Values in '_envars' dict must be strings, instead got " +
                                      u"value '{0}' of type '{1}' for key {2}".format(val, type(val), key))

        if _envvars and _merge_sys_envvars:
            _envvars = dict(os.environ.copy(), **(_envvars or {}))
        return _envvars

    def _check_and_get_version(self, _required_versions=None):
        try:
            resp = self.version()
            version = resp.result
            if version is None:
                raise PockerException(resp.stdout_raw + resp.stderr_raw)
            current_version = version['Client']['Version']
        except OSError as err:
            if err.errno == os.errno.ENOENT: #no such file
                raise PDockerLauncherError(
                    u"Seems that docker isn't istalled on this host. "
                    u"Or there is error in path to custom '_launcher'. "
                    u"There was '{0}' exception.".format(err)
                )
            raise err

        if _required_versions is not None:
            required_version(current_version, _required_versions)

        return current_version

    def _reject(self, opts, to_reject):
        if not '_parser' in opts: #if custom  parser isn't provided
            reject_opts(opts, *to_reject.split())


    def _call(self, cmd, *args, **opts):
        #TODO: редирект stdin и stdout на python file objects
        # лучше просто возвращать ручки stdin и output, кому надо пускай сам заморачивается
        pargs = [self.launcher] + getopts(**self.docker_opts) + shlex.split(cmd) + getopts(**opts) + filter(lambda arg: arg is not None, list(args))
        proc = Popen(pargs, stdin=PIPE, stdout=PIPE, stderr=PIPE, env=self.envvars)
        stdout_raw, stderr_raw = proc.communicate(opts.get('_input', None))
        if 'flag provided but not defined' in stderr_raw:
            raise PUnsupportedOption(stderr_raw)

        return  stdout_raw, stderr_raw, proc.returncode

    #TODO: аналог _call для интерактивной сессии с использование генератора?
    # - чтобы получать stream(logs, events) или общатся с контейнером(exec, run, attach)
    # - быть с этим осторожнее, иначе программа может заблокироваться если pipe буффер заполнится
    # - кроме того, все передающиеся данные будут хранится в этом случае в оперативке
    #   т.е. для тяжелых данных лучше использовать TempFile и опцию --output где возможно

    #все методы принимают команды в exec формате
    #если лень все разбивать на exec формата, можно использовать shlex
    #https://docs.python.org/2/library/subprocess.html#subprocess.Popen
    # import shlex
    # d.cmd(shlex.split('cmd arg1 arg2 ..'))

    def daemon(self, **opts):
        if self.docker_opts:
            raise PockerException(u"Method 'daemon' can't be used if self.docker_opts non empty."
                                  u"Create another pocker instance to start daemon: Docker().daemon()")
        self._reject(opts, 'h help')
        #TODO: use daemon command for docker version > 1.7.0(?)
        return get_result(self._call('-d', **opts),
                          opts.get('_parser', None),
                          opts.get('_suppress_excp', self.suppress_excp))

    def attach(self, *args, **opts):
        raise PNotYetImplemented()

    def build(self, path, *args, **opts):
        """
        Args:
            path (str): PATH to build context or URL to git repo
        """
        self._reject(opts, 'h help')
        return get_result(self._call('build', path, **opts),
                          opts.get('_parser', parse_build),
                          opts.get('_suppress_excp', self.suppress_excp))

    def commit(self, *args, **opts):
        raise PNotYetImplemented()

    def cp(self, *args, **opts):
        raise PNotYetImplemented()

    def create(self, image, *args, **opts):
        """
        Args:
            image (str): image NAME or ID
        """
        self._reject(opts, 'h help')
        return get_result(self._call('create', image, *args, **opts),
                          opts.get('_parser', parse_id),
                          opts.get('_suppress_excp', self.suppress_excp))

    def diff(self, container, *args, **opts):
        """
        Args:
            container (str): container NAME or ID
        """
        self._reject(opts, 'h help')
        return get_result(self._call('diff', container, *args, **opts),
                          opts.get('_parser', parse_diff),
                          opts.get('_suppress_excp', self.suppress_excp))

    def events(self, *args, **opts):
        raise PNotYetImplemented()

    def exec_(self, container, cmd, *args, **opts):
        """
        Args:
            container (str): container NAME or ID
            cmd (str): command to execute in container
        """
        self._reject(opts, 'h help')
        return get_result(self._call('exec', container, cmd, *args, **opts),
                          opts.get('_parser', None),
                          opts.get('_suppress_excp', self.suppress_excp))

    def export(self, *args, **opts):
        raise PNotYetImplemented()

    def history(self, image, *args, **opts):
        """
        Args:
            image (str): image NAME or ID
        """
        self._reject(opts, 'h help q quiet')
        return get_result(self._call('history', image, *args, **opts),
                          opts.get('_parser', parse_history),
                          opts.get('_suppress_excp', self.suppress_excp))

    def images(self, *args, **opts):
        self._reject(opts, 'h help q quiet')
        opts.setdefault('no_trunc', True)
        return get_result(self._call('images', *args, **opts),
                          opts.get('_parser', parse_images),
                          opts.get('_suppress_excp', self.suppress_excp))

    def import_(self, *args, **opts):
        raise PNotYetImplemented()

    def info(self, *args, **opts):
        self._reject(opts, 'h help')
        return get_result(self._call('info', *args, **opts),
                          opts.get('_parser', parse_colon),
                          opts.get('_suppress_excp', self.suppress_excp))

    def inspect(self, entity, *args, **opts):
        """
        Args:
            entity (str): container or image NAME or ID
        """
        self._reject(opts, 'h help f format')
        return get_result(self._call('inspect', entity, *args, **opts),
                          opts.get('_parser', parse_inspect),
                          opts.get('_suppress_excp', self.suppress_excp))

    def kill(self, container, *args, **opts):
        """
        Args:
            container (str): container NAME or ID
        """
        self._reject(opts, 'h help')
        return get_result(self._call('kill', container, *args, **opts),
                          opts.get('_parser', None),
                          opts.get('_suppress_excp', self.suppress_excp))

    def load(self, *args, **opts):
        raise PNotYetImplemented()

    def login(self, *args, **opts):
        raise PNotYetImplemented()

    def logout(self, *args, **opts):
        raise PNotYetImplemented()

    def logs(self, container, *args, **opts):
        #TODO: logs stream
        """
        Args:
            container (str): container NAME or ID
        """
        self._reject(opts, 'h help')
        return get_result(self._call('logs', container, *args, **opts),
                          opts.get('_parser', None),
                          opts.get('_suppress_excp', self.suppress_excp))

    def network_connect(self, network, container, *args, **opts):
        """
        Args:
            network (str): network NAME or ID
            container (str): container NAME or ID
        """
        self._reject(opts, 'h help')
        return get_result(self._call('network connect', network, container, *args, **opts),
                          opts.get('_parser', None),
                          opts.get('_suppress_excp', self.suppress_excp))

    def network_create(self, network, *args, **opts):
        """
        Args:
            network (str): network NAME
        """
        self._reject(opts, 'h help')
        return get_result(self._call('network create', network, *args, **opts),
                          opts.get('_parser', parse_id),
                          opts.get('_suppress_excp', self.suppress_excp))

    def network_disconnect(self, network, container, *args, **opts):
        """
        Args:
            network (str): network NAME or ID
            container (str): container NAME or ID
        """
        self._reject(opts, 'h help')
        return get_result(self._call('network disconnect', network, container, *args, **opts),
                          opts.get('_parser', None),
                          opts.get('_suppress_excp', self.suppress_excp))

    def network_inspect(self, network, *args, **opts):
        """
        Args:
            network (str): network NAME or ID
        """
        self._reject(opts, 'h help')
        return get_result(self._call('network inspect', network, *args, **opts),
                          opts.get('_parser', parse_inspect),
                          opts.get('_suppress_excp', self.suppress_excp))

    def network_ls(self, *args, **opts):
        self._reject(opts, 'h help q quite')
        opts.setdefault('no_trunc', True)
        return get_result(self._call('network ls', *args, **opts),
                          opts.get('_parser', parse_network_ls),
                          opts.get('_suppress_excp', self.suppress_excp))

    def network_rm(self, network, *args, **opts):
        """
        Args:
            network (str): network NAME or ID
        """
        self._reject(opts, 'h help')
        return get_result(self._call('network rm', network, *args, **opts),
                          opts.get('_parser', None),
                          opts.get('_suppress_excp', self.suppress_excp))

    def volume_create(self, *args, **opts):
        self._reject(opts, 'h help')
        return get_result(self._call('volume create', *args, **opts),
                          opts.get('_parser', parse_name),
                          opts.get('_suppress_excp', self.suppress_excp))

    def volume_inspect(self, volume, *args, **opts):
        """
        Args:
            volume (str): volume NAME
        """
        self._reject(opts, 'h help')
        return get_result(self._call('volume inspect', volume, *args, **opts),
                          opts.get('_parser', parse_inspect),
                          opts.get('_suppress_excp', self.suppress_excp))

    def volume_ls(self, *args, **opts):
        self._reject(opts, 'h help q quite')
        return get_result(self._call('volume ls', *args, **opts),
                          opts.get('_parser', parse_volume_ls),
                          opts.get('_suppress_excp', self.suppress_excp))

    def volume_rm(self, volume, *args, **opts):
        """
        Args:
            volume (str): volume NAME
        """
        self._reject(opts, 'h help')
        return get_result(self._call('volume rm', volume, *args, **opts),
                          opts.get('_parser', None),
                          opts.get('_suppress_excp', self.suppress_excp))

    def pause(self, container, *args, **opts):
        """
        Args:
            container (str): container NAME or ID
        """
        self._reject(opts, 'h help')
        return get_result(self._call('pause', container, *args, **opts),
                          opts.get('_parser', None),
                          opts.get('_suppress_excp', self.suppress_excp))

    def port(self, container, *args, **opts):
        """
        Args:
            container (str): container NAME or ID
        """
        self._reject(opts, 'h help')
        return get_result(self._call('port', container, *args, **opts),
                          opts.get('_parser', parse_port),
                          opts.get('_suppress_excp', self.suppress_excp))

    def ps(self, *args, **opts):
        self._reject(opts, 'h help q quiet format')
        opts.setdefault('no_trunc', True)
        if Ver(self.current_version) > Ver('1.8.0'):
            #enforce output format, to override settings in ~/.docker/config.json
            opts.setdefault('format', "table {{.ID}}\t{{.Image}}\t{{.Command}}\t{{.CreatedAt}}\t{{.Status}}\t{{.Ports}}\t{{.Names}}")
        return get_result(self._call('ps', *args, **opts),
                          opts.get('_parser', parse_ps),
                          opts.get('_suppress_excp', self.suppress_excp))

    def pull(self, repo, *args, **opts):
        #TODO: parser: downloaded, up to date
        """
        Args:
            repo (str): image name(optionaly with tag and repo address)
        """
        self._reject(opts, 'h help')
        return get_result(self._call('pull', repo, *args, **opts),
                          opts.get('_parser', None),
                          opts.get('_suppress_excp', self.suppress_excp))

    def push(self, *args, **opts):
        raise PNotYetImplemented()

    def rename(self, old_name, new_name, *args, **opts):
        """
        Args:
            container (str): container NAME or ID
        """
        self._reject(opts, 'h help')
        return get_result(self._call('rename', old_name, new_name, *args, **opts),
                          opts.get('_parser', None),
                          opts.get('_suppress_excp', self.suppress_excp))

    def restart(self, container, *args, **opts):
        """
        Args:
            container (str): container NAME or ID
        """
        self._reject(opts, 'h help')
        return get_result(self._call('restart', container, *args, **opts),
                          opts.get('_parser', None),
                          opts.get('_suppress_excp', self.suppress_excp))

    def rm(self, container, *args, **opts):
        """
        Args:
            container (str): container NAME or ID
        """
        self._reject(opts, 'h help')
        return get_result(self._call('rm', container, *args, **opts),
                          opts.get('_parser', None),
                          opts.get('_suppress_excp', self.suppress_excp))

    def rmi(self, image, *args, **opts):
        #TODO: parser: deleted, untagged, errors(can't delete)
        """
        Args:
            image (str): image NAME or ID
        """
        self._reject(opts, 'h help')
        return get_result(self._call('rmi', image, *args, **opts),
                          opts.get('_parser', None),
                          opts.get('_suppress_excp', self.suppress_excp))

    def run(self, image, *args, **opts):
        """
        Args:
            image (str): image NAME or ID
        """
        self._reject(opts, 'h help')
        return get_result(self._call('run', image, *args, **opts),
                          opts.get('_parser', parse_id),
                          opts.get('_suppress_excp', self.suppress_excp))

    def save(self, *args, **opts):
        raise PNotYetImplemented()

    def search(self, *args, **opts):
        raise PNotYetImplemented()

    def start(self, container, *args, **opts):
        """
        Args:
            container (str): container NAME or ID
        """
        self._reject(opts, 'h help')
        return get_result(self._call('start', container, *args, **opts),
                          opts.get('_parser', None),
                          opts.get('_suppress_excp', self.suppress_excp))

    def stop(self, container, *args, **opts):
        """
        Args:
            container (str): container NAME or ID
        """
        self._reject(opts, 'h help')
        return get_result(self._call('stop', container, *args, **opts),
                          opts.get('_parser', None),
                          opts.get('_suppress_excp', self.suppress_excp))

    def stats(self, container, *args, **opts):
        #TODO: parser
        #TODO: если сделать интерактинвый режим, добавить возможность получать stream
        """
        Args:
            container (str): container NAME or ID
        """
        if Ver(self.current_version) < Ver('1.7.1'):
            raise PNotYetImplemented("For docker < 1.7.1 'stats' can only be run"
                                     "in stream mode. Work with streams isn't"
                                     "implemented yet in 'pocker'")
        self._reject(opts, 'h help')
        opts.setdefault('no_stream', True)
        return get_result(self._call('stats', container, *args, **opts),
                          opts.get('_parser', None),
                          opts.get('_suppress_excp', self.suppress_excp))

    def tag(self, image, name, *args, **opts):
        """
        Args:
            image (str): image NAME or ID
            name (str): additional name for image(with tag)
        """
        self._reject(opts, 'h help')
        return get_result(self._call('tag', image, name, *args, **opts),
                          opts.get('_parser', None),
                          opts.get('_suppress_excp', self.suppress_excp))

    def top(self, container, *args, **opts):
        """
        [ps OPTIONS] isn't supported by default parser!

        Args:
            container (str): container NAME or ID
        """
        self._reject(opts, 'h help')
        return get_result(self._call('top', container, *args, **opts),
                          opts.get('_parser', parse_top),
                          opts.get('_suppress_excp', self.suppress_excp))

    def unpause(self, container, *args, **opts):
        """
        Args:
            container (str): container NAME or ID
        """
        self._reject(opts, 'h help')
        return get_result(self._call('unpause', container, *args, **opts),
                          opts.get('_parser', None),
                          opts.get('_suppress_excp', self.suppress_excp))

    def version(self, *args, **opts):
        """
        Args:
            container (str): container NAME or ID
        """
        self._reject(opts, 'h help')
        return get_result(self._call('version', *args, **opts),
                          opts.get('_parser', parse_version),
                          opts.get('_suppress_excp', self.suppress_excp))

    def wait(self, container, *args, **opts):
        """
        Args:
            container (str): container NAME or ID
        """
        self._reject(opts, 'h help')
        return get_result(self._call('wait', container, *args, **opts),
                          opts.get('_parser', parse_wait),
                          opts.get('_suppress_excp', self.suppress_excp))


