__author__ = "UShareSoft"

from texttable import Texttable
from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from ussclicore.cmd import Cmd, CoreGlobal
from marketplace.objects.marketplace import *
from marketplacecli.utils import org_utils
from ussclicore.utils import printer
from ussclicore.utils import generics_utils
from marketplacecli.utils import marketplace_utils
import shlex


class UserAdminCmds(Cmd, CoreGlobal):
    """Manage administrators (promote/demote users as administrators)"""

    cmd_name = "admin"

    def __init__(self):
        super(UserAdminCmds, self).__init__()

    def arg_promote(self):
        doParser = ArgumentParser(add_help=True,
                                  description="Promote user to be an administrator of an organization (note: admin access rights are handled by roles)")
        mandatory = doParser.add_argument_group("mandatory arguments")
        optionnal = doParser.add_argument_group("optionnal arguments")

        mandatory.add_argument('--account', dest='account', type=str, required=True,
                               help="User name of the account to promote")
        optionnal.add_argument('--org', dest='org', type=str, required=False,
                               help="the organization where the user is/will be a member/administrator (depending on command context). If no organization is provided, then the default organization is used.")
        return doParser

    def do_promote(self, args):
        try:
            doParser = self.arg_promote()
            doArgs = doParser.parse_args(shlex.split(args))
            orgSpecified = org_utils.org_get(api=self.api, name=doArgs.org)

            adminUser = self.api.Users(doArgs.account).Get()

            if adminUser == None:
                printer.out("User [" + doArgs.account + "] doesn't exist.", printer.ERROR)
            else:
                self.api.Orgs(orgSpecified.dbId).Members(adminUser.loginName).Change(Admin=True, body=adminUser)
                printer.out("User [" + doArgs.account + "] has been promoted in [" + orgSpecified.name + "] :",
                            printer.OK)

            if adminUser.active == True:
                active = "X"
            else:
                active = ""

            printer.out("Informations about [" + adminUser.loginName + "] :")
            table = Texttable(200)
            table.set_cols_align(["c", "l", "c", "c", "c", "c", "c", "c"])
            table.header(
                ["Login", "Email", "Lastname", "Firstname", "Created", "Active", "Promo Code", "Creation Code"])
            table.add_row([adminUser.loginName, adminUser.email, adminUser.surname, adminUser.firstName,
                           adminUser.created.strftime("%Y-%m-%d %H:%M:%S"), active, adminUser.promoCode,
                           adminUser.creationCode])
            print table.draw() + "\n"
            return 0
        except ArgumentParserError as e:
            printer.out("In Arguments: " + str(e), printer.ERROR)
            self.help_promote()
        except Exception as e:
            return marketplace_utils.handle_uforge_exception(e)

    def arg_demote(self):
        doParser = ArgumentParser(add_help=True,
                                  description="Demote an user from being an organization administrator")
        mandatory = doParser.add_argument_group("mandatory arguments")
        optionnal = doParser.add_argument_group("optionnal arguments")
        mandatory.add_argument('--account', dest='account', type=str, required=True,
                               help="User name of the account to demote")
        optionnal.add_argument('--org', dest='org', type=str, required=False,
                               help="the organization where the user is/will be a member/administrator (depending on command context). If no organization is provided, then the default organization is used.")
        return doParser

    def help_promote(self):
        doParser = self.arg_promote()
        doParser.print_help()

    def do_demote(self, args):
        try:
            doParser = self.arg_demote()
            doArgs = doParser.parse_args(shlex.split(args))
            orgSpecified = org_utils.org_get(api=self.api, name=doArgs.org)

            adminUser = self.api.Users(doArgs.account).Get()

            if adminUser == None:
                printer.out("User [" + doArgs.account + "] doesn't exist.", printer.ERROR)
            else:
                self.api.Orgs(orgSpecified.dbId).Members(adminUser.loginName).Change(Admin=False,
                                                                                     body=adminUser)
                printer.out("User [" + doArgs.account + "] has been demoted in [" + orgSpecified.name + "] :",
                            printer.OK)

            if adminUser.active == True:
                active = "X"
            else:
                active = ""

            printer.out("Informations about [" + adminUser.loginName + "] :")
            table = Texttable(200)
            table.set_cols_align(["c", "l", "c", "c", "c", "c", "c", "c"])
            table.header(
                ["Login", "Email", "Lastname", "Firstname", "Created", "Active", "Promo Code", "Creation Code"])
            table.add_row([adminUser.loginName, adminUser.email, adminUser.surname, adminUser.firstName,
                           adminUser.created.strftime("%Y-%m-%d %H:%M:%S"), active, adminUser.promoCode,
                           adminUser.creationCode])
            print table.draw() + "\n"
            return 0
        except ArgumentParserError as e:
            printer.out("In Arguments: " + str(e), printer.ERROR)
            self.help_demote()
        except Exception as e:
            return marketplace_utils.handle_uforge_exception(e)

    def help_demote(self):
        doParser = self.arg_demote()
        doParser.print_help()
