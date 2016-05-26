__author__ = "UShareSoft"

from texttable import Texttable
from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from ussclicore.cmd import Cmd, CoreGlobal
from marketplacecli.utils import org_utils
from ussclicore.utils import printer
from ussclicore.utils import generics_utils
from marketplace.objects.marketplace import *
from subscriptionprofile_admins import SubscriptionProfileAdmins
from subscriptionprofile_roles import SubscriptionProfileRoles
from marketplacecli.utils import marketplace_utils
import pyxb
import shlex

class SubscriptionProfileCmds(Cmd, CoreGlobal):
    """Manage subscription profiles : list profile, create profiles, update profiles. This is restricted to administrators."""

    cmd_name = "subscription"

    def __init__(self):
        self.subCmds = {}
        self.generate_sub_commands()
        super(SubscriptionProfileCmds, self).__init__()

    def generate_sub_commands(self):
        subscriptionprofile_roles_cmds = SubscriptionProfileRoles()
        self.subCmds[subscriptionprofile_roles_cmds.cmd_name] = subscriptionprofile_roles_cmds
        subscriptionprofile_admin_cmds = SubscriptionProfileAdmins()
        self.subCmds[subscriptionprofile_admin_cmds.cmd_name] = subscriptionprofile_admin_cmds

    def arg_list(self):
        do_parser = ArgumentParser(prog=self.cmd_name + " list", add_help=True,
                                   description="List all the subscription profiles for a given organization.  If no organization is provided the default organization is used.")
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
            printer.out("Getting all the subscription profiles for organization ...")
            org = org_utils.org_get(self.api, org_name)
            print org
            subscriptions = self.api.Orgs(org.dbId).Subscriptions().Getall(None)

            table = Texttable(200)
            table.set_cols_align(["c", "c", "c", "c"])
            table.header(["Name", "Code", "Active", "description"])
            for subscription in subscriptions.subscriptionProfiles.subscriptionProfile:
                table.add_row([subscription.name, subscription.code, "X" if subscription.active else "",
                               subscription.description])
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
                                   description="Get detailed information on a subscription profile within an organization.")
        mandatory = do_parser.add_argument_group("mandatory arguments")
        mandatory.add_argument('--name', dest='name', required=True, help="the name of the subscription profile")
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
            printer.out("Getting subscription profile with name [" + do_args.name + "]...")
            org = org_utils.org_get(self.api, do_args.org)
            subscriptions = self.api.Orgs(org.dbId).Subscriptions().Getall(Search=do_args.name)

            table = Texttable(200)
            table.set_cols_align(["l", "l"])
            table.header(["Info", "Value"])
            subscription = subscriptions.subscriptionProfiles.subscriptionProfile[0]
            table.add_row(["Name", subscription.name])
            table.add_row(["Code", subscription.code])
            table.add_row(["Active", "Yes" if subscription.active else "No"])
            if subscription.roles.role:
                table.add_row(["Roles", ""])
                for role in subscription.roles.role:
                    table.add_row(["", role.name])
            else:
                table.add_row(["Roles", "None"])
            if subscription.admins.admin:
                table.add_row(["Administrators", ""])
                for admin in subscription.admins.admin:
                    table.add_row(["", admin.loginName])
            else:
                table.add_row(["Administrators", "None"])
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
                                   description="Create a new subscription profile within an organization. A subscription profile is mandatory in order to create a user. It must also be activated. By default, the subscription profiles you create are not active.")
        mandatory = do_parser.add_argument_group("mandatory arguments")
        mandatory.add_argument('--name', dest='name', required=True,
                               help="the name of the subscription profile to create")
        mandatory.add_argument('--code', dest='code', required=True,
                               help="the code of the subscription profile to create")
        optional = do_parser.add_argument_group("optional arguments")
        optional.add_argument('--description', dest='description', required=False,
                              help="the description of the subscription profile to create")
        optional.add_argument('--active', dest='active', required=False,
                              help="flag to make the subscription profile active.")
        optional.add_argument('--admins', dest='admins', nargs='+', required=False,
                              help="admin users to be added to the subscription profile that can use the subscription profile to create a user (users separated by spaces)")
        optional.add_argument('--roles', dest='roles', nargs='+', required=False,
                              help="roles to be added to the subscription profile")
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

            # call UForge API
            printer.out("Creating subscription profile [" + do_args.name + "] ...")
            org = org_utils.org_get(self.api, do_args.org)

            # create a user manually
            new_subscription_profile = subscriptionProfile()
            new_subscription_profile.name = do_args.name
            new_subscription_profile.code = do_args.code
            if do_args.description:
                new_subscription_profile.description = do_args.description
            if do_args.active:
                new_subscription_profile.active = do_args.active

            new_subscription_profile.admins = pyxb.BIND()
            if do_args.admins:
                for a in do_args.admins:
                    new_admin = user()
                    new_admin.loginName = a
                    new_subscription_profile.admins.append(new_admin)

            new_subscription_profile.roles = pyxb.BIND()
            if do_args.roles:
                for a in do_args.roles:
                    new_role = role()
                    new_role.name = a
                    new_subscription_profile.roles.append(new_role)

            # Send the create user request to the server
            new_subscription_profile = self.api.Orgs(org.dbId).Subscriptions().Add(new_subscription_profile)

            if new_subscription_profile is None:
                printer.out("No information about the new subscription profile available", printer.ERROR)
            else:
                table = Texttable(200)
                table.set_cols_align(["c", "c", "c"])
                table.header(
                    ["Name", "Code", "Active"])
                table.add_row([new_subscription_profile.name, new_subscription_profile.code,
                               "X" if new_subscription_profile.active else ""])
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

    def arg_delete(self):
        do_parser = ArgumentParser(prog=self.cmd_name + " delete", add_help=True,
                                   description="Delete a subscription profile from an organization.")
        mandatory = do_parser.add_argument_group("mandatory arguments")
        mandatory.add_argument('--name', dest='name', required=True,
                               help="the name of the subscription profile to delete")
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

            printer.out("Deleting subscription profile [" + do_args.name + "] ...")
            org = org_utils.org_get(self.api, do_args.org)

            # call UForge API
            subscriptions = self.api.Orgs(org.dbId).Subscriptions().Getall(Search=do_args.name)

            if len(subscriptions.subscriptionProfiles.subscriptionProfile) == 1:
                subscription = subscriptions.subscriptionProfiles.subscriptionProfile[0]
                self.api.Orgs(org.dbId).Subscriptions(subscription.dbId).Remove(None)
                printer.out("Subscription profile [" + do_args.name + "] deleted")
            else:
                printer.out("Unable to delete subscription profile [" + do_args.name + "]")
            return 0
        except ArgumentParserError as e:
            printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
            self.help_delete()
        except Exception as e:
            return marketplace_utils.handle_uforge_exception(e)

    def help_delete(self):
        do_parser = self.arg_delete()
        do_parser.print_help()

    def arg_update(self):
        do_parser = ArgumentParser(prog=self.cmd_name + " update", add_help=True,
                                   description="Updates a new subscription profile")
        mandatory = do_parser.add_argument_group("mandatory arguments")
        mandatory.add_argument('--name', dest='name', required=True,
                               help="the name of the subscription profile to update")
        optional = do_parser.add_argument_group("optional arguments")
        optional.add_argument('--description', dest='description', required=False,
                              help="the description of the subscription profile to update")
        optional.add_argument('--active', dest='active', required=False,
                              help="flag to make the subscription profile active.")
        optional.add_argument('--org', dest='org', required=False,
                              help="the organization name. If no organization is provided, then the default organization is used.")
        return do_parser

    def do_update(self, args):
        try:
            # add arguments
            do_parser = self.arg_update()
            try:
                do_args = do_parser.parse_args(shlex.split(args))
            except SystemExit as e:
                return

            printer.out("Getting subscription profile with name [" + do_args.name + "]...")
            org = org_utils.org_get(self.api, do_args.org)
            # call UForge API
            subscriptions = self.api.Orgs(org.dbId).Subscriptions().Getall(Search=do_args.name)

            if subscriptions.total == 1:
                subscription = subscriptions.subscriptionProfiles.subscriptionProfile[0]
                updated_subscription = subscriptionProfile()
                updated_subscription.name = subscription.name
                updated_subscription.code = subscription.code
                if do_args.description:
                    updated_subscription.description = do_args.description
                if do_args.active:
                    updated_subscription.active = True
                else:
                    updated_subscription.active = False
                printer.out("Updating subscription profile with name [" + do_args.name + "] ...")
                # call UForge API
                self.api.Orgs(org.dbId).Subscriptions(subscription.dbId).Update(updated_subscription)
            return 0
        except ArgumentParserError as e:
            printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
            self.help_update()
        except Exception as e:
            return marketplace_utils.handle_uforge_exception(e)

    def help_update(self):
        do_parser = self.arg_update()
        do_parser.print_help()
