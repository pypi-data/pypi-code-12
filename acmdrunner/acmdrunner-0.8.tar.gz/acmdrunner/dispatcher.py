from .exceptions import (
    CommandAlreadyRegisteredException,
    CommandNotRegisteredException
)


class CommandDispatcher(object):

    __slots__ = ('registered_commands')

    def __init__(self):
        self.registered_commands = {}

    def register_command(self, name, callable_func_or_object):
        """Enables execution of the command with name `name`

        :param name: The name of the command
        :type name: string
        :param callable_func_or_object: any callable
        :returns: None
        :rtype: None
        :raises acmdrunner.exceptions.CommandAlreadyRegisteredException: in
        case if command has been registered already
        """
        if name in self.registered_commands:
            raise CommandAlreadyRegisteredException(
                'command {} already registered'.format(name)
            )
        self.registered_commands[name] = callable_func_or_object

    def execute_command(self, name, *params, **param_kwargs):
        """Execute given command

        :param name: Name of the command to be executed
        :type name: string
        :returns: None
        :rtype: None
        :raises acmdrunner.exceptions.CommandNotRegisteredException: in case if
        such command is not registered yet
        """
        if name not in self.registered_commands:
            raise CommandNotRegisteredException(
                'command {} is not loaded yet'.format(name)
            )
        self.registered_commands[name](*params, **param_kwargs)

    def is_registered(self, name):
        """Is exists given command

        :param name: Name of the command
        :type name: string
        :returns: None
        :rtype: None
        """
        return name in self.registered_commands

    def list_all_commands(self):
        """Prints all registered commands to stdout
        :returns: None
        :rtype: None
        """
        print("\n".join(self.registered_commands.keys()))
