# -*- coding: utf-8 -*-

import re
import calendar
from collections import namedtuple

import pygit2
from dateutil.parser import parse as parse_date

from pychurn import utils
from pychurn.gitsource import gitsource

Diff = namedtuple('Diff', ['lines', 'a_path', 'b_path'])
DIFF_LINE = re.compile(r'^diff --git a\/(?P<a>.*) b\/(?P<b>.*)$')

def convert_date(value):
    if value is not None:
        date = parse_date(value)
        return calendar.timegm(date.timetuple())

class LibGitSource(gitsource.GitSource):

    def get_repo(self, path):
        return pygit2.Repository(path)

    def iter_commits(self):
        since, until = convert_date(self.since), convert_date(self.until)
        for commit in self.repo.walk(self.repo.head.target, pygit2.GIT_SORT_TIME):
            if len(commit.parents) != 1:
                continue
            if since is not None and commit.commit_time <= since:
                continue
            if until is not None and commit.commit_time > until:
                break
            yield commit

    def get_diffs(self, commit):
        diff = self.repo.diff(commit.parents[0], commit, context_lines=0)
        lines = diff.patch.splitlines()
        pairs = [(line, DIFF_LINE.match(text)) for line, text in enumerate(lines)]
        pairs = [pair for pair in pairs if pair[1]]
        pairs.append((len(lines), None))
        for idx, (line, match) in enumerate(pairs[:-1]):
            groups = match.groupdict()
            next_line, _ = pairs[idx + 1]
            yield Diff(
                lines=lines[line:next_line],
                a_path=groups['a'],
                b_path=groups['b'],
            )

    def get_path(self, diff):
        return diff.b_path

    def get_changes(self, diff):
        return set(utils.diff_lines(diff.lines))

    def get_source(self, commit, path):
        try:
            entry = commit.tree[path]
            blob = self.repo.get(entry.id)
            return blob.read_raw()
        except (KeyError, AttributeError):
            return None
