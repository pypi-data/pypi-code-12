#!/usr/bin/env python
# encoding: utf-8

import sys
import functools
import collections

import click
import tabulate

try:
    import ipdb as debugger
except ImportError:
    import pdb as debugger

try:
    from pychurn.gitsource.libgitsource import LibGitSource as GitSource
except:
    from pychurn.gitsource.pygitsource import PyGitSource as GitSource

from pychurn.complexity import get_complexity

def format_change(change):
    parts = [change.file, change.name]
    if change.parent:
        parts.insert(1, change.parent)
    return ':'.join(parts)

def apply_options(options, *keys):
    def wrapper(func):
        return functools.reduce(lambda memo, val: options[val](memo), keys, func)
    return wrapper

options = {
    'path': click.option(
        '--path', default='.', type=click.Path(), help='Path to git repo'),
    'sort': click.option(
        '--sort', default='churn', type=click.Choice(['churn', 'complexity']),
        help='Sort attribute'),
    'count': click.option('--count', default=20, type=click.INT, help='Max row count'),
    'include': click.option('--include', multiple=True, help='Include glob pattern'),
    'exclude': click.option('--exclude', multiple=True, help='Exclude glob pattern'),
    'since': click.option('--since', help='Begin commit date range'),
    'until': click.option('--until', help='End commit date range'),
}

@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    if debug:
        def hook(exc_type, exc_value, exc_tb):
            debugger.post_mortem(exc_tb)
        sys.excepthook = hook

@cli.command()
@apply_options(options, 'path', 'include', 'exclude', 'since', 'until')
def churn(**kwargs):
    changes = GitSource(**kwargs).churn()
    counts = collections.Counter(changes)
    table = [
        (format_change(change), count)
        for change, count in counts.most_common(20)
    ]
    print(tabulate.tabulate(table, headers=('code', 'count')))

@cli.command()
@apply_options(options, 'path', 'include', 'exclude', 'until')
def complexity(**kwargs):
    results = sorted(
        get_complexity(**kwargs),
        key=lambda pair: pair[1],
        reverse=True,
    )
    table = [
        (format_change(change), value)
        for change, value in results[:20]
    ]
    print(tabulate.tabulate(table, headers=('code', 'complexity')))

@cli.command()
@apply_options(options, 'path', 'sort', 'count', 'include', 'exclude', 'since', 'until')
def report(**kwargs):
    sort, count, since = kwargs.pop('sort'), kwargs.pop('count'), kwargs.pop('since')
    changes = GitSource(since=since, **kwargs).churn()
    counts = collections.Counter(changes)
    scores = dict(get_complexity(**kwargs))
    keys = set(counts.keys()) | set(scores.keys())
    merged = sorted(
        [
            (key, counts.get(key, 0), scores.get(key, 0))
            for key in keys
        ],
        key=lambda triple: triple[1 if sort == 'churn' else 2],
        reverse=True,
    )
    table = [
        (format_change(change), churn, complexity)
        for change, churn, complexity in merged[:count]
    ]
    print(tabulate.tabulate(table, headers=('code', 'churn', 'complexity')))

if __name__ == '__main__':
    cli()
