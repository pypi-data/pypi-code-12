# -*- coding: utf-8 -*-

import re
import fnmatch

import git

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

DIFF_RANGE = re.compile(
    r'''
        @@\s
        (?P<a_op>[+-])(?P<a_start>\d+)(?:,(?P<a_count>\d+))?
        \s
        (?P<b_op>[+-])(?P<b_start>\d+)(?:,(?P<b_count>\d+))?
        \s@@
    ''',
    re.VERBOSE,
)

def diff_lines(lines):
    for line in lines:
        match = DIFF_RANGE.search(line)
        if match:
            params = match.groupdict()
            start = int(params['b_start'])
            count = int(params['b_count'] or '1') or 1
            for line in range(start, start + count):
                yield line
