#!/usr/bin/env python

import os
import sys

import click

@click.command()
def cli():
    """Example script."""
    click.echo('Hello World!')