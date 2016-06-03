import os
import subprocess
from contextlib import contextmanager


class GitRepo:

    def __init__(self, git_command="git", repo_dir=".", **kwargs):
        self.git_command = git_command
        self.repo_dir = repo_dir

        self.subprocess_params = {
            'stderr': subprocess.STDOUT,
        }
        self.subprocess_params.update(kwargs)

    def __getattr__(self, method):
        method = method.replace('_', '-')

        def _git_method(*args, **kwargs):
            return self.__run_command(method,
                                      git_cmd_params=args, check_output_params=kwargs)

        return _git_method

    def __run_command(self, method, git_cmd_params, check_output_params=None):

        @contextmanager
        def cwd(new_dir):
            old_dir = os.path.abspath(os.curdir)
            try:
                os.chdir(new_dir)
                yield
            finally:
                os.chdir(old_dir)

        if check_output_params is None:
            check_output_params = {}

        check_output_params.update(self.subprocess_params)
        cmd_line = [self.git_command, method] + list(git_cmd_params)
        with cwd(self.repo_dir):
            return subprocess.check_output(cmd_line,
                                           **check_output_params).decode('utf-8')
