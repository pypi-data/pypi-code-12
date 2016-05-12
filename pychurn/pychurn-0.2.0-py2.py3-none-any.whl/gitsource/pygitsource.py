# -*- coding: utf-8 -*-

import git

from pychurn import utils
from pychurn.gitsource import gitsource

class PyGitSource(gitsource.GitSource):

    def get_repo(self, path):
        return git.Repo(path)

    def iter_commits(self):
        opts = {
            'min_parents': 1,
            'max_parents': 1,
            'since': self.since,
            'until': self.until,
        }
        opts = {key: value for key, value in opts.items() if value is not None}
        return self.repo.iter_commits(**opts)

    def get_diffs(self, commit):
        return commit.parents[0].diff(commit, create_patch=True, unified=0)

    def get_path(self, diff):
        return diff.b_path

    def get_changes(self, diff):
        lines = utils.decode(diff.diff).splitlines()
        return set(utils.diff_lines(lines))

    def get_source(self, commit, path):
        return utils.git_show(self.repo, commit, path)
