__author__ = "UShareSoft"

from texttable import Texttable
from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from ussclicore.cmd import Cmd, CoreGlobal
from marketplace.objects.marketplace import *
from marketplacecli.utils import org_utils
from ussclicore.utils import printer
from marketplacecli.utils import marketplace_utils
import shlex


class UserRoleCmds(Cmd, CoreGlobal):
    """Manage users' roles"""

    cmd_name = "role"

    def __init__(self):
        super(UserRoleCmds, self).__init__()

    def arg_list(self):
        do_parser = ArgumentParser(prog=self.cmd_name + " list", add_help=True,
                                   description="Display the current list of roles for the user")
        mandatory = do_parser.add_argument_group("mandatory arguments")
        mandatory.add_argument('--account', dest='account', required=True,
                               help="user name of the account for which the current command should be executed")
        optional = do_parser.add_argument_group("optional arguments")
        optional.add_argument('--org', dest='org', required=False,
                              help="the organization name. If no organization is provided, then the default organization is used.")
        return do_parser

    def do_list(self, args):
        try:
            # add arguments
            do_parser = self.arg_list()
            try:
                do_args = do_parser.parse_args(shlex.split(args))
            except SystemExit as e:
                return

            printer.out("Getting roles for user [" + do_args.account + "]")
            roles = self.api.Users(do_args.account).Roles.Getall()

            table = Texttable(200)
            table.set_cols_align(["c", "c"])
            table.header(["Name", "Description"])
            for role in roles.roles.role:
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

    def arg_add(self):
        do_parser = ArgumentParser(prog=self.cmd_name + " add", add_help=True,
                                   description="Add one or more roles to the user (note the role(s) must exist in the organization where the user is a member)")
        mandatory = do_parser.add_argument_group("mandatory arguments")
        mandatory.add_argument('--account', dest='account', required=True,
                               help="user name of the account for which the current command should be executed")
        mandatory.add_argument('--roles', dest='roles', nargs='+', required=True,
                               help="a list of roles to be added to this user (example: --roles \"role1 role2 role3\"). For a list of available roles, run the command: uforge role list --org <org name>")
        optional = do_parser.add_argument_group("optional arguments")
        optional.add_argument('--org', dest='org', required=False,
                              help="the organization name. If no organization is provided, then the default organization is used.")
        return do_parser

    def do_add(self, args):
        try:
            do_parser = self.arg_add()
            try:
                do_args = do_parser.parse_args(shlex.split(args))
            except SystemExit as e:
                return

            # call UForge API
            printer.out("Getting user [" + do_args.account + "] ...")
            user = self.api.Users(do_args.account).Get()

            if user is None:
                printer.err("user " + self.login + "does not exist", printer.ERROR)
                return 1

            org = org_utils.org_get(self.api, do_args.org)
            all_roles = self.api.Orgs(org.dbId).Roles().Getall(None)

            # Check if the given roles really exist in the organization
            found = False
            for r in do_args.roles:
                found = False
                for existing_role in all_roles.roles.role:
                    if existing_role.name == r:
                        found = True
                        break;
                if not found:
                    printer.err("unable to find role with name [" + r + "] in org [" + org.name + "]")
                    return 1

            # Create a new roles structures
            new_roles = roles()
            new_roles.roles = pyxb.BIND()

            # Add the new roles
            for new_role in do_args.roles:
                r = role()
                r.name = new_role
                new_roles.roles.append(r)
            # Add the user existing roles
            for existing_user_role in user.roles.role:
                new_roles.roles.append(existing_user_role)

            self.api.Users(do_args.account).Roles.Update(new_roles)
            printer.out("User [" + do_args.account + "] updated with new roles.")
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
                                   description="Remove one or more roles from the user")
        mandatory = do_parser.add_argument_group("mandatory arguments")
        mandatory.add_argument('--account', dest='account', required=True,
                               help="user name of the account for which the current command should be executed")
        mandatory.add_argument('--roles', dest='roles', nargs='+', required=True,
                               help="a list of roles to be removed (example: --roles \"role1 role2 role3\").")
        return do_parser

    def do_remove(self, args):
        try:
            # add arguments
            do_parser = self.arg_remove()
            try:
                do_args = do_parser.parse_args(shlex.split(args))
            except SystemExit as e:
                return

            # Call to UForge API
            printer.out("Getting user [" + do_args.account + "] ...")
            user = self.api.Users(do_args.account).Get()

            new_roles = roles()
            new_roles.roles = pyxb.BIND()

            for r in user.roles.role:
                if r.name not in do_args.roles:
                    already_role = role()
                    already_role.name = r.name
                    new_roles.roles.append(already_role)

            self.api.Users(do_args.account).Roles.Update(new_roles)
            printer.out("User [" + do_args.account + "] roles updated.")
            return 0
        except ArgumentParserError as e:
            printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
            self.help_remove()
        except Exception as e:
            return marketplace_utils.handle_uforge_exception(e)

    def help_remove(self):
        do_parser = self.arg_remove()
        do_parser.print_help()
