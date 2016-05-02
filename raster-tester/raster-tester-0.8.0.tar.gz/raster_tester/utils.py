#!/usr/bin/env python
import sys

import click

def exception_raiser(message, no_stderr):
    if no_stderr:
        click.echo("not ok - %s" % (message))
        sys.exit(0)
    else:
        raise ValueError(message)
