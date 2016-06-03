__author__ = "UShareSoft"

from texttable import Texttable
from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from ussclicore.cmd import Cmd, CoreGlobal
from marketplace.objects.marketplace import *
from marketplacecli.utils import org_utils
from ussclicore.utils import printer
from role_entitlements_cmds import RoleEntitlementCmds
from marketplacecli.utils import marketplace_utils
from marketplacecli.utils.compare_utils import compare
import pyxb
import shlex

class RoleCmds(Cmd, CoreGlobal):
    """Manage platform roles. This is restricted to administrators."""

    cmd_name = "role"

    def __init__(self):
        self.subCmds = {}
        self.generate_sub_commands()
        super(RoleCmds, self).__init__()

    def generate_sub_commands(self):
        entitlements_cmds = RoleEntitlementCmds()
        self.subCmds[entitlements_cmds.cmd_name] = entitlements_cmds

    def arg_list(self):
        do_parser = ArgumentParser(prog=self.cmd_name + " list", add_help=True,
                                   description="List all the roles for a given organization.  If not organization is provided the default organization is used.")
        optional = do_parser.add_argument_group("optional arguments")
        optional.add_argument('--org', dest='org', required=False,
                              help="the organization name. If no organization is provided, then the default organization is used.")
        return do_parser

    def do_list(self, args):
        try:
            org_name = None
            if args:
                do_parser = self.arg_list()
                try:
                    do_args = do_parser.parse_args(shlex.split(args))
                except SystemExit as e:
                    return
                org_name = do_args.org

            # call UForge API
            printer.out("Getting all the roles for the organization...")
            org = org_utils.org_get(self.api, org_name)
            all_roles = self.api.Orgs(org.dbId).Roles().Getall(None)

            table = Texttable(200)
            table.set_cols_align(["c", "c"])
            table.header(["Name", "Description"])
            for role in all_roles.roles.role:
                table.add_row([role.name, role.description])
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

    def arg_info(self):
        do_parser = ArgumentParser(prog=self.cmd_name + " info", add_help=True,
                                   description="Prints out all the details of a specified role within an organization")
        mandatory = do_parser.add_argument_group("mandatory arguments")
        mandatory.add_argument('--name', dest='name', required=True, help="name of the role")
        optional = do_parser.add_argument_group("optional arguments")
        optional.add_argument('--org', dest='org', required=False,
                              help="the organization name. If no organization is provided, then the default organization is used.")
        return do_parser

    def do_info(self, args):
        try:
            # add arguments
            do_parser = self.arg_info()
            try:
                do_args = do_parser.parse_args(shlex.split(args))
            except SystemExit as e:
                return

            # call UForge API
            printer.out("Getting role [" + do_args.name + "]...")
            org = org_utils.org_get(self.api, do_args.org)
            all_roles = self.api.Orgs(org.dbId).Roles().Getall(None)

            selected_role = None
            for role in all_roles.roles.role:
                if role.name == do_args.name:
                    selected_role = role
                    break

            if selected_role is None:
                printer.out("No role [" + do_args.name + "]...")
                return 1

            printer.out("Name: " + selected_role.name)
            printer.out("Description: " + selected_role.description)
            table = Texttable(200)
            table.set_cols_align(["l", "l"])
            table.header(["Entitlement", "Description"])
            for entitlement in selected_role.entitlements.entitlement:
                table.add_row([entitlement.name, entitlement.description])
            print table.draw() + "\n"
            return 0
        except ArgumentParserError as e:
            printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
            self.help_info()
        except Exception as e:
            return marketplace_utils.handle_uforge_exception(e)

    def help_info(self):
        do_parser = self.arg_info()
        do_parser.print_help()

    def arg_create(self):
        do_parser = ArgumentParser(prog=self.cmd_name + " create", add_help=True,
                                   description="Create a new empty role in the specified organization")
        mandatory = do_parser.add_argument_group("mandatory arguments")
        mandatory.add_argument('--name', dest='name', required=True,
                               help="the name of the subscription profile to create")
        optional = do_parser.add_argument_group("optional arguments")
        optional.add_argument('--description', dest='description', required=False,
                              help="a role description for which the current command should be executed")
        optional.add_argument('--entitlements', dest='entitlements', nargs='+', required=False,
                              help="a list of entitlements to be added to this role during creation (example: --entitlements ent1 ent2 ent3). For a list of available entitlements, run the command: uforge entitlement list --org <org name>")
        optional.add_argument('--org', dest='org', required=False,
                              help="the organization name. If no organization is provided, then the default organization is used.")
        return do_parser

    def do_create(self, args):
        try:
            # add arguments
            do_parser = self.arg_create()
            try:
                do_args = do_parser.parse_args(shlex.split(args))
            except SystemExit as e:
                return

            printer.out("Creating role [" + do_args.name + "] ...")
            org = org_utils.org_get(self.api, do_args.org)

            new_role = role()
            new_role.name = do_args.name
            if do_args.description:
                new_role.description = do_args.description
            if do_args.entitlements:
                if do_args.entitlements is not None:
                    new_role.entitlements = pyxb.BIND()
                    entList = self.api.Entitlements.Getall()
                    entList = entList.entitlements.entitlement
                    entList = compare(entList, do_args.entitlements, "name")
                    for ent in entList:
                        add_entitlement = entitlement()
                        add_entitlement.name = ent.name
                        add_entitlement.description = ent.description
                        new_role.entitlements.append(add_entitlement)
                        printer.out("Entitlement " + ent.name + " added to the role")

            self.api.Orgs(org.dbId).Roles().Create(new_role)
            printer.out("Role [" + new_role.name + "] was correctly created", printer.OK)
            return 0
        except ArgumentParserError as e:
            printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
            self.help_create()
        except Exception as e:
            return marketplace_utils.handle_uforge_exception(e)

    def help_create(self):
        do_parser = self.arg_create()
        do_parser.print_help()

    def arg_delete(self):
        do_parser = ArgumentParser(prog=self.cmd_name + " delete", add_help=True,
                                   description="Delete a role from the specified organization")
        mandatory = do_parser.add_argument_group("mandatory arguments")
        mandatory.add_argument('--name', dest='name', required=True, help="name of the role")
        optional = do_parser.add_argument_group("optional arguments")
        optional.add_argument('--org', dest='org', required=False,
                              help="the organization name. If no organization is provided, then the default organization is used.")
        return do_parser

    def do_delete(self, args):
        try:
            # add arguments
            do_parser = self.arg_delete()
            try:
                do_args = do_parser.parse_args(shlex.split(args))
            except SystemExit as e:
                return

            printer.out("Deleting role [" + do_args.name + "] ...")
            org = org_utils.org_get(self.api, do_args.org)
            self.api.Orgs(org.dbId).Roles(do_args.name).Delete()
            printer.out("Role [" + do_args.name + "] deleted")
            return 0
        except ArgumentParserError as e:
            printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
            self.help_delete()
        except Exception as e:
            return marketplace_utils.handle_uforge_exception(e)

    def help_delete(self):
        do_parser = self.arg_delete()
        do_parser.print_help()
