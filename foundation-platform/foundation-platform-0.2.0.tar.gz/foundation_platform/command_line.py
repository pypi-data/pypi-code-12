import argparse
from collections import OrderedDict
from foundation_platform.common import error
from foundation_platform.csar import csar
import os
from traceback import format_exc


class NoSuchCommand(error.Error):
    """
    Exception raised when trying to add parameters to a non-existent command.

    :param value: the command that was asked for but not found.
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Commands(OrderedDict):
    """
    The Commands object simply creates an ordered dictionary.

    It contains a set of commands
    that will ultimately be used to create an argparse parser.  The commands are added with
    a pointer to a function the will be used to provide the desired functionality.  Commands
    may have parameters that include help text and may be optional or required.
    """

    def __init__(self):
        super(Commands, self).__init__()

    def add_command(self, command, cmd_help):
        """
        Add a new command to the list of commands we know about

        :param command: command name to be added
        :type command: str
        :param cmd_help: help text for the command
        :type cmd_help: str or unicode
        :return: None
        """

        self[command] = OrderedDict({'help': cmd_help})
        self[command]['params'] = OrderedDict()

    def add_param(self, command, param, param_help, required=True):
        """
        Adds a new parameter to a command

        :param str command: command to add the parameter to
        :param str param: parameter being added to the command
        :param param_help: help text for the parameter
        :type param_help: str or unicode
        :param bool required: is the parameter required (default is True)
        :raises NoSuchCommand: thrown when adding a parameter to a non-existing command
        :return: None
        """

        if not self[command]:
            raise Exception(NoSuchCommand, command)
        self[command]['params'][param] = OrderedDict()
        self[command]['params'][param]['help'] = param_help
        self[command]['params'][param]['required'] = required

    def get_command_help(self, command):
        """
        Return the help string for a given command

        :type command: str
        :return: help string for the command :rtype: str
        """

        try:
            return self[command]['help']
        except KeyError:
            raise(NoSuchCommand, command)

    def get_param_help(self, command, param):
        """
        Return the help string for a given parameter of a command

        :param command: command whose parameter we want to know about
        :type command: str
        :param param: parameter for the command whose help string we want
        :type param: str
        :return: help string for the parameter
        :rtype: str
        """

        try:
            return self[command]['params'][param]['help']
        except KeyError:
            raise(NoSuchCommand, command + " " + param)

    def param_required(self, command, param):
        """
        Return whether a given parameter for a command is required or optional

        :param command: command whose parameter we want to know about
        :type command: str
        :param param: parameter for teh command whose optionality we want
        :type param: str
        :return: True if the parameter is required, else False
        :rtype: bool
        """

        try:
            return self[command]['params'][param]['required']
        except KeyError:
            raise(NoSuchCommand, command + " " + param)


class CsarParser(object):
    def __init__(self):
        """
        Create a parser for CSAR commands.  The commands, their help text, required parameters, etc

        are all in the __known_commands dictionary.
        :return: parser object for CSAR commands
        :rtype: CsarParser
        """

        self.__command = None
        self.__args = None
        self.__known_commands = self.__init_commands()
        self.__parser = self.__create_parser(self.__known_commands)

        # If we end up needing required parameters, they should be initialized here as
        # self.__some_name = None and then set from either the command line or environment
        # variables

    @staticmethod
    def __init_commands():
        """
        Initialize the set of commands that we know about.

        :return: commands we know about
        :rtype: Commands
        """

        # Create the list of commands that we know.
        #
        __cmds = Commands()

        try:
            # The create command will build a CSAR file
            __cmds.add_command('create', 'create a new CSAR file')
            __cmds.add_param('create',
                             'input',
                             'Full path for the input files location')
            __cmds.add_param('create',
                             'output',
                             'Full path for the CSAR  file output location')
            __cmds.add_param('create',
                             'name',
                             'CSAR name')
            __cmds.add_param('create',
                             'author',
                             'CSAR Author')
            __cmds.add_param('create',
                             'file_name',
                             'File name to store the CSAR in (default is ./name)',
                             required=False)
            __cmds.add_param('create',
                             'image',
                             'Input for image file name/names separated by commas',
                             required=False)
            __cmds.add_param('create',
                             'hot',
                             'Input for hot-template file name/names separated by commas',
                             required=False)
            __cmds.add_param('create',
                             'scripts',
                             'Input for hot-template file name/names separated by commas',
                             required=False)
            __cmds.add_param('create',
                             'other',
                             'Input for any other file name/names separated by comma',
                             required=False)

            # The load_file command will read a CSAR file and load it into a cloud catalog
            __cmds.add_command('load_file', 'load a CSAR file into a cloud catalog')
            __cmds.add_param('load_file',
                             'csar_file',
                             'full or relative CSAR file path')
            __cmds.add_param('load_file',
                             'html_dir',
                             'base directory that will serve HTML requests - must exist ' +
                             '(default = /var/www/html)',
                             required=False)
            __cmds.add_param('load_file',
                             'csar_target_dir',
                             'directory (relatie to html_dir) that the CSAR will ' +
                             'be unpacked to - will be created if it does not exist ' +
                             '(default = csar)',
                             required=False)

            # The load_url command will attempt to retrieve a CSAR from a URL and then load it
            # into a cloud catalog
            __cmds.add_command('load_url', 'load a CSAR from a URL into a cloud catalog')
            __cmds.add_param('load_url',
                             'csar_url',
                             'FQDN to retrieve the CSAR from')
            __cmds.add_param('load_url',
                             'html_dir',
                             'base directory that will serve HTML requests ' +
                             '(default = /var/www/html)',
                             required=False)
            __cmds.add_param('load_url',
                             'csar_target_dir',
                             'directory (relatie to html_dir) that the CSAR will ' +
                             'be unpacked to (default = csar)',
                             required=False)
        except NoSuchCommand as e:
            exit('internal error - tried to add param to non-existent command ' + e.value)

        return __cmds

    @staticmethod
    def __create_parser(cmds):
        """
        Create a parser from a set of commands, adding common options

        :param cmds: a set of commands to add to the parser
        :type cmds: Commands
        :return: parser for the commands
        :rtype: argparse.ArgumentParser
        """

        __parser = argparse.ArgumentParser("Process CSAR files")

        # Optional parameters for all subcommands.
        #
        __parser.add_argument("--version", action="version", version="foo")

        # Add the commands we know about and their options
        #
        __sub_parser = __parser.add_subparsers(dest='__command', help="subcommand help")
        try:
            for __cmd, __parms in cmds.items():
                __new_parser = __sub_parser.add_parser(__cmd, help=__parms['help'])
                if __parms['params']:
                    __new_group = __new_parser.add_argument_group(__cmd)
                    for __arg, __opts in __parms['params'].items():
                        if __opts['required']:
                            __new_group.add_argument(__arg, help=__opts['help'])
                        else:
                            __new_group.add_argument('--' + __arg, help=__opts['help'])
        except KeyError:
            __parser.error('internal error - invalid command structure')

        return __parser

#    def __load_env(self):
#        """Stub function.  If we need to import variables from the user's environment, that will
#        happen here.
#        :return:
#        """
#
#        return True

    def parse(self, args=None):
        """
        Parse command line arguments.

        In addition, pull in any environment variables - command
        line arguments take precedence over environment variables.
        :param args: optional argument string to parse (default is argv)
        :type args: str
        :return: True
        :rtype: bool
        """

        # self.__load_env()
        # noinspection PyBroadException
        try:
            if args:
                self.__args = vars(self.__parser.parse_args(args.split()))
            else:
                self.__args = vars(self.__parser.parse_args())
        except Exception:
            print(format_exc())
            self.__parser.exit(status=1, message='failed to parse command line')

        self.__command = self.__args['__command']

    @property
    def command(self):
        return self.__command

    @property
    def args(self):
        return self.__args


