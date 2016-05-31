import click
import os
import re


def directory(ctx, param, value):
    if value is not None and not os.path.isdir(value):
        raise click.BadParameter('path is not a directory')
    elif not value.startswith('/'):
        raise click.BadParameter('path must be an absolute path')
    return value


def mysql_databases(ctx, param, value):
    if value == '*' or value is None:
        databases = []
    else:
        databases = re.findall(r'[\w_-]+', value)
        if len(databases) == 0:
            raise click.BadParameter('incorrect value')
    return databases


def postgresql_databases(ctx, param, value):
    if value == '*' or value is None:
        databases = []
    else:
        databases = re.findall(r'[\w_-]+', value)
        if len(databases) == 0:
            raise click.BadParameter('incorrect value')
    return databases
