#! /usr/bin/env python
# -*- coding: utf-8 -*-


# This file is part of Linshare api.
#
# LinShare api is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# LinShare api is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LinShare api.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2014 Frédéric MARTIN
#
# Contributors list :
#
#  Frédéric MARTIN frederic.martin.fma@gmail.com
#

from linshareapi.core import CoreCli
from linshareapi.core import ApiNotImplementedYet as ANIY
from linshareapi.user.users import Users
from linshareapi.user.rshares import ReceivedShares
from linshareapi.user.shares import Shares
from linshareapi.user.threads import Threads
from linshareapi.user.threadmembers import ThreadsMembers
from linshareapi.user.documents import Documents
# V2
from linshareapi.user.documents import Documents2
from linshareapi.user.rshares import ReceivedShares2
from linshareapi.user.threads import Threads2
from linshareapi.user.threadmembers import ThreadsMembers2
from linshareapi.user.threadentries import ThreadEntries
from linshareapi.user.users import Users2
from linshareapi.user.shares import Shares2



# -----------------------------------------------------------------------------
class UserCli(CoreCli):

    VERSION = 1
    VERSIONS = [0, 1]

    def __init__(self, host, user, password, verbose, debug, api_version=None):
        super(UserCli, self).__init__(host, user, password, verbose, debug)
        if api_version is None:
            api_version = self.VERSION
        if api_version not in self.VERSIONS:
            raise ValueError("API version not supported : " + str(api_version))
        self.base_url = "linshare/webservice/rest"
        # Default API
        self.documents = ANIY(self, api_version, "documents")
        self.rshares = ANIY(self, api_version, "rshares")
        self.shares = ANIY(self, api_version, "shares")
        self.threads = ANIY(self, api_version, "threads")
        self.thread_members = ANIY(self, api_version, "thread_members")
        self.users = ANIY(self, api_version, "users")
        # API declarations
        if api_version == 0:
            self.documents = Documents(self)
            self.rshares = ReceivedShares(self)
            self.shares = Shares(self)
            self.threads = Threads(self)
            self.thread_members = ThreadsMembers(self)
            self.users = Users(self)
        elif api_version == 1:
            self.base_url = "linshare/webservice/rest/user"
            self.users = Users2(self)
            self.documents = Documents2(self)
            self.rshares = ReceivedShares2(self)
            self.threads = Threads2(self)
            self.thread_members = ThreadsMembers2(self)
            self.thread_entries = ThreadEntries(self)
            self.shares = Shares2(self)
