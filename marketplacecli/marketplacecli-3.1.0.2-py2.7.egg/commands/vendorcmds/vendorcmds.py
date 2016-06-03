__author__ = "UShareSoft"

from texttable import Texttable
from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from ussclicore.cmd import Cmd, CoreGlobal
from marketplacecli.utils import org_utils
from ussclicore.utils import printer
from ussclicore.utils import generics_utils
from marketplacecli.utils import marketplace_utils
from marketplace.objects.marketplace import *
import shlex


class VendorCmds(Cmd, CoreGlobal):
    """Manage vendors : list vendors."""

    cmd_name = "vendor"

    def __init__(self):
        super(VendorCmds, self).__init__()

    def arg_list(self):
        do_parser = ArgumentParser(prog=self.cmd_name + " list", add_help=True,
                                   description="List the vendors that are part of the Marketplace. Also indicates whether the vendors are active or not.")
        optional = do_parser.add_argument_group("optional arguments")
        optional.add_argument('--org', dest='org', required=False,
                              help="the organization name. If no organization is provided, then the default organization is used.")
        return do_parser

    def do_list(self, args):
        try:
            # add arguments
            do_parser = self.arg_list()
            do_args = do_parser.parse_args(shlex.split(args))

            # call UForge API
            printer.out("Getting vendors ...")
            org = org_utils.org_get(self.api, do_args.org)
            vendors = self.api.Orgs(org.dbId).Vendors().Getall()

            table = Texttable(200)
            table.set_cols_align(["c", "c", "c"])
            table.header(["Active", "Name", "Email"])
            sorted_vendor_list = generics_utils.order_list_object_by(vendors.vendors.vendor, "name")
            for vendor in sorted_vendor_list:
                table.add_row(["" if vendor.inactive else "X", vendor.name, vendor.email])
            print table.draw() + "\n"
            return 0
        except ArgumentParserError as e:
            printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
            self.help_list()
        except Exception as e:
            return marketplace_utils.handle_uforge_exception(e)

    def help_list(self):
        do_parser = self.arg_info()
        do_parser.print_help()
