__author__ = "UShareSoft"

from texttable import Texttable
from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from ussclicore.cmd import Cmd, CoreGlobal
from marketplacecli.utils import org_utils
from ussclicore.utils import printer
from ussclicore.utils import generics_utils
from marketplacecli.utils import marketplace_utils
from marketplace.objects.marketplace import *
from user_admin_cmds import UserAdminCmds
from user_role_cmds import UserRoleCmds
import shlex


class UserCmds(Cmd, CoreGlobal):
    """Manage users : list users, update users, update roles, enable/disable users"""

    cmd_name = "user"

    def __init__(self):
        self.subCmds = {}
        self.generate_sub_commands()
        super(UserCmds, self).__init__()

    def generate_sub_commands(self):
        user_admin_cmds = UserAdminCmds()
        self.subCmds[user_admin_cmds.cmd_name] = user_admin_cmds
        user_role_cmds = UserRoleCmds()
        self.subCmds[user_role_cmds.cmd_name] = user_role_cmds

    def arg_info(self):
        do_parser = ArgumentParser(prog=self.cmd_name + " info", add_help=True,
                                   description="Display informations of provided user")
        return do_parser

    def do_info(self, args):
        try:
            # call UForge API
            printer.out("Getting user [" + self.login + "] ...")
            user = self.api.Users(self.login).Get()

            if user is None:
                printer.out("user " + self.login + "does not exist", printer.ERROR)
            else:
                table = Texttable(200)
                table.set_cols_align(["c", "l", "c", "c", "c", "c", "c", "c"])
                table.header(
                    ["Login", "Email", "Lastname", "Firstname", "Created", "Active", "Promo Code", "Creation Code"])
                table.add_row([user.loginName, user.email, user.surname, user.firstName,
                               user.created.strftime("%Y-%m-%d %H:%M:%S"), "X", user.promoCode, user.creationCode])
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
        do_parser = ArgumentParser(prog=self.cmd_name + " create", add_help=True, description="Create a new user. This is restricted to administrators.")
        mandatory = do_parser.add_argument_group("mandatory arguments")
        mandatory.add_argument('--account', dest='account', required=True, help="the login name of the user to create")
        mandatory.add_argument('--email', dest='email', required=True, help="the email of the user to create")
        mandatory.add_argument('--code', dest='code', required=True,
                               help="the creation code (subscription profile) to be used to create the user account")
        optional = do_parser.add_argument_group("optional arguments")
        optional.add_argument('--accountPassword', dest='accountPassword', required=False,
                              help="the new user account password")
        optional.add_argument('--org', dest='org', required=False,
                              help="the organization in which the user should be created")
        optional.add_argument('--disable', dest='disable', required=False,
                              help="flag to de-activate the account during the creation")
        return do_parser

    def do_create(self, args):
        try:
            # add arguments
            do_parser = self.arg_create()
            try:
                do_args = do_parser.parse_args(shlex.split(args))
            except SystemExit as e:
                return

            # call UForge API
            printer.out("Creating user account [" + do_args.account + "] ...")

            # create a user manually
            new_user = user()
            new_user.loginName = do_args.account
            new_user.password = do_args.accountPassword
            new_user.creationCode = do_args.code
            new_user.email = do_args.email
            new_user.password = do_args.accountPassword

            if do_args.org:
                org = do_args.org
            else:
                org = None
            if do_args.disable:
                new_user.active = False
            else:
                new_user.active = True

            if do_args.accountPassword:
                auto_password = "false"
            else:
                auto_password = "true"

            # Send the create user request to the server
            new_user = self.api.Users(self.login).Create("true", "true", org, "false", "false", auto_password, new_user)

            if new_user is None:
                printer.out("No information about new user available", printer.ERROR)
            else:
                table = Texttable(200)
                table.set_cols_align(["c", "l", "c", "c", "c", "c", "c", "c"])
                table.header(
                    ["Login", "Email", "Lastname", "Firstname", "Created", "Active", "Promo Code", "Creation Code"])
                table.add_row([new_user.loginName, new_user.email, new_user.surname, new_user.firstName,
                               new_user.created.strftime("%Y-%m-%d %H:%M:%S"), "X", new_user.promoCode,
                               new_user.creationCode])
                print table.draw() + "\n"
            return 0
        except ArgumentParserError as e:
            printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
            self.help_create()
        except Exception as e:
            return marketplace_utils.handle_uforge_exception(e)

    def help_create(self):
        do_parser = self.arg_create()
        do_parser.print_help()

    def arg_list(self):
        do_parser = ArgumentParser(prog=self.cmd_name + " list", add_help=True,
                                   description="List the users registered to the platform")
        return do_parser

    def do_list(self, args):
        try:

            # call UForge API
            printer.out("Getting users...")
            users = self.api.Users(self.login).Getall(None, None, None)

            if users is None:
                printer.out("No user")
            else:
                table = Texttable(200)
                table.set_cols_align(["c", "l", "c", "c", "c", "c", "c", "c"])
                table.header(
                    ["Login", "Email", "Lastname", "Firstname", "Created", "Active", "Promo Code", "Creation Code"])
                for u in users.users.user:
                    if u.active:
                        active = "X"
                    else:
                        active = ""
                    table.add_row([u.loginName, u.email, u.surname, u.firstName,
                                   u.created.strftime("%Y-%m-%d %H:%M:%S"), active, u.promoCode, u.creationCode])
                print table.draw() + "\n"
            return 0
        except ArgumentParserError as e:
            printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
            self.help_info()
        except Exception as e:
            return marketplace_utils.handle_uforge_exception(e)

    def help_list(self):
        do_parser = self.arg_list()
        do_parser.print_help()

    def arg_enable(self):
        doParser = ArgumentParser(prog=self.cmd_name + " enable", add_help=True, description="Enable provided user. This is restricted to administrators.")
        mandatory = doParser.add_argument_group("mandatory arguments")

        mandatory.add_argument('--account', dest='account', required=True,
                               help="user name of the account for which the current command should be executed")
        return doParser

    def do_enable(self, args):
        try:
            doParser = self.arg_enable()
            doArgs = doParser.parse_args(shlex.split(args))

            printer.out("Enabling user [" + doArgs.account + "] ...")
            user = self.api.Users(doArgs.account).Get()
            if user is None:
                printer.out("user " + doArgs.account + "does not exist", printer.ERROR)
            else:
                if user.active == True:
                    printer.out("User [" + doArgs.account + "] is already enabled", printer.ERROR)
                else:
                    user.active = True
                    self.api.Users(doArgs.account).Update(body=user)
                    printer.out("User [" + doArgs.account + "] is now enabled", printer.OK)
                if user.active == True:
                    actived = "X"
                else:
                    actived = ""
                printer.out("Informations about [" + doArgs.account + "] :")
                table = Texttable(200)
                table.set_cols_align(["c", "l", "c", "c", "c", "c", "c", "c"])
                table.header(
                    ["Login", "Email", "Lastname", "Firstname", "Created", "Active", "Promo Code", "Creation Code"])
                table.add_row([user.loginName, user.email, user.surname, user.firstName,
                               user.created.strftime("%Y-%m-%d %H:%M:%S"), actived, user.promoCode, user.creationCode])
                print table.draw() + "\n"
            return 0
        except ArgumentParserError as e:
            printer.out("In Arguments: " + str(e), printer.ERROR)
            self.help_enable()
        except Exception as e:
            return marketplace_utils.handle_uforge_exception(e)

    def help_enable(self):
        doParser = self.arg_enable()
        doParser.print_help()

    def arg_disable(self):
        doParser = ArgumentParser(prog=self.cmd_name + " disable", add_help=True, description="Disable provided user. This is restricted to administrators.")
        mandatory = doParser.add_argument_group("mandatory arguments")

        mandatory.add_argument('--account', dest='account', required=True,
                               help="user name of the account for which the current command should be executed")
        return doParser

    def do_disable(self, args):
        try:
            doParser = self.arg_disable()
            doArgs = doParser.parse_args(shlex.split(args))

            printer.out("Disabling user [" + doArgs.account + "] ...")
            user = self.api.Users(doArgs.account).Get()
            if user is None:
                printer.out("user " + doArgs.account + "does not exist", printer.ERROR)
            else:
                if user.active == False:
                    printer.out("User [" + doArgs.account + "] is already disabled", printer.ERROR)
                else:
                    user.active = False
                    self.api.Users(doArgs.account).Update(body=user)
                    printer.out("User [" + doArgs.account + "] is now disabled", printer.OK)
                if user.active == True:
                    actived = "X"
                else:
                    actived = ""
                printer.out("Informations about [" + doArgs.account + "] :")
                table = Texttable(200)
                table.set_cols_align(["c", "l", "c", "c", "c", "c", "c", "c"])
                table.header(
                    ["Login", "Email", "Lastname", "Firstname", "Created", "Active", "Promo Code", "Creation Code"])
                table.add_row([user.loginName, user.email, user.surname, user.firstName,
                               user.created.strftime("%Y-%m-%d %H:%M:%S"), actived, user.promoCode, user.creationCode])
                print table.draw() + "\n"
            return 0
        except ArgumentParserError as e:
            printer.out("In Arguments: " + str(e), printer.ERROR)
            self.help_disable()
        except Exception as e:
            return marketplace_utils.handle_uforge_exception(e)

    def help_disable(self):
        doParser = self.arg_disable()
        doParser.print_help()
