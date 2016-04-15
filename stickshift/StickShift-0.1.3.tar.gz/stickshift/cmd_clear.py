import click

try:
    from stickshift.shell import pass_context
    from stickshift.cli_strings import CLIStrings
except ImportError:
    from shell import pass_context
    from cli_strings import CLIStrings


@click.command('clear', short_help='Clears out a repo.')
@pass_context
def cli(ctx):

    if ctx.repository().clear():
        ctx.log(CLIStrings.DB_MIGRATION_REPOSITORY_CLEARED)
    else:
        ctx.log(CLIStrings.DB_MIGRATION_REPOSITORY_DOESNT_EXIST_AT_DIRECTORY)
