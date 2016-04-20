import click
from json import dumps

@click.group('task')
@click.pass_context
def cli(ctx):
    pass

@cli.command(name='list')
@click.option('--type', '-t', default='active', type=click.Choice(['scheduled', 'lbcleanup', 'cleaning', 'active']), help='Request type to get')
@click.option('--slave-id', '-s', help='Slave id')
@click.option('--json', '-j', is_flag=True, help='Enable json output')
@click.pass_context
def get_tasks(ctx, type, slave_id, json):
    res = ctx.obj['client'].get_tasks(type, slave_id)
    click.echo(dumps(res, indent=2))