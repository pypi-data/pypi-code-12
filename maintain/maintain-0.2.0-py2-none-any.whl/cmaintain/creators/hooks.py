import os
import subprocess
from contextlib import contextmanager
import six
from maintain.creators.base import Creator, ValidationError



@contextmanager
def chdir(path):
    current = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(current)


class HookCreator(Creator):
    name = 'hooks'

    def __str__(self):
        pre = self.hooks_named('pre_create')
        create = self.hooks_named('create')
        post = self.hooks_named('post_create')

        description = []
        if pre:
            description.append('pre')

        if create:
            description.append('create')

        if pre:
            description.append('pre')

        return 'hooks ({})'.format(', '.join(description))

    def hooks_named(self, key):
        hooks = self.config['hooks.' + key]

        if isinstance(hooks, six.string_types):
            return [hooks]
        elif isinstance(hooks, list):
            return hooks

        return []

    def pre_create(self):
        map(self.invoke, self.hooks_named('pre_create'))

    def create(self):
        map(self.invoke, self.hooks_named('create'))

    def post_create(self):
        map(self.invoke, self.hooks_named('post_create'))

    def invoke(self, command):
        with chdir(self.destination):
            result = subprocess.check_call(command.format(name=self.destination), shell=True)

