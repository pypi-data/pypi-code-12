# -*- coding: utf-8 -*-

import re
import ast
import types
import itertools

import git

from pychurn import utils
from pychurn.parse import ChurnVisitor

pattern = re.compile(r'(?P<op>[+-])(?P<start>\d+)(?:,(?P<count>\d+))? @@')

def parse_diff_lines(diff):
    for line in utils.decode(diff.diff).splitlines():
        if not line.startswith('@@'):
            continue
        match = pattern.search(line)
        if match:
            params = match.groupdict()
            start, count = int(params['start']), int(params['count'] or 1)
            yield range(start, start + count)

def parse_diff(diff):
    return set(itertools.chain.from_iterable(parse_diff_lines(diff)))

def get_type(node):
    if isinstance(node, ast.ClassDef):
        return type
    assert isinstance(node, ast.FunctionDef)
    return types.MethodType if node.parent else types.FunctionType

def get_churn(path, since=None, until=None, include=(), exclude=()):
    repo = git.Repo(path)
    opts = {
        'min_parents': 1,
        'max_parents': 1,
        'since': since,
        'until': until,
    }
    opts = {key: value for key, value in opts.items() if value is not None}
    for commit in repo.iter_commits(**opts):
        diffs = commit.parents[0].diff(commit, create_patch=True, unified=0)
        for diff in diffs:
            if not utils.check_path(diff.b_path, include, exclude):
                continue
            changes = parse_diff(diff)
            source = utils.git_show(repo, commit, diff.b_path)
            if source is None:
                continue
            try:
                parsed = ast.parse(source)
            except SyntaxError:
                continue
            for node in ChurnVisitor.extract(parsed):
                if changes.intersection(range(node.lineno, node.lineno_end)):
                    yield utils.Node(
                        diff.b_path,
                        get_type(node),
                        node.name,
                        node.parent.name if node.parent else None,
                    )
