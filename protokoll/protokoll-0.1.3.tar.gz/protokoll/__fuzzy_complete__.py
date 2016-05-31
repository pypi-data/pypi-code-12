"""
Adds support for fuzzy completion to click.
"""

import click

class FuzzyGroup(click.Group):
    """
    Class to convert partial commands into unique ones.
    """

    def get_command(self, ctx, cmd_name):
        """
        Return a unique command based on a partial string.
        If the command is not unique, the context will fail.

        :param ctx: Click context
        :type ctx: click.Context
        :param cmd_name: The command which should be matched.
        :type cmd_name: str
        :return: A unique command, or None if there are no matches.
        """
        click.echo('here')
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            click.echo('there')
            return rv
        click.echo('everywhere')
        matches = [x for x in self.list_commands(ctx)
                   if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        click.echo('everythere')
        ctx.fail('Too many matches: %s' % ', '.join(sorted(matches)))
