# -*- coding: utf-8 -*-

import abc
import ast

import six

from pychurn import utils
from pychurn.parse import ChurnVisitor

class GitSource(six.with_metaclass(abc.ABCMeta, object)):

    def __init__(self, path, since=None, until=None, include=(), exclude=()):
        self.repo = self.get_repo(path)
        self.since = since
        self.until = until
        self.include = include
        self.exclude = exclude

    def churn(self):
        for commit in self.iter_commits():
            for path, parsed, changes in self.iter_changes(commit):
                for node in ChurnVisitor.extract(path, parsed, changes):
                    yield node

    def iter_changes(self, commit):
        for diff in self.get_diffs(commit):
            path = self.get_path(diff)
            if not utils.check_path(path, self.include, self.exclude):
                continue
            source = self.get_source(commit, path)
            try:
                parsed = ast.parse(source)
            except (TypeError, SyntaxError):
                continue
            changes = self.get_changes(diff)
            yield path, parsed, changes

    @abc.abstractmethod
    def iter_commits(self):
        pass

    @abc.abstractmethod
    def get_diffs(self, commit):
        pass

    @abc.abstractmethod
    def get_path(self, diff):
        pass

    @abc.abstractmethod
    def get_changes(self, diff):
        pass

    @abc.abstractmethod
    def get_source(self, commit, diff):
        pass
