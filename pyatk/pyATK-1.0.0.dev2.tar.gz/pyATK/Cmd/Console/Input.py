import getopt
from pyATK.Cmd.Console.InputOption import InputOption
from pyATK.Cmd.Console.InputArgument import InputArgument
from pyATK.Cmd.Helpers.ArgumentsHelper import ArgumentsHelper
from pyATK.Cmd.Base.MissingArgumentException import MissingArgumentException


class Input:

    HELP_REQUIRED = 0x01

    def __init__(self):
        self.argumentsHelper = ArgumentsHelper(self)
        self.arguments = []
        self.options = []

    def getArgument(self, argName):
        return self.argumentsHelper.argument(argName).value

    def registerArgument(self, argument):
        self.arguments.append(argument)

    def getOption(self, optName):
        return self.argumentsHelper.option(optName).value

    def registerOption(self, option):
        self.options.append(option)

    def validate(self):
        for argument in self.arguments:
            if argument.valueRequired == InputArgument.ARGUMENT_REQUIRED and argument.value is None:
                raise MissingArgumentException('Missing value for ' + argument.name)

        for option in self.options:
            if option.optionRequired == InputOption.OPTION_REQUIRED and option.value is None:
                raise MissingArgumentException('Missing value for ' + option.name)

    def parse(self, cli_args):
        opts, args = getopt.getopt(cli_args, self.getShortFormString(),
                                   self.getLongFormString())

        for opt, value in opts:
            if opt in ["-h", "--help"]:
                return self.HELP_REQUIRED
            for couple in self.argumentsHelper.getOptionCouples():
                if opt in couple:
                    self.argumentsHelper.option(opt).value = value
                    break

        index = 0
        for arg_val in args:
            self.arguments[index] = arg_val
            index += 1

        self.validate()


    def getShortFormString(self):
        result = ""
        for opt in self.options:
            if opt.optionRequired is InputOption.OPTION_NONE:
                result = result + opt.shortForm
            else:
                result = result + opt.shortForm + ":"
        return result

    def getLongFormString(self):
        result = []
        for opt in self.options:
            if opt.optionRequired is InputOption.OPTION_NONE:
                result.append(opt.longForm)
            else:
                result.append(opt.longForm + "=")
        return result

