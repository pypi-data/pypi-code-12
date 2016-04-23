"""Command line interface to hitchsystem."""
from click import command, group, argument, option, echo
from hitchsystem.utils import log, warn, signals_trigger_exit, get_hitch_directory
from os import path
from sys import exit
import unixpackage
import itertools
import signal
import pip


def _hitchpackage_specified_packages():
    """Get a list of all required packages from this hitch environment."""

    # Get a list of all UNIXPACKAGES lists from installed packages starting with 'hitch'
    packages = []
    for name in [dist.key for dist in pip.get_installed_distributions()]:
        if name.startswith("hitch"):
            module = __import__(name)

            if hasattr(module, 'UNIXPACKAGES'):
                packages.extend(module.UNIXPACKAGES)

    # Return a de-deuplicated list
    return list(set(packages))


def _specified_system_packages():
    """Get a list of all system packages specified in the system.packages reqs file."""
    systempackages = path.join(get_hitch_directory(), "..", "system.packages")
    if path.exists(systempackages):
        return unixpackage.parse_requirements_file(systempackages)
    else:
        return []


def _all_required_packages():
    """All system packages specified in system.packages and hitch packages and base reqs."""
    return list(set(
            _specified_system_packages() + \
            _hitchpackage_specified_packages() + \
            [
                "python-dev",
                "python3-dev",
                "libtool",
                "automake",
                "cmake",
                "rsync",
                "libncurses5-dev",
                "aria2",
                "libzmq",
                "g++",
            ]
        ))


@group()
def cli():
    """System tools for hitch."""
    pass


@command()
def installpackages():
    """Install all system packages required by this environment to run."""
    try:
        unixpackage.install(_all_required_packages(), polite=True)
    except unixpackage.exceptions.UnixPackageException as error:
        echo(error)
        exit(1)



@command()
def freezepackages():
    """List all system packages required by this environment to run."""
    echo("\n".join(_all_required_packages()))


@command()
def packagecommand():
    """Show command needed to run to install all system packages required by environment."""
    echo(unixpackage.install_command(_all_required_packages()))


def run():
    """Run hitch system CLI"""
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    signal.signal(signal.SIGQUIT, signal.SIG_IGN)

    cli.add_command(installpackages)
    cli.add_command(freezepackages)
    cli.add_command(packagecommand)
    cli()


if __name__ == '__main__':
    run()
