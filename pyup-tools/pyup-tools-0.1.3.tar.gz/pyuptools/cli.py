# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
from pkg_resources import parse_version
import click
import requests
from requests.exceptions import ConnectionError, ConnectTimeout
from pyuptools import __version__


@click.group()
@click.version_option(__version__, '-v', '--version')
def cli():  # pragma: no cover
    pass

@click.command()
@click.version_option(__version__, '-v', '--version')
@click.option('--server', prompt='Index Server', help='')
@click.option('--pkg', prompt='Package', help='')
def devpi(server, pkg):
    url = "".join([server, pkg]) if server.endswith("/") else "/".join([server, pkg])
    headers = {"Accept": "application/json"}
    click.secho("Requesting {}".format(url))
    try:
        r = requests.get(url, headers=headers)
    except (ConnectionError, ConnectTimeout):
        click.secho("Error: Unable to connect", fg="red")
        return

    try:
        json = r.json()
    except ValueError:
        click.secho("Error: Unable to parse JSON", fg="red")
        return

    try:
        versions = sorted(json["result"].keys(), key=lambda v: parse_version(v), reverse=True)
    except KeyError:
        click.secho("Error: The returned JSON contains no result.", fg="red")
        click.secho("Expected: {'result': {..}}, returned: %s" % json, fg="blue")
        return

    # filter out versions that are greater than 100 chars
    versions = [v for v in versions if len(v) < 100]
    click.secho("Success", fg="green")
    click.secho("Parsed versions: {}".format(versions))
cli.add_command(devpi)

if __name__ == '__main__':
    cli()
