from tinycm.basedefinition import BaseDefinition
import os
import logging

logger = None


class LinkDefinition(BaseDefinition):
    def init(self, ensure, target):
        self.ensure = ensure
        self.target = target

        global logger
        logger = logging.getLogger('tinycm')

    def try_merge(self, other):
        self.ensure = self.merge_if_same('ensure', other)
        self.target = self.merge_if_same('target', other)
        return self

    def get_system_state(self):

        if not os.path.islink(self.name):
            return {
                'ensure': 'removed'
            }

        result = {
            'target': os.path.realpath(self.name),
            'ensure': 'symlink'
        }
        return result

    def get_config_state(self):
        if self.ensure == 'removed':
            return {
                'ensure': 'removed'
            }
        return {
            'target': self.target,
            'ensure': self.ensure
        }

    def update_state(self, state_diff):
        if 'ensure' in state_diff:
            if self.ensure == 'removed':
                os.remove(self.name)
            else:
                os.symlink(self.target, self.name)

        if 'target' in state_diff:
            os.remove(self.name)
            os.symlink(self.target, self.name)
