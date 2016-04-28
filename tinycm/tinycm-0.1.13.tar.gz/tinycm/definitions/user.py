from tinycm import DefinitionConflictError, InvalidParameterError
from tinycm.basedefinition import BaseDefinition
import os
import pwd
import grp
import spwd
import crypt
import subprocess


class UserDefinition(BaseDefinition):
    def init(self, ensure, password=None, password_hash=None, uid=None, gid=None, comment=None, homedir=None,
             shell='/bin/false', groups=None, manage_home=False):
        self.ensure = ensure
        self.password = password
        self.password_hash = password_hash
        self.uid = uid
        self.gid = gid
        self.comment = comment
        self.homedir = homedir
        self.shell = shell
        self.extra_groups = groups
        self.manage_home = manage_home

        if self.password and self.password_hash:
            raise InvalidParameterError('Both password and password-hash defined.')

        if not os.path.isfile(self.shell):
            raise InvalidParameterError('Shell "{}" does not exist'.format(self.shell))

    def try_merge(self, other):
        self.ensure = self.merge_if_same('ensure', other)
        self.comment = self.merge_if_same('comment', other)
        self.shell = self.merge_if_same('shell', other, '/bin/false')
        self.uid = self.merge_if_same('uid', other)
        self.gid = self.merge_if_same('gid', other)
        self.password = self.merge_if_same('password', other)
        self.password_hash = self.merge_if_same('password_hash', other)

        # The passwords are an edge case
        if self.password and self.password_hash:
            raise DefinitionConflictError("Both password and password-hash defined after merge")

        # Merge lists
        if self.extra_groups or other.extra_groups:
            if not self.extra_groups:
                self.extra_groups = []
            if not other.extra_groups:
                other.extra_groups = []
            self.extra_groups = list(set(self.extra_groups) | set(other.extra_groups))
        self.after = list(set(self.after) | set(other.after))

        return self

    def get_config_state(self):
        result = {
            'exists': self.ensure == 'exists',
            'shell': self.shell,
        }
        if self.password:
            result['password'] = self._hash_password(self.password)
        if self.password_hash:
            result['password'] = self.password_hash
        if self.comment:
            result['comment'] = self.comment
        if self.uid:
            result['uid'] = self.uid
        if self.gid:
            result['gid'] = self.gid
        if self.homedir:
            result['homedir'] = self.homedir
        if self.extra_groups:
            result['groups'] = self.extra_groups

        return result

    def get_system_state(self):
        try:
            name, passwd, uid, gid, comment, homedir, shell = pwd.getpwnam(self.name)

            return {
                'exists': True,
                'uid': uid,
                'gid': gid,
                'comment': comment,
                'homedir': homedir,
                'shell': shell,
                'password': spwd.getspnam(self.name)[1],
                'groups': self._get_existing_groups()
            }

        except KeyError:
            return {
                'exists': False
            }

    def update_state(self, state_diff):
        diff = state_diff.changed_keys()

        if 'exists' in diff:
            if self.ensure == 'exists':
                self._useradd()
            else:
                self._userdel()
        else:
            if 'groups' in diff:
                existing_groups = self._get_existing_groups()
                wanted_groups = set(self.extra_groups)

                for group in wanted_groups - existing_groups:
                    command = ['usermod', '-A', '-g', group, self.name]
                    subprocess.check_call(command)

                for group in existing_groups - wanted_groups:
                    command = ['deluser', self.name, group]
                    subprocess.check_call(command)

            if 'shell' in diff:
                self._chsh()

    def _get_existing_groups(self):
        return set([g.gr_name for g in grp.getgrall() if self.name in g.gr_mem])

    def _hash_password(self, password):
        return crypt.crypt(password)

    def _useradd(self):
        command = ['useradd', '--shell', self.shell]
        if self.gid:
            command.extend(['--gid', str(self.gid)])
        if self.extra_groups:
            command.extend(['--groups', ','.join(self.extra_groups)])
        if self.uid:
            command.extend(['--uid', str(self.uid)])
        if self.homedir:
            command.extend(['--home', self.homedir])
        if self.comment:
            command.extend(['--comment', self.comment])
        if self.password_hash:
            command.extend(['--password', self.password_hash])
        if self.password:
            command.extend(['--password', self._hash_password(self.password)])
        if self.manage_home:
            command.append('--create-home')

        subprocess.check_call(command)

    def _userdel(self):
        if self.manage_home:
            subprocess.check_call(['userdel', '-r', self.name])
        else:
            subprocess.check_call(['userdel', self.name])

    def _chsh(self):
        command = ['chsh', self.name, '-s', self.shell]
        subprocess.check_call(command)
