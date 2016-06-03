__author__ = "UShareSoft"

from texttable import Texttable
from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from ussclicore.cmd import Cmd, CoreGlobal
from ussclicore.utils import printer
from marketplacecli.utils import marketplace_utils


class EntitlementCmds(Cmd, CoreGlobal):
    """Manage entitlements: list them all. This is restricted to administrators."""

    cmd_name = "entitlement"

    def __init__(self):
        super(EntitlementCmds, self).__init__()

    def arg_list(self):
        do_parser = ArgumentParser(prog=self.cmd_name + " list", add_help=True,
                                   description="List all the entitlements in UForge.")
        return do_parser

    def do_list(self, args):
        try:
            # call UForge API
            printer.out("Getting all the entitlements for the platform ...")
            all_entitlements = self.api.Entitlements.Getall(None)

            table = Texttable(200)
            table.set_cols_align(["l", "l"])
            table.header(["Name", "Description"])
            for entitlement in all_entitlements.entitlements.entitlement:
                table.add_row([entitlement.name, entitlement.description])
            print table.draw() + "\n"
            return 0
        except ArgumentParserError as e:
            printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
            self.help_list()
        except Exception as e:
            return marketplace_utils.handle_uforge_exception(e)

    def help_list(self):
        do_parser = self.arg_list()
        do_parser.print_help()
