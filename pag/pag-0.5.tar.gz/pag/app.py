#!/usr/bin/env python

import click

@click.group()
def app():
    pass

__all__ = [
    'app',
]

from .commands import create
from .commands import clone
from .commands import fork
from .commands import remote
from .commands import pullrequest


if __name__ == '__main__':
    app()
