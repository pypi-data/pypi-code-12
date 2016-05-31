import click
from ubackup.cli import validators
from ubackup.backup.mysql import MysqlBackup
from ubackup.cli.utils import ask_for_rev


option = click.option(
    '--databases',
    help='List of MySQL databases you want to backup/restore, "*" for all.',
    callback=validators.mysql_databases)


@click.command()
@click.pass_context
@option
def backup(ctx, databases):
    ctx.obj['manager'].push_backup(MysqlBackup(databases=databases))


@click.command()
@click.pass_context
@option
def restore(ctx, databases):
    backup = MysqlBackup(databases=databases)

    revisions = ctx.obj['manager'].get_revisions(backup)
    rev = ask_for_rev(revisions)

    ctx.obj['manager'].restore_backup(backup, rev)
