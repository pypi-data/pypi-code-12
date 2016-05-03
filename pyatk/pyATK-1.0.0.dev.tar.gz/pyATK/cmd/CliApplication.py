# -*- coding: utf-8 -*-

import sys
import getopt
from pyATK.cmd.InputArgument import InputArgument
from pyATK.cmd.InputOption import InputOption
from pyATK.utils.misc import if_else


class CliApplication:

    STATUS_SUCCESS = 0x0
    STATUS_FAILURE = 0x1

    def __init__(self):
        self.options = []
        self.arguments = []
        self.setOptions = 0
        self.setArguments = 0
        self.name = sys.argv[0]
        self.version = "x.y.z"
        self.expectingOptions = False
        self.expectingArguments = False

        self.add_option("h", "help", "Displays this help message", InputOption.OPTION_NONE)

    def set_name(self, name):
        self.name = name

    def set_version(self, version):
        self.version = version

    def add_option(self, short_form, long_form=None, description=None, value_required=InputOption.OPTION_NONE):
        self.assert_valid_value_for_option(value_required)

        opt = InputOption(short_form, long_form, description, value_required)
        self.options.append(opt)
        if self.expectingOptions is False:
            self.expectingOptions = True
        return self

    def add_argument(self, argument_name, description, value_required):
        self.assert_valid_value_for_argument(value_required)
        
        arg = InputArgument(argument_name, description, value_required)
        self.arguments.append(arg)
        if self.expectingArguments is False:
            self.expectingArguments = True
        return self

    def get_value_for_option(self, option):
        for opt in self.options:
            if option in [opt.shortForm, opt.longForm]:
                return opt.value
        return None

    def usage(self):
        print(self.name + ", version : " + self.version)
        print("Usage:")

        print(self.name + if_else(self.expectingOptions == True, " [OPTIONS] ", "") + " ".join(self.arguments) + "\n")

        print("Options:\n")

        for option in self.options:
            print(option)
        print("")

    def run(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], self.get_short_form_string(), self.get_long_form_string())
        except getopt.GetoptError as err:
            print(err)
            sys.exit(1)

        for opt, arg in opts:
            if self.expectingOptions is False:
                print("Extra option(s) provided. Don't know what to do with that")
                self.usage()
                return CliApplication.STATUS_FAILURE
            if "-h" == opt or "--help" == opt:
                self.usage()
                return CliApplication.STATUS_SUCCESS
            for couple in self.get_option_couples():
                if opt in couple:
                    self.options[self.get_option_by_name(opt)].value = arg
                    self.setOptions += 1
                    break

        if self.expectingArguments is True and len(args) == 0:
            print("Not enough arguments provided")
            return CliApplication.STATUS_FAILURE
        else:
            index = 0
            for arg in args:
                if self.expectingArguments is False:
                    print("Extra argument(s) provided. Don't know what to do with that.")
                    self.usage()
                    return CliApplication.STATUS_FAILURE
                else:
                    self.arguments[index].value = arg
                    self.setArguments += 1
                    index += 1

        return self.do_run()

    def do_run(self):
        raise NotImplementedError("This method is not implemented!")

    #
    # Input methods
    #
    def confirm(self, question):
        print(question + " [Y/n]")
        response = input()
        if response.startswith("Y"):
            return True
        return False

    def choice(self, question, choices={}, message="Please select your choice"):
        keys = []
        for key, choice in choices:
            print("[" + str(key) + "] " + str(choice))
            keys.append(str(key))
        print(message)
        response = input()
        if response in keys:
            return response
        return None

    #
    # Utility methods
    #
    def get_short_form_string(self):
        result = ""
        for opt in self.options:
            if opt.valueRequired is InputOption.OPTION_NONE:
                result = result + opt.shortForm
            else:
                result = result + opt.shortForm + ":"

        return result

    def get_long_form_string(self):
        result = []
        for opt in self.options:
            if opt.valueRequired is InputOption.OPTION_NONE:
                result.append(opt.longForm)
            else:
                result.append(opt.longForm + "=")
        return result

    def get_option_couples(self):
        result = []
        for opt in self.options:
            result.append(["-" + opt.shortForm, "--" + opt.longForm])
        return result

    def get_option_by_name(self, name):
        for option in self.options:
            if name in ["-" + option.shortForm, "--" + option.longForm]:
                return self.options.index(option)
        raise Exception("Option " + name + " was not found")

    def assert_valid_value_for_option(self, value_required):
        if value_required not in [InputOption.OPTION_NONE, InputOption.OPTION_OPTIONAL, InputOption.OPTION_REQUIRED]:
            raise ValueError("Wrong value provided. Should be one of OPTION_REQUIRED, OPTION_OPTIONAL, OPTION_NONE")

    def assert_valid_value_for_argument(self, value_required):
        if value_required not in [InputArgument.ARGUMENT_OPTIONAL, InputArgument.ARGUMENT_REQUIRED]:
            raise ValueError("Wrong value provided. Should be one of ARGUMENT_REQUIRED, ARGUMENT_OPTIONAL")