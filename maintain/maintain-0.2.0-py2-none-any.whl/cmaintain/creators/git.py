import os
import subprocess
from maintain.creators.base import Creator


class GitCreator(Creator):
    name = 'git'

    def create(self):
        self.git('init')

    def post_create(self):
        self.git('add', '.')
        self.git('commit', '-m', 'Initial project')

        if self.git('config', 'remote.origin.url'):
            self.git('push', '-u', 'origin', 'master')

    def git(self, *arguments):
        git_dir = os.path.join(self.destination, '.git')
        work_tree = self.destination

        stdout = open(os.devnull, 'w')
        result = subprocess.call([
            'git',
            '--git-dir={}'.format(git_dir),
            '--work-tree={}'.format(work_tree)
        ] + list(arguments), stdout=stdout) == 0
        stdout.close()
        return result
