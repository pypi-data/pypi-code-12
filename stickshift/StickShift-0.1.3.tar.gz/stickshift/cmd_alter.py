import click

try:
    from stickshift.shell import pass_context
except ImportError:
    from shell import pass_context


@click.command('new', short_help='Creates a migration script for creating a new table or procedure')
@click.argument('tablename', required=True, type=click.STRING, metavar='<tablename>')
@click.argument('tablechange', required=True, type=click.STRING, metavar='<tablechange>')
@pass_context
def cli(ctx, tablename, tablechange):

    if ctx.repository().is_repository_setup():
        ctx.repository().create_new_table_alteration_migration(name="{0}_{1}".format(tablename, tablechange))
    else:
        ctx.log("Migration Repository must be setup before creating migration scripts")
