from tinycm.basedefinition import BaseDefinition
import subprocess
import os
import logging
import shutil

logger = None


class GitDefinition(BaseDefinition):
    def init(self, ensure, remote, recursive=False):
        self.ensure = ensure
        self.remote = remote
        self.recursive = recursive

        global logger
        logger = logging.getLogger('tinycm')

    def try_merge(self, other):
        self.ensure = self.merge_if_same('ensure', other)
        self.remote = self.merge_if_same('remote', other)
        self.recursive = self.merge_if_same('recursive', other, False)
        return self

    def get_system_state(self):
        if not os.path.isdir(self.name) or not os.path.isdir(os.path.join(self.name, '.git')):
            return {
                'cloned': False
            }

        result = {
            'cloned': True,
            'ensure': self._git_get_current_rev()
        }
        return result

    def get_config_state(self):
        if self.ensure == 'removed':
            return {
                'cloned': False
            }
        return {
            'cloned': True,
            'ensure': self.ensure
        }

    def update_state(self, state_diff):
        diff = state_diff.changed_keys()
        if 'cloned' in diff:
            if self.ensure == 'removed':
                shutil.rmtree(self.name)
            else:
                self._git_clone()

        if 'ensure' in diff:
            self._git_checkout()

    def _git_command(self, command):
        return subprocess.check_output(command, cwd=self.name, universal_newlines=True)

    def _git_clone(self):
        command = ['git', 'clone', self.remote, self.name]
        if self.recursive:
            command.append('--recursive')

        return subprocess.check_output(command, universal_newlines=True)

    def _git_checkout(self):
        command = ['git', 'checkout', self.ensure]
        return self._git_command(command)

    def _git_get_current_rev(self):
        command = ['git', 'rev-parse', '--abbrev-ref', 'HEAD']
        result = self._git_command(command).strip()
        if result != 'HEAD':
            return result

        command = ['git', 'describe', '--tags']
        return self._git_command(command).strip()
