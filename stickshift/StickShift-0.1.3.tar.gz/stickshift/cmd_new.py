import click

try:
    from stickshift.shell import pass_context
    from stickshift.cli_strings import CLIStrings
except ImportError:
    from shell import pass_context
    from cli_strings import CLIStrings


@click.command('new', short_help='Creates a migration script for creating a new table or procedure')
@click.argument('type', required=True, type=click.STRING, metavar='<type>')
@click.argument('name', required=True, type=click.STRING, metavar='<name>')
@pass_context
def cli(ctx, type, name):

    if ctx.repository().is_repository_setup():
        if type == "table":
            ctx.repository().create_new_table_migration(name)
        elif type == "procedure":
            ctx.repository().create_new_procedure_migration(name)
    else:
        print(CLIStrings.DB_MIGRATION_REPOSITORY_MUST_BE_SETUP)
