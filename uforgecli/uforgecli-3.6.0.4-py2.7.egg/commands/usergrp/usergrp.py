
__author__="UShareSoft"

from texttable import Texttable
from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from uforgecli.utils.uforgecli_utils import *
from ussclicore.cmd import Cmd, CoreGlobal
from uforgecli.utils import org_utils
from ussclicore.utils.generics_utils import order_list_object_by
from ussclicore.utils import printer
from uforge.objects import uforge
from ussclicore.utils import generics_utils
from uforgecli.utils import uforgecli_utils
from uforgecli.utils.org_utils import org_get
from usergrp_user import UserGroup_User_Cmd
import pyxb
import datetime
import shlex


class Usergrp_Cmd(Cmd, CoreGlobal):
        """user group administration (list/info/create/delete etc)"""

        cmd_name = "usergrp"

        def __init__(self):
                self.generate_sub_commands()
                super(Usergrp_Cmd, self).__init__()

        def generate_sub_commands(self):
                if not hasattr(self, 'subCmds'):
                        self.subCmds = {}

                user = UserGroup_User_Cmd()
                self.subCmds[user.cmd_name] = user

        def arg_list(self):
                doParser = ArgumentParser(add_help=True, description="List all the user groups for a given organization.  If not organization is provided the default organization is used.")

                optional = doParser.add_argument_group("optional arguments")

                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")

                return doParser

        def do_list(self, args):
                try:
                        doParser = self.arg_list()
                        doArgs = doParser.parse_args(shlex.split(args))
                        org = org_get(self.api, doArgs.org)

                        allUsergrp = self.api.Usergroups.Getall(Name=org.name)

                        if allUsergrp is None:
                                printer.out("No user groups found.")
                                return 0

                        allUsergrp = allUsergrp.userGroups.userGroup

                        table = Texttable(200)
                        table.set_cols_align(["l", "r"])
                        table.header(["Name", "# Members"])
                        for item in allUsergrp:
                                table.add_row([item.admin.name, str(len(item.members.member))])
                        print table.draw() + "\n"

                        printer.out("Found " + str(len(allUsergrp)) + " user group in [" + org.name + "].")

                        return 0

                except ArgumentParserError as e:
                        printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
                        self.help_list()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_list(self):
                doParser = self.arg_list()
                doParser.print_help()

        def arg_info(self):
                doParser = ArgumentParser(add_help=True, description="Prints out all the information for a user group within an organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--name', dest='name', type=str, required=True, help="Name of the user group")
                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")

                return doParser

        def do_info(self, args):
                try:
                        doParser = self.arg_info()
                        doArgs = doParser.parse_args(shlex.split(args))
                        org = org_get(self.api, doArgs.org)

                        printer.out("Getting user group [" + org.name + "] from the default organization ...")
                        allUsergrp = self.api.Usergroups.Getall(Name=org.name)

                        if allUsergrp is None:
                                printer.out("No user groups found in [" + org.name + "].")
                                return 0

                        allUsergrp = allUsergrp.userGroups.userGroup
                        for item in allUsergrp:
                                if item.admin.name == doArgs.name:
                                        printer.out("Displaying info on [" + item.admin.name + "]:\n")
                                        printer.out("Name : " + item.admin.name)
                                        if len(item.members.member) > 0:
                                                table = Texttable(200)
                                                table.set_cols_align(["l"])
                                                table.header(["Members"])
                                                for item2 in item.members.member:
                                                        table.add_row([item2.name])
                                                print table.draw() + "\n"
                                                return 0
                                        else:
                                                printer.out("No members found in this user group.")
                                                return 0
                        printer.out("The user group [" + doArgs.name + " was not found in [" + org.name + "].")
                        return 0

                except ArgumentParserError as e:
                        printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
                        self.help_info()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_info(self):
                doParser = self.arg_info()
                doParser.print_help()

        def arg_create(self):
                doParser = ArgumentParser(add_help=True, description="Create a new user group in the specified organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--name', dest='name', type=str, required=True, help="Name of the user group")
                mandatory.add_argument('--email', dest='email', type=str, required=True, help="The email address associated to this user group (the email cannot be used by another user in the platform)")
                mandatory.add_argument('--usergrpPassword', dest='usergrpPassword', type=str, required=True, help="The password of the user group administrator")
                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")
                optional.add_argument('--accounts', dest='accounts', nargs='+', required=False, help="A list of users to be added to this user group during creation (example: --accounts userA userB userC).")

                return doParser

        def do_create(self, args):
                try:
                        doParser = self.arg_create()
                        doArgs = doParser.parse_args(shlex.split(args))
                        org = org_get(self.api, doArgs.org)

                        newUsergrp = userGroup()
                        newUser = user()
                        newUser.loginName = doArgs.name
                        newUser.email = doArgs.email
                        newUser.password = doArgs.usergrpPassword
                        newUsergrp.admin = newUser

                        newUsergrp.members = pyxb.BIND()
                        if doArgs.accounts is not None:
                                for item in doArgs.accounts:
                                        addNewUser = user()
                                        addNewUser.loginName = item
                                        newUsergrp.members.append(addNewUser)
                                        printer.out("[" + addNewUser.loginName + "] has been added to user group.")

                        result = self.api.Usergroups.Create(Org=org.name,body=newUsergrp)
                        printer.out("User group [" + newUser.loginName + "] has been successfully created", printer.OK)
                        return 0

                except ArgumentParserError as e:
                        printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
                        self.help_create()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_create(self):
                doParser = self.arg_create()
                doParser.print_help()

        def arg_delete(self):
                doParser = ArgumentParser(add_help=True, description="Delete an user group from the specified organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--name', dest='name', type=str, required=True, help="Name of the user group")
                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")

                return doParser

        def do_delete(self, args):
                try:
                        doParser = self.arg_delete()
                        doArgs = doParser.parse_args(shlex.split(args))
                        org = org_get(self.api, doArgs.org)

                        allUsergrp = self.api.Usergroups.Getall(Name=org.name)

                        if allUsergrp is None:
                                printer.out("No user groups found in [" + org.name + "].")
                                return 0

                        allUsergrp = allUsergrp.userGroups.userGroup
                        for item in allUsergrp:
                                if item.admin.name == doArgs.name:
                                        result = self.api.Usergroups(item.dbId).Delete()
                                        printer.out("[" + item.admin.name + "] has been successfully deleted.", printer.OK)
                                        return 0

                        printer.out("[" + doArgs.name + "] was not found in [" + org.name + "].")

                        return 0

                except ArgumentParserError as e:
                        printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
                        self.help_delete()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_delete(self):
                doParser = self.arg_delete()
                doParser.print_help()
