#!/usr/bin/env python
# from git.config import GitConfigParser
from gitconfigparser import GitConfigParser
from conf import Conf
from fullpath import fullpath
from public import public


@public
class GitConfig(Conf):
    read_only = False

    def __init__(self, path, read_only=False):
        self.read_only = read_only
        path = fullpath(path)
        parser = GitConfigParser(path, read_only=self.read_only)
        Conf.__init__(self, path=path, parser=parser)

    def write(self):
        self.parser.write()

gitconfig = GitConfig("~/.gitconfig", True)
public(gitconfig)
