# -*- coding: utf-8 -*-

import types

import git
import radon.complexity

from pychurn import utils

def get_complexity(path, until=None, include=(), exclude=()):
    repo = git.Repo(path)
    params = utils.filter_items(lambda x: x, until=until)
    commits = repo.iter_commits(**params)
    commit = next(commits)
    for blob in utils.iter_blobs(commit.tree):
        if not utils.check_path(blob.name, include, exclude):
            continue
        source = utils.git_show(repo, commit, blob.path)
        if source is None:
            continue
        try:
            visitor = radon.complexity.ComplexityVisitor.from_code(source)
        except SyntaxError:
            continue
        for node in visitor.classes:
            yield (
                utils.Node(blob.path, type, node.name, None),
                node.real_complexity,
            )
            for child in visitor.functions:
                yield (
                    utils.Node(blob.path, types.MethodType, child.name, node.name),
                    child.complexity,
                )
        for node in visitor.functions:
            yield (
                utils.Node(blob.path, types.FunctionType, node.name, None),
                node.complexity,
            )
