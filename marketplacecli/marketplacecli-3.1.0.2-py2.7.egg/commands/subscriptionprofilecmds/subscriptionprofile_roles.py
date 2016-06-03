__author__ = "UShareSoft"

from texttable import Texttable
from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from ussclicore.cmd import Cmd, CoreGlobal
from ussclicore.utils import printer
from marketplace.objects.marketplace import role
from marketplace.objects.marketplace import roles
from marketplacecli.utils import org_utils
from marketplacecli.utils import marketplace_utils
import pyxb
import shlex

class SubscriptionProfileRoles(Cmd, CoreGlobal):
    """Manage subscription profile roles"""

    cmd_name = "role"

    def __init__(self):
        super(SubscriptionProfileRoles, self).__init__()

    def arg_add(self):
        do_parser = ArgumentParser(prog=self.cmd_name + " add", add_help=True,
                                   description="Add roles to a subscription profile")
        mandatory = do_parser.add_argument_group("mandatory arguments")
        mandatory.add_argument('--name', dest='name', required=True, help="the name of the subscription profile")
        mandatory.add_argument('--roles', dest='roles', nargs='+', required=True,
                               help="the roles to add to the subscription profile")
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

            subscription = subscriptions.subscriptionProfiles.subscriptionProfile[0]

            # Create the list of roles
            all_roles = roles()
            all_roles.roles = pyxb.BIND()

            # Copy the list of current administrators
            for r in subscription.roles.role:
                already_role = role()
                already_role.name = r.name
                all_roles.roles.append(already_role)

            # Add the new administrators given as input
            for nr in do_args.roles:
                new_role = role()
                new_role.name = nr
                all_roles.roles.append(new_role)

            # call UForge API
            self.api.Orgs(org.dbId).Subscriptions(subscription.dbId).Roles.Update(all_roles)
            printer.out("Some roles added for subscription profile [" + do_args.name + "]...")
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
                                   description="Remove one or several roles from a subscription profile")
        mandatory = do_parser.add_argument_group("mandatory arguments")
        mandatory.add_argument('--name', dest='name', required=True, help="the name of the subscription profile")
        mandatory.add_argument('--roles', dest='roles', nargs='+', required=True,
                               help="the roles to add to the subscription profile")
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

            subscription = subscriptions.subscriptionProfiles.subscriptionProfile[0]

            # Create the list of administrators
            all_roles = roles()
            all_roles.roles = pyxb.BIND()

            # Copy the list of current roles - Remove the roles selected in args
            for r in subscription.roles.role:
                if r.name not in do_args.roles:
                    already_role = role()
                    already_role.name = r.name
                    all_roles.roles.append(already_role)

            # call UForge API
            self.api.Orgs(org.dbId).Subscriptions(subscription.dbId).Roles.Update(all_roles)
            printer.out("Somes roles removed from subscription profile [" + do_args.name + "]...")
            return 0
        except ArgumentParserError as e:
            printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
            self.help_remove()
        except Exception as e:
            return marketplace_utils.handle_uforge_exception(e)

    def help_remove(self):
        do_parser = self.arg_remove()
        do_parser.print_help()
