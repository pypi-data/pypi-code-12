import argparse
import sys

from .create_command import CreateCommand
from .init_command import InitCommand
from .make_command import MakeCommand
from .sync_command import SyncCommand
from .rollback_command import RollbackCommand


def get_command(command):
    """
    Let's be dynamic
    :return: command
    """
    commands = {'create': CreateCommand, 'init': InitCommand, 'make': MakeCommand, 'sync': SyncCommand,
                'rollback': RollbackCommand}
    return commands.get(command, None)


def parse_args(args):
    """
    解析命令行参数
    :param args: command line arguments
    :return: arguments
    """
    parser = argparse.ArgumentParser(description="A simple database migration tool")

    subparsers = parser.add_subparsers(help="commands", dest="command")
    # create
    create_parser = subparsers.add_parser("create", help="Create a new project")
    create_parser.add_argument('dirname', action='store', default='.',
                               help="The directory to create your project. (default: %(default)s)")

    # init
    init_parser = subparsers.add_parser("init", help="Init your project")
    init_parser.add_argument("-e", "--env", action="store", default="dev",
                               choices=['dev', 'prod'],
                               help="the enviroment you want to control. (default: %(default)s)")

    # make
    make_parser = subparsers.add_parser("make", help="Make a new migration")
    make_parser.add_argument("description", action="store",
                             help="provide a description. (for example: create_user_table)")

    # sync
    sync_parser = subparsers.add_parser("sync", help="Synchronize migrations")
    sync_parser.add_argument("-e", "--env", action="store", default="dev",
                               choices=['dev', 'prod'],
                               help="the enviroment you want to control. (default: %(default)s)")

    # rollback
    rollback_parser = subparsers.add_parser("rollback", help="Rollback migration")
    rollback_parser.add_argument("-e", "--env", action="store", default="dev",
                               help="the enviroment you want to control. (default: %(default)s)")

    arguments = parser.parse_args(args)

    if arguments.command is None:
        print(parser.print_help())
        sys.exit(-1)

    return arguments


def main():
    """
    命令工具户主入口
    :return: None
    """
    arguments = parse_args(sys.argv[1:])

    Command = get_command(arguments.command)
    if Command is None:
        print("An error occurred", file=sys.stderr)
        sys.exit(-1)

    try:
        command = Command(arguments)
        command.run()
    except Exception as e:
        print("Error: ", sys.exc_info()[1])