def main():
    try:
        parser = CsarParser()
        parser.parse()

        if parser.command == 'create':
            # Set the required parameters, then add the various optional inforamtion on scripts,
            # images, templates, etc, then create the CSAR.
            my_csar = csar.Csar(name=parser.args['name'],
                                input_dir=parser.args['input'],
                                output_dir=parser.args['output'],
                                author=parser.args['author'])
            if parser.args['file_name']:
                __output_file = parser.args['file_name']
            else:
                __output_file = "./" + parser.args['file_name']
            if parser.args['image']:
                for name in parser.args['image'].split(","):
                    my_csar.add_image(name)
            if parser.args['scripts']:
                for name in parser.args['scripts'].split(","):
                    my_csar.add_script(name)
            if parser.args['hot']:
                for name in parser.args['hot'].split(","):
                    my_csar.add_hot_template(name)
            my_csar.create(__output_file)
        elif parser.command == 'load_file':
            # If the html directory doesn't exist
            if parser.args['output_dir']:
                __output_directory = parser.args['output_dir']
            else:
                __output_directory = '/var/www/html'
            if parser.args['load_file']:
                __output_file = parser.args['load_file']
            else:
                __output_file = 'csar'
            __path = os.path.join(__output_directory, __output_file)
            try:
                os.mkdir(__path)
            except OSError as e:
                raise ('could not create output directory ' + __path + ' ' + str(e))

            my_csar = csar.Csar(input_file=parser.args['csar_file'],
                                output_dir=__path)
            my_csar.ingest()
        elif parser.command == 'load_url':
            my_csar = csar.Csar()
            my_csar.ingest()
        else:
            raise NoSuchCommand(parser.command)
    except KeyboardInterrupt:
        exit('caught keyboard interrupt - exiting')


if __name__ == "__main__":
    main()
