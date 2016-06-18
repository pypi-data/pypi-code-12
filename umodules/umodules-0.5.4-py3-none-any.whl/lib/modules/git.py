import os
import shutil
import stat

from progress.bar import Bar

import git
from umodules.lib.module import IModule


class ModuleGit(IModule):

    def __init__(self):
        self.name = 'git'

    def init(self):
        super().init()

    def install(self, project):
        super().install(project)


class Progress(git.remote.RemoteProgress):

    @staticmethod
    def line_dropped(line):
        pass

    def update(self, *args):
        pass



def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def test():
    url = 'git@gitlab.com:kozmicblue/kozmicblue.git'
    repo_dir = 'git_test'
    branch = 'develop'

    git_progress = Progress()

    bar = Bar('Processing', max=5)

    for i in range(5):
        bar.next()
        if os.path.exists(repo_dir):
            shutil.rmtree(repo_dir, onerror=remove_readonly)
        git.Repo.clone_from(url, repo_dir, branch=branch, recursive=True, progress=git_progress)

    bar.finish()
