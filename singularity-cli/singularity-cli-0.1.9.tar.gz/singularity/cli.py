import click
import json
import os
import requests
from singularity import client
import sys

cmd_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), 'commands'))

class MultiCommandCLI(click.MultiCommand):

    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(cmd_folder):
            if filename.endswith('.py') and filename.startswith('cmd_'):
                rv.append(filename[4:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            if sys.version_info[0] == 2:
                name = name.encode('ascii', 'replace')
            mod = __import__('singularity.commands.cmd_' + name, None, None, ['cli'])
        except ImportError:
            return
        return mod.cli

@click.command(cls=MultiCommandCLI)
@click.option('--host', '-h', envvar='SINGULARITY_HOST', default='http://localhost:7099', help='Singularity host url')
@click.option('--insecure', '-k', is_flag=True, envvar='SINGULARITY_INSECURE', help='Allow connections to SSL sites without certs (H)')
@click.version_option()
@click.pass_context
def cli(ctx, host, insecure):
    """Opinionated CLI for Singularity PAAS"""
    ctx.obj = {'client': client.Client(host, insecure)}
    

# TODO: singularity history api
# TODO: singularity logs api
# TODO: singularity racks api
# TODO: singularity sandbox api
# TODO: singularity slaves api
# TODO: singularity tasks api
# TODO: singularity test api
# TODO: singularity webhooks api
