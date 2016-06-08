# -*- coding: utf-8 -*-

from __future__ import print_function
import sys

from malibu.command import module
from malibu.text import ascii


class BuiltinHelpModule(module.CommandModule):

    BASE = "help"

    def __init__(self, loader):

        super(BuiltinHelpModule, self).__init__(base=BuiltinHelpModule.BASE)

        self.project_description = "default"
        self.project_version = "0.0.1"

        self.__loader = loader
        self.register_subcommand("all", self.all_help)
        self.register_subcommand("show", self.show_module)

    def all_help(self, *args, **kw):
        """ Displays help for all registered modules.
        """

        if 'args' in kw:
            argparser = kw['args']
        else:
            argparser = self.__loader.get_argument_parser()

        exec_name = sys.argv[0] if not argparser.exec_file else argparser.exec_file
        print("{:4s}: version {:s}: {:s}".format(
            ascii.style_text(ascii.STYLE_BOLD, exec_name),
            ascii.style_text(ascii.STYLE_UNDERSCORE, self.project_version),
            ascii.style_text(ascii.FG_GREEN, self.project_description)))

        print("{:>24s}".format(
            ascii.style_text(ascii.FG_GREEN, 'Arguments')))

        args = argparser.get_option_descriptions()
        for option, description in args.items():
            print("{:>36s}    {:<64s}".format(
                ascii.style_text(ascii.STYLE_BOLD, option),
                ascii.style_text(ascii.STYLE_OFF, description)))

        print("{:>24s}".format(
            ascii.style_text(ascii.FG_GREEN, 'Subcommands')))

        modules = self.__loader.modules
        for mod in sorted(modules, key=lambda m: m.get_base()):
            for sub, helpstr in mod.get_help().items():
                command = ':'.join([mod.get_base(), sub])
                helplst = helpstr.splitlines()
                if len(helplst) == 1:
                    print("{:>36s}    {:<64s}".format(
                        ascii.style_text(ascii.STYLE_UNDERSCORE, command),
                        helpstr))
                else:
                    print("{:>36s}    {:<64s}".format(
                        ascii.style_text(ascii.STYLE_UNDERSCORE, command),
                        ascii.style_text(ascii.STYLE_OFF, helplst[0].lstrip())))
                    for line in helplst[1:]:
                        print("{:>28s}    {:<64s}".format(
                            "",
                            ascii.style_text(ascii.STYLE_OFF, line.lstrip())))
                print("")

    def show_module(self, *args, **kw):
        """ Displays help for a single module.
        """

        if 'args' in kw:
            argparser = kw['args']
        else:
            argparser = self.__loader.get_argument_parser()

        try:
            mod_name = args[1]
        except:
            self.all_help(args=argparser)
            return

        if len(mod_name) == 0:
            self.all_help(args=argparser)
            return

        exec_name = sys.argv[0]
        print("{:4s}: version {:s}: {:s}".format(
            ascii.style_text(ascii.STYLE_BOLD, exec_name),
            ascii.style_text(ascii.STYLE_UNDERSCORE, self.project_version),
            ascii.style_text(ascii.FG_GREEN, self.project_description)))

        print("{:>24s}".format(
            ascii.style_text(ascii.FG_GREEN, 'Subcommands')))

        modules = self.__loader.modules
        for mod in modules:
            if mod.get_base() == mod_name:
                for sub, helpstr in mod.get_help().items():
                    command = ':'.join([mod.get_base(), sub])
                    helplst = helpstr.splitlines()
                    if len(helplst) == 1:
                        print("{:>36s}   {:<64s}".format(
                            ascii.style_text(ascii.STYLE_UNDERSCORE, command),
                            helpstr))
                    else:
                        print("{:>36s}    {:<64s}".format(
                            ascii.style_text(ascii.STYLE_UNDERSCORE, command),
                            ascii.style_text(ascii.STYLE_OFF, helplst[0].lstrip())))
                        for line in helplst[1:]:
                            print("{:>28s}    {:<64s}".format(
                                "",
                                ascii.style_text(ascii.STYLE_OFF, line.lstrip())))
                    print("")
