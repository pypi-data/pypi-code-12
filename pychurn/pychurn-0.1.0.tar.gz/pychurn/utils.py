# -*- coding: utf-8 -*-

import fnmatch
import collections

import git

Node = collections.namedtuple(
    'Node',
    ['file', 'type', 'name', 'parent'],
)

def match(path, patterns):
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)

def check_path(path, include=(), exclude=()):
    return (
        (not include or match(path, include)) and
        not match(path, exclude)
    )

def filter_items(predicate, **kwargs):
    return {
        key: value for key, value in kwargs.items()
        if predicate(value)
    }

def iter_blobs(tree):
    for blob in tree.blobs:
        yield blob
    for subtree in tree.trees:
        for blob in iter_blobs(subtree):
            yield blob

def git_show(repo, ref, path):
    try:
        return repo.git.show('{}:{}'.format(ref.hexsha, path))
    except (git.GitCommandError, UnicodeDecodeError):
        return None

def decode(value, encoding='utf-8'):
    try:
        return value.decode(encoding)
    except AttributeError:
        return value
