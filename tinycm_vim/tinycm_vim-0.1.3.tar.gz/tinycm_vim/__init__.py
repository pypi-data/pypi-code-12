from tinycm import Dependency, InvalidParameterError
from tinycm.basedefinition import BaseDefinition

import pwd
import os


class VimDefinition(BaseDefinition):
    def init(self, is_global=False, ensure='exists', config=None, type='constant', interpolate=False):
        self.is_global = is_global
        self.ensure = ensure
        self.config = config if config else self._get_default_config()
        self.type = type
        self.interpolate = interpolate

        if type not in ['constant', 'http']:
            raise InvalidParameterError('Type not in [constant, http]')

        # Add dependencies
        self.after.append('file::{}'.format(self._get_config_path()))
        if not self.is_global:
            self.after.append('user::{}'.format(self.name))

    def dependencies(self):
        user = self.name
        after = ['user::{}'.format(self.name)]
        if self.is_global:
            user = 'root'
            after = []

        after.append('package::vim')

        dependencies = [
            Dependency('package', 'vim', {'ensure': 'installed'}),
            Dependency('file', self._get_config_path(), {
                'ensure': 'exists',
                'type': self.type,
                'contents': self.config,
                'interpolate': self.interpolate,
                'permission-mask': '644',
                'owner': user,
                'after': after
            })
        ]
        if not self.is_global:
            Dependency('user', self.name, {'ensure': 'exists'})
        return dependencies

    def try_merge(self, other):
        self.ensure = self.merge_if_same('ensure', other)
        self.is_global = self.merge_if_same('is_global', other, False)
        self.type = self.merge_if_same('type', other)
        self.interpolate = self.merge_if_same('interpolate', other, False)
        return self

    def get_config_state(self):
        return {}

    def get_system_state(self):
        return {}

    def update_state(self):
        pass

    def _get_config_path(self):
        if self.is_global:
            return '/etc/vim/vimrc.local'

        homedir = pwd.getpwnam(self.name).pw_dir
        return os.path.join(homedir, '.vimrc')

    def _get_default_config(self):
        return "set nocompatible\n" \
               "filetype ident plugin on\n" \
               "syntax on\n" \
               "set hlsearch\n" \
               "set ignorecase\n" \
               "set smartcase\n" \
               "set autoindent\n" \
               "set shiftwidth=4\n" \
               "set softtabstop=4\n" \
               "set expandtab\n"
