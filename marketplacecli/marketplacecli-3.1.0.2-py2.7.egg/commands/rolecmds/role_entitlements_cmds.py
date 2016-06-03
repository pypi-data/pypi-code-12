__author__ = "UShareSoft"

from texttable import Texttable
from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from ussclicore.cmd import Cmd, CoreGlobal
from marketplace.objects.marketplace import *
from marketplacecli.utils import org_utils
from ussclicore.utils import printer
from ussclicore.utils import generics_utils
from marketplacecli.utils import marketplace_utils
from marketplacecli.utils.compare_utils import compare
import pyxb
import shlex

class RoleEntitlementCmds(Cmd, CoreGlobal):
    """Manage roles entitlements"""

    cmd_name = "entitlement"

    def __init__(self):
        super(RoleEntitlementCmds, self).__init__()

    def arg_add(self):
        do_parser = ArgumentParser(prog=self.cmd_name + " add", add_help=True,
                                   description="Add one or more entitlements to a role within the specified organization")
        mandatory = do_parser.add_argument_group("mandatory arguments")
        mandatory.add_argument('--name', dest='name', required=True, help="the name of role")
        mandatory.add_argument('--entitlements', dest='entitlements', nargs='+', required=True,
                               help="the entitlements to the role")
        optional = do_parser.add_argument_group("optional arguments")
        optional.add_argument('--org', dest='org', required=False,
                              help="the organization name. If no organization is provided, then the default organization is used.")
        return do_parser

    def do_add(self, args):
        try:
            # add arguments
            do_parser = self.arg_add()
            try:
                do_args = do_parser.parse_args(shlex.split(args))
            except SystemExit as e:
                return

            printer.out("Getting role [" + do_args.name + "]...")
            org = org_utils.org_get(self.api, do_args.org)
            all_roles = self.api.Orgs(org.dbId).Roles().Getall(None)

            old_role = None
            for r in all_roles.roles.role:
                if r.name == do_args.name:
                    old_role = r
                    break

            if old_role is None:
                printer.out("No role [" + do_args.name + "]...")
                return 1

            new_role = role()
            new_role.name = old_role.name
            new_role.description = old_role.description
            new_role.entitlements = pyxb.BIND()

            for r in old_role.entitlements.entitlement:
                already_entitlement = entitlement()
                already_entitlement.name = r.name
                new_role.entitlements.append(already_entitlement)

            entitlementsList = self.api.Entitlements.Getall()
            entitlementsList = compare(entitlementsList.entitlements.entitlement, do_args.entitlements, "name")

            for e in do_args.entitlements:
                new_entitlement = entitlement()
                new_entitlement.name = e
                new_role.entitlements.append(new_entitlement)

            self.api.Orgs(org.dbId).Roles().Update(new_role)
            printer.out("Role [" + do_args.name + "] updated with new entitlements.")
            return 0
        except ArgumentParserError as e:
            printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
            self.help_add()
        except Exception as e:
            return marketplace_utils.handle_uforge_exception(e)

    def help_add(self):
        do_parser = self.arg_add()
        do_parser.print_help()

    def arg_remove(self):
        do_parser = ArgumentParser(prog=self.cmd_name + " remove", add_help=True,
                                   description="Remove one or more entitlements to a role within the specified organization")
        mandatory = do_parser.add_argument_group("mandatory arguments")
        mandatory.add_argument('--name', dest='name', required=True, help="the name of role")
        mandatory.add_argument('--entitlements', dest='entitlements', nargs='+', required=True,
                               help="the login name to remove as a new subscription profile administrator.")
        optional = do_parser.add_argument_group("optional arguments")
        optional.add_argument('--org', dest='org', required=False,
                              help="the organization name. If no organization is provided, then the default organization is used.")
        return do_parser

    def do_remove(self, args):
        try:
            # add arguments
            do_parser = self.arg_remove()
            try:
                do_args = do_parser.parse_args(shlex.split(args))
            except SystemExit as e:
                return

            printer.out("Getting role [" + do_args.name + "]...")
            org = org_utils.org_get(self.api, do_args.org)
            all_roles = self.api.Orgs(org.dbId).Roles().Getall(None)

            old_role = None
            for r in all_roles.roles.role:
                if r.name == do_args.name:
                    old_role = r
                    break

            if old_role is None:
                printer.out("No role [" + do_args.name + "]...")
                return 1

            new_role = role()
            new_role.name = old_role.name
            new_role.description = old_role.description
            new_role.entitlements = pyxb.BIND()

            delete_roles = compare(r.entitlements.entitlement, do_args.entitlements, "name")

            for entitlementItem in r.entitlements.entitlement:
                    exist = False
                    for deleterole in delete_roles:
                            if entitlementItem.name == deleterole.name:
                                    exist = True
                    if not exist:
                            already_entitlement = entitlement()
                            already_entitlement.name = entitlementItem.name
                            new_role.entitlements.append(already_entitlement)
                    else:
                            printer.out("Removed " + entitlementItem.name + " from role.")

            self.api.Orgs(org.dbId).Roles().Update(new_role)
            printer.out("Role [" + do_args.name + "] updated with new entitlements.")
            return 0
        except ArgumentParserError as e:
            printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
            self.help_remove()
        except Exception as e:
            return marketplace_utils.handle_uforge_exception(e)

    def help_remove(self):
        do_parser = self.arg_remove()
        do_parser.print_help()
