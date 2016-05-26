__author__ = "UShareSoft"

from texttable import Texttable
from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from ussclicore.cmd import Cmd, CoreGlobal
from ussclicore.utils import printer
from marketplace.objects.marketplace import user
from marketplace.objects.marketplace import users
from marketplacecli.utils import org_utils
from marketplacecli.utils import marketplace_utils
import pyxb
import shlex

class SubscriptionProfileAdmins(Cmd, CoreGlobal):
    """Manage subscription profile admins"""

    cmd_name = "admin"

    def __init__(self):
        super(SubscriptionProfileAdmins, self).__init__()

    def arg_add(self):
        do_parser = ArgumentParser(prog=self.cmd_name + " add", add_help=True,
                                   description="Add a user as a subscription profile administrator.")
        mandatory = do_parser.add_argument_group("mandatory arguments")
        mandatory.add_argument('--name', dest='name', required=True, help="the name of the subscription profile")
        mandatory.add_argument('--admins', dest='admins', nargs='+', required=True,
                               help="the login names to add as new subscription profile administrators.")
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

            printer.out("Getting subscription profile with name [" + do_args.name + "]...")
            org = org_utils.org_get(self.api, do_args.org)
            subscriptions = self.api.Orgs(org.dbId).Subscriptions().Getall(Search=do_args.name)

            if subscriptions is None:
                printer.out("No subscription with name [" + do_args.name + "]")
            else:
                subscription = subscriptions.subscriptionProfiles.subscriptionProfile[0]

                # Create the list of administrators
                admins = users()
                admins.users = pyxb.BIND()

                # Copy the list of current administrators
                for admin in subscription.admins.admin:
                    already_admin = user()
                    already_admin.loginName = admin.loginName
                    admins.users.append(already_admin)

                for e in do_args.admins:
                    new_admin = user()
                    new_admin.loginName = e
                    admins.users.append(new_admin)

                # call UForge API
                self.api.Orgs(org.dbId).Subscriptions(subscription.dbId).Admins.Update(admins)
                printer.out("Some users added as administrators of subscription profile [" + do_args.name + "]...")
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
                                   description="Remove a user as an administrator of subscription profiles")
        mandatory = do_parser.add_argument_group("mandatory arguments")
        mandatory.add_argument('--name', dest='name', required=True, help="the name of the subscription profile")
        mandatory.add_argument('--admins', dest='admins', nargs='+', required=True,
                               help="the login names of the users to be removed from the the subscription profile administrators")
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

            printer.out("Getting subscription profile with name [" + do_args.name + "]...")
            org = org_utils.org_get(self.api, do_args.org)
            subscriptions = self.api.Orgs(org.dbId).Subscriptions().Getall(Search=do_args.name)

            if subscriptions is None:
                printer.out("No subscription with name [" + do_args.name + "]")
            else:
                subscription = subscriptions.subscriptionProfiles.subscriptionProfile[0]

                # Create the list of administrators
                admins = users()
                admins.users = pyxb.BIND()

                # Copy the list of current administrators - Remove the user selected in the input
                for admin in subscription.admins.admin:
                    if admin.loginName not in do_args.admins:
                        already_admin = user()
                        already_admin.loginName = admin.loginName
                        admins.users.append(already_admin)

                # call UForge API
                self.api.Orgs(org.dbId).Subscriptions(subscription.dbId).Admins.Update(admins)
                printer.out("Some users removed as administrators of subscription profile [" + do_args.name + "]...")
                return 0
        except ArgumentParserError as e:
            printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
            self.help_remove()
        except Exception as e:
            return marketplace_utils.handle_uforge_exception(e)

    def help_remove(self):
        do_parser = self.arg_remove()
        do_parser.print_help()
