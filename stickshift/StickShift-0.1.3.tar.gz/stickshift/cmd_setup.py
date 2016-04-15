import click

try:
    from stickshift.shell import pass_context
    from stickshift.cli_strings import CLIStrings
except ImportError:
    from shell import pass_context
    from cli_strings import CLIStrings


@click.command('setup', short_help='Initializes a repo.')
@pass_context
def cli(ctx):

    if ctx.repository().create_repository():
        ctx.log(CLIStrings.DB_MIGRATION_REPOSITORY_CREATED)
    else:
        ctx.log(CLIStrings.DB_MIGRATION_REPOSITORY_ALREADY_CREATED)
