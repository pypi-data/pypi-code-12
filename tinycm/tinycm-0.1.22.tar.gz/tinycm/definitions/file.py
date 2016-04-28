from tinycm import DefinitionConflictError, InvalidParameterError
from tinycm.basedefinition import BaseDefinition
from tinycm.backup import backup_file
import os
import grp
import pwd
import stat
import requests
from tinycm.utils import get_module_file


class FileDefinition(BaseDefinition):
    def init(self, type, contents, interpolate=False, encoding='utf-8', ensure='contents', permission_mask=None,
             owner=None, group=None):
        self.type = type
        self.contents = contents
        self.interpolate = interpolate
        self.encoding = encoding
        self.ensure = ensure
        self.permission_mask = permission_mask
        self.owner = owner
        self.group = group

        if self.type not in ['constant', 'http', 'template']:
            raise InvalidParameterError('Type not in [constant, http, template]')
        if self.ensure not in ['deleted', 'exists', 'contents']:
            raise InvalidParameterError('Ensure not in [deleted, exists, contents]')

        self._fetched_and_interpolated = False

    def try_merge(self, other):
        self.type = self.merge_if_same('type', other)
        self.contents = self.merge_if_same('contents', other)
        self.encoding = self.merge_if_same('encoding', other, 'utf-8')
        self.owner = self.merge_if_same('owner', other)
        self.group = self.merge_if_same('group', other)

        if self.permission_mask and other.permission_mask:
            perm_user, perm_group, perm_other = self.permission_mask.split()
            other_user, other_group, other_other = other.permission_mask.split()

            if perm_user != 'x' and other_user != 'x' and perm_user != other_user:
                raise DefinitionConflictError('Duplicate definition for user in permission-mask')
            if perm_group != 'x' and other_group != 'x' and perm_group != other_group:
                raise DefinitionConflictError('Duplicate definition for group in permission-mask')
            if perm_other != 'x' and other_other != 'x' and perm_other != other_other:
                raise DefinitionConflictError('Duplicate definition for other in permission-mask')

            if perm_user == 'x':
                perm_user = other_user
            if perm_group == 'x':
                perm_group = other_group
            if perm_other == 'x':
                perm_other = other_other

            self.permission_mask = ''.join([perm_user, perm_group, perm_other])
        if not self.permission_mask:
            self.permission_mask = other.permission_mask

        return self

    def get_system_state(self):
        result = {
            'exists': os.path.isfile(self.name)
        }
        if result['exists']:
            if self.ensure == 'contents':
                with open(self.name) as input_file:
                    result['contents'] = input_file.read()

            file_info = os.stat(self.name)
            file_uid = file_info[stat.ST_UID]
            file_gid = file_info[stat.ST_GID]

            result['owner'] = file_uid
            result['group'] = file_gid
            result['permission-mask'] = str(oct(file_info[stat.ST_MODE]))[-3:]

        return result

    def get_config_state(self):
        self._ensure_contents()
        result = {
            'exists': os.path.isfile(self.name)
        }
        if result['exists']:
            if self.ensure == 'contents':
                result['contents'] = self.contents
            if self.owner:
                result['owner'] = self.owner
            if self.group:
                result['group'] = self.group
            if self.permission_mask:
                result['permission-mask'] = self.permission_mask
        return result

    def update_state(self, state_diff):
        diff = state_diff.changed_keys()
        exists = os.path.isfile(self.name)

        if 'exists' in diff:
            if self.ensure == 'removed':
                os.remove(self.name)
            elif self.ensure == 'exists' and not exists or self.ensure == 'contents':
                self._ensure_contents()
                with open(self.name, 'w') as target_file:
                    target_file.write(self.contents)

        if 'contents' in diff:
            self._ensure_contents()
            backup_file(self.name)
            with open(self.name, 'w') as target_file:
                target_file.write(self.contents)

        if 'owner' in diff or 'group' in diff or 'permission-mask' in diff:
            self._execute_permissions()

    def _ensure_contents(self):
        if self._fetched_and_interpolated:
            return

        if self.type == 'http':
            url = self.contents
            response = requests.get(url)
            self.contents = response.content.decode(self.encoding)

        if self.type == 'template':
            url = get_module_file(self.contents)
            response = requests.get(url)
            self.contents = response.content.decode(self.encoding)

        if self.interpolate:
            self.contents = self.contents.format(**self.context)

        self._fetched_and_interpolated = True

    def _execute_permissions(self):
        mask, uid, gid = self._get_file_perms()

        if self.owner:
            if isinstance(self.owner, int):
                uid = self.owner
            else:
                uid = pwd.getpwnam(self.owner).pw_uid

        if self.group:
            if isinstance(self.group, int):
                gid = self.group
            else:
                gid = grp.getgrnam(self.group).gr_gid

        if self.permission_mask:
            mask = self._merge_permission_mask(mask, self.permission_mask)

        os.chown(self.name, uid, gid)
        os.chmod(self.name, self._oct_to_dec(int(mask)))

    def _merge_permission_mask(self, mask1, mask2):
        mask1 = list(mask1)
        for i in range(0, 3):
            if mask2[i] != 'x':
                mask1[i] = mask2[i]

        return ''.join(mask1)

    def _get_file_perms(self):
        file_info = os.stat(self.path)
        file_uid = file_info[stat.ST_UID]
        file_gid = file_info[stat.ST_GID]
        file_mask = str(oct(file_info[stat.ST_MODE]))[-3:]
        return file_mask, file_uid, file_gid

    def _oct_to_dec(self, input_number):
        return sum(int(digit) * (8 ** power) for power, digit in enumerate(str(input_number)[::-1]))
