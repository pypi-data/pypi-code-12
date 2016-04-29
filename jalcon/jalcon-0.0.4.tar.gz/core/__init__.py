from core.commands import *

def execute_from_command_line(argv=None):
    """
    A simple method that runs something from command line.
    argv[1] is the command
    argv[2] is the remaining command or project name
    """
    if argv[1] == 'createproject':
        createproject(argv[2])
