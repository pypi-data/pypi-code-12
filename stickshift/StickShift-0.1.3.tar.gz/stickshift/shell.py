import os
import sys
import click
try:
    from stickshift.migration_repository import MigrationRepository
    from stickshift.database_manager import DatabaseManager
except ImportError:
    from migration_repository import MigrationRepository
    from database_manager import DatabaseManager

cmd_folder = os.path.abspath(os.path.dirname(__file__))


class ShellContext(object):

    def __init__(self):
        self.verbose = False
        self.directory = ""

    def log(self, msg, *args):
        """Logs a message to stderr."""
        if args:
            msg %= args
        click.echo(msg, file=sys.stderr)

    def vlog(self, msg, *args):
        """Logs a message to stderr only if verbose is enabled."""
        if self.verbose:
            self.log(msg, *args)

    def repository(self):
        return MigrationRepository(directory=self.directory) if self.directory else MigrationRepository()

    def database_manager(self, environment):
        return DatabaseManager(migration_repository=self.repository(), environment=environment)

pass_context = click.make_pass_decorator(ShellContext, ensure=True)


class ShellCLI(click.MultiCommand):

    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(cmd_folder):
            if filename.endswith('.py') and \
                    filename.startswith('cmd_'):
                rv.append(filename[4:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            if sys.version_info[0] == 2:
                name = name.encode('ascii', 'replace')
            mod = __import__("stickshift.cmd_" + name, fromlist=['cli'])
        except ImportError as error:
            return
        return mod.cli
