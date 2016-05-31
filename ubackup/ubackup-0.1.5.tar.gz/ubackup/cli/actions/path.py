import click
from ubackup.cli import validators
from ubackup.backup.path import PathBackup
from ubackup.cli.utils import ask_for_rev


option = click.option(
    '--path',
    help='Absolute path of the backup you want to create/restore.',
    callback=validators.directory,
    required=True)


@click.command()
@click.pass_context
@option
def backup(ctx, path):
    ctx.obj['manager'].push_backup(PathBackup(path=path))


@click.command()
@click.pass_context
@option
def restore(ctx, path):
    backup = PathBackup(path=path)

    revisions = ctx.obj['manager'].get_revisions(backup)
    rev = ask_for_rev(revisions)

    ctx.obj['manager'].restore_backup(backup, rev=rev)
