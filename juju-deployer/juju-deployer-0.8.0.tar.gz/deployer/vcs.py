from __future__ import absolute_import
import subprocess
import os
import re

from .utils import ErrorExit


class Vcs(object):

    err_update = (
        "Could not update branch %(path)s from %(branch_url)s\n\n %(output)s")
    err_branch = "Could not branch %(branch_url)s to %(path)s\n\n %(output)s"
    err_is_mod = "Couldn't determine if %(path)s was modified\n\n %(output)s"
    err_pull = (
        "Could not pull branch @ %(branch_url)s to %(path)s\n\n %(output)s")
    err_cur_rev = (
        "Could not determine current revision %(path)s\n\n %(output)s")

    def __init__(self, path, origin, log):
        self.path = path
        self.log = log
        self.extended_options = self.get_extended_options(origin)

        if self.extended_options:
            self.origin = origin.split("#")[0]
        else:
            self.origin = origin

    def _call(self, args, error_msg, cwd=None, stderr=()):
        try:
            if stderr is not None and not stderr:
                stderr = subprocess.STDOUT
            output = subprocess.check_output(
                args, cwd=cwd or self.path, stderr=stderr)
        except subprocess.CalledProcessError as e:
            self.log.error(error_msg % self.get_err_msg_ctx(e))
            raise ErrorExit()
        return output.strip().decode()

    def get_err_msg_ctx(self, e):
        return {
            'path': self.path,
            'branch_url': self.origin,
            'exit_code': e.returncode,
            'output': e.output,
            'vcs': self.__class__.__name__.lower()}

    def get_extended_options(self, origin):
        regexp = re.compile(r"[\?#&](?P<name>[^&=]+)=(?P<value>[^&=]+)")
        matched = regexp.findall(origin)

        if matched:
            ret = dict()
            for option in matched:
                (name, value) = option
                if name in ret:
                    raise Exception("%s option already defined" % name)
                ret[name] = value
            return ret
        return {}

    def get_cur_rev(self):
        raise NotImplementedError()

    def update(self, rev=None):
        raise NotImplementedError()

    def branch(self):
        raise NotImplementedError()

    def pull(self):
        raise NotImplementedError()

    def is_modified(self):
        raise NotImplementedError()

    # upstream missing revisions?


class Bzr(Vcs):

    def get_cur_rev(self):
        params = ["bzr", "revno", "--tree"]
        return self._call(params, self.err_cur_rev, stderr=None)

    def update(self, rev=None):
        params = ["bzr", "up"]
        if rev:
            params.extend(["-r", str(rev)])
        self._call(params, self.err_update)

    def branch(self):
        params = ["bzr", "co", "--lightweight", self.origin, self.path]
        cwd = os.path.dirname(os.path.dirname(self.path))
        if not cwd:
            cwd = "."
        self._call(params, self.err_branch, cwd)

    def is_modified(self):
        return subprocess.call(
            ["bzr", "diff"],
            cwd=self.path, stdout=subprocess.PIPE) != 0


class Git(Vcs):

    def get_cur_rev(self):
        params = ["git", "rev-parse", "HEAD"]
        return self._call(params, self.err_cur_rev)

    def update(self, rev=None):
        params = ["git", "reset", "--merge"]
        if rev:
            params.append(rev)
        self._call(params, self.err_update)

    def branch(self):
        params = ["git", "clone", "--depth", "1"]
        # Deal with branches in the format
        # <repository-url>;<branch>
        components = self.origin.split(';')
        if len(components) == 2:
            params += ["--branch", components[1],
                       components[0], self.path]
        else:
            params += [self.origin, self.path]
        cwd = os.path.dirname(os.path.dirname(self.path))
        if not cwd:
            cwd = "."

        self._call(params, self.err_branch, cwd)

        change_ref = self.extended_options.get('changeref', None)
        if change_ref:
            change_ref = 'refs/changes/{}/{}'.format(
                change_ref.split("/")[0][-2:], change_ref)

            self._call(["git", "fetch", "--depth", "1",
                        self.origin, change_ref],
                       self.err_branch, self.path)
            self._call(["git", "checkout", "FETCH_HEAD"], self.err_branch,
                       self.path)

    def is_modified(self):
        params = ["git", "status", "-s"]
        return bool(self._call(params, self.err_is_mod).strip())

    def get_remote_origin(self):
        params = ["git", "config", "--get", "remote.origin.url"]
        return self._call(params, "")
