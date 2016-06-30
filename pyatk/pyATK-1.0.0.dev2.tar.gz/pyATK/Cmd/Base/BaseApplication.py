# -*- coding: utf-8 -*-
import sys
import getopt
from abc import ABCMeta

from pyATK.Cmd.Console.InputArgument import InputArgument
from pyATK.Cmd.Console.InputOption import InputOption
from pyATK.Cmd.Console.Input import Input
from pyATK.Cmd.Console.Output import Output
from pyATK.Cmd.Base.MissingArgumentException import MissingArgumentException


class BaseApplication(metaclass=ABCMeta):
    STATUS_SUCCESS = 0x0
    STATUS_FAILURE = 0x1

    def __init__(self):
        self.name = ""
        self.version = ""
        self.expectingOptions = False
        self.expectingArguments = False
        self.input = Input()
        self.output = Output()

        self.addOption('h', 'help', 'Displays this help message', InputOption.OPTION_NONE)
        self.addOption('q', 'quiet', 'Do not output any message', InputOption.OPTION_NONE)
        self.addOption('V', 'version', 'Displays this application version', InputOption.OPTION_NONE)
        self.addOption('v', 'verbose', 'Increase verbosity level of messages', InputOption.OPTION_NONE)

    def setName(self, name):
        self.name = name
        return self

    def setVersion(self, version):
        self.version = version
        return self

    def addOption(self, shortForm, longForm=None, description=None, optionRequired=InputOption.OPTION_NONE):
        self.input.registerOption(InputOption(shortForm, longForm, description, optionRequired))
        return self

    def addArgument(self, argumentName, description, valueRequired):
        self.input.registerArgument(InputArgument(argumentName, description, valueRequired))
        return self

    def getHelpMessage(self):
        msg = self.name
        if self.version != "":
            msg += ", version : " + self.version + "\n"
        else:
            msg += "\n"

        msg += "Usage:"

        argString = ""
        if len(self.input.arguments) == 1:
            argString = str(self.input.arguments[0])
        else:
            count = 0
            for arg in self.input.arguments:
                if count != len(self.input.arguments) - 1:
                    argString += str(arg) + " "
                else:
                    argString += str(arg)
                count += 1

        msg += self.name + "[OPTIONS] " + argString + "\n"
        msg += "Options:\n"
        for option in self.input.options:
            msg += str(option) + "\n"
        msg += "\n"
        return msg

    def run(self):
        try:
            if self.input.parse(sys.argv[1:]) == self.input.HELP_REQUIRED:
                print(self.getHelpMessage())
                sys.exit(self.STATUS_SUCCESS)
            else:
                self.doRun()
                sys.exit(self.STATUS_SUCCESS)

        except getopt.GetoptError as err:
            print(err)
            sys.exit(self.STATUS_FAILURE)

        except MissingArgumentException as err:
            print(err)
            sys.exit(self.STATUS_FAILURE)

        # except Exception as err:
        #     print(err)
        #     return self.STATUS_FAILURE

    def doRun(self):
        raise NotImplementedError("This method is not implemented!")
