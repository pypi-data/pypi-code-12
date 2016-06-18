"""
This file contains the `cli` function as well as any related classes
necessary for running `sdep` from the command line.

We build our cli with [click](http://click.pocoo.org/5/).
"""

# pylint: disable=import-error

import sys

import click

from .app import Sdep
from .config import Config, ConfigParseError

CONFIG_HELP = "The configuration file to use."
TEST_HELP = "Set this option if testing `cli`. Nothing will execute."

class Actions(object):
    """
    An enumeration of the different actions `sdep` can take.
    """
    # pylint: disable=too-few-public-methods
    CREATE = "create"
    UPDATE = "update"

@click.command()
@click.argument('action')
@click.option("--config", help=CONFIG_HELP)
@click.option("--test/--no-test", help=TEST_HELP, default=False)
def cli(action, config, test):
    """
    This function specifies the command line interface.

    Args:
        action (str): Which action, (create|update) we want `sdep` to take.
        config (str): The path to our configuration file.
    """
    poss_actions = [Actions.CREATE, Actions.UPDATE]

    if action not in poss_actions:
        # @TODO Specify the method to use for returning with an error.
        click.echo("Error not specified.", err=True)
        sys.exit(1)

    else:
        if test:
            click.echo("Running {0}".format(action))
        else:
            try:
                if config is not None:
                    configuration = Config(config_file=config)
                else:
                    configuration = Config()

            except ConfigParseError:
                click.echo("Error generating configuration.", err=True)
                sys.exit(1)

            sdep = Sdep(config=configuration)

            if action == Actions.CREATE:
                sdep.create()
            elif action == Actions.UPDATE:
                sdep.update()

def main():
    """
    The `main` function will be run when we execute `$ sdep create...` from the
    terminal.
    """
    # pylint: disable=no-value-for-parameter
    cli()
