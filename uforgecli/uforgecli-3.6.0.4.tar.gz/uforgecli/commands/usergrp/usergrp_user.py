
__author__="UShareSoft"

from ussclicore.argumentParser import ArgumentParser, ArgumentParserError
from ussclicore.cmd import Cmd, CoreGlobal
from texttable import Texttable
from uforgecli.utils.org_utils import org_get
from ussclicore.utils import generics_utils, printer
from uforgecli.utils.uforgecli_utils import *
from uforgecli.utils import *
import shlex


class UserGroup_User_Cmd(Cmd, CoreGlobal):
        """User operation in user groups"""

        cmd_name = "user"

        def __init__(self):
                super(UserGroup_User_Cmd, self).__init__()

        def arg_add(self):
                doParser = ArgumentParser(add_help=True, description="Add one or more users to an user group within the specified organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--accounts', dest='accounts', nargs='+', required=True, help="A list of users to be added to this user group (example: --accounts userA userB userC)")
                mandatory.add_argument('--name', dest='name', type=str, required=True, help="Name of the user group")
                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")

                return doParser

        def do_add(self, args):
                try:
                        doParser = self.arg_add()
                        doArgs = doParser.parse_args(shlex.split(args))
                        org = org_get(self.api, doArgs.org)

                        allUsergrp = self.api.Usergroups.Getall(Name=org.name)
                        if allUsergrp.userGroups.userGroup is None or len(allUsergrp.userGroups.userGroup) == 0:
                                printer.out("There is no user group in organization [" + org.name + "].")
                                return 0
                        Exist = False
                        for item in allUsergrp.userGroups.userGroup:
                                if item.admin.name == doArgs.name:
                                        Exist = True
                                        userGroupId = item.dbId
                        if not Exist:
                                printer.out("The user group [" + doArgs.name + "] doesn't exist in [" + org.name + "].")
                                return 0

                        allMembers = self.api.Usergroups(userGroupId).Members.Get()

                        newUsers = users()
                        newUsers.users = pyxb.BIND()
                        for item2 in allMembers.users.user:
                                newUser = user()
                                newUser.loginName = item2.loginName
                                newUsers.users.append(newUser)
                        for item3 in doArgs.accounts:
                                userExist = False
                                for item4 in allMembers.users.user:
                                        if item3 == item4.loginName:
                                                userExist = True
                                                printer.out("User [" + item3 + "] is already in the user group.", printer.WARNING)
                                                break
                                if not userExist:
                                        newUser = user()
                                        newUser.loginName = item3
                                        newUsers.users.append(newUser)
                                        printer.out("User " + newUser.loginName + " has been added to the user group.", printer.OK)

                        result = self.api.Usergroups(userGroupId).Members.Add(body=newUsers)
                        return 0

                except ArgumentParserError as e:
                        printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
                        self.help_add()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_add(self):
                doParser = self.arg_add()
                doParser.print_help()

        def arg_remove(self):
                doParser = ArgumentParser(add_help=True, description="Remove one or more users from an user group within the specified organization")

                mandatory = doParser.add_argument_group("mandatory arguments")
                optional = doParser.add_argument_group("optional arguments")

                mandatory.add_argument('--accounts', dest='accounts', nargs='+', required=True, help="A list of users to be deleted to this user group (example: --accounts userA userB userC)")
                mandatory.add_argument('--name', dest='name', type=str, required=True, help="Name of the user group")
                optional.add_argument('--org', dest='org', type=str, required=False, help="The organization name. If no organization is provided, then the default organization is used.")

                return doParser

        def do_remove(self, args):
                try:
                        doParser = self.arg_remove()
                        doArgs = doParser.parse_args(shlex.split(args))
                        org = org_get(self.api, doArgs.org)

                        allUsergrp = self.api.Usergroups.Getall(Name=org.name)
                        if allUsergrp.userGroups.userGroup is None or len(allUsergrp.userGroups.userGroup) == 0:
                                printer.out("There is no user group in organization [" + org.name + "].")
                                return 0
                        Exist = False
                        for item in allUsergrp.userGroups.userGroup:
                                if item.admin.name == doArgs.name:
                                        Exist = True
                                        userGroupId = item.dbId
                        if not Exist:
                                printer.out("The user group [" + doArgs.name + "] doesn't exist in [" + org.name + "].")
                                return 0

                        allMembers = self.api.Usergroups(userGroupId).Members.Get()

                        newUsers = users()
                        newUsers.users = pyxb.BIND()
                        for item2 in allMembers.users.user:
                                for item3 in doArgs.accounts:
                                        if item3 == item2.loginName:
                                                result = self.api.Usergroups(userGroupId).Members.Delete(User=item2.loginName)
                                                printer.out("User [" + item2.loginName + "] has been deleted from the user group.", printer.OK)

                        return 0

                except ArgumentParserError as e:
                        printer.out("ERROR: In Arguments: " + str(e), printer.ERROR)
                        self.help_remove()
                except Exception as e:
                        return handle_uforge_exception(e)

        def help_remove(self):
                doParser = self.arg_remove()
                doParser.print_help()