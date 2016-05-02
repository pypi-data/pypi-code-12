#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Budy API
# Copyright (c) 2008-2016 Hive Solutions Lda.
#
# This file is part of Hive Budy API.
#
# Hive Budy API is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Budy API is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Budy API. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2016 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

class AccountApi(object):

    def me_account(self):
        url = self.base_url + "accounts/me"
        contents = self.get(url)
        return contents

    def update_me_account(self, payload):
        url = self.base_url + "accounts/me"
        contents = self.put(url, data_j = payload)
        return contents

    def orders_me_account(self):
        url = self.base_url + "accounts/me/orders"
        contents = self.get(url)
        return contents

    def addresses_me_account(self):
        url = self.base_url + "accounts/me/addresses"
        contents = self.get(url)
        return contents

    def create_addresses_me_account(self, payload):
        url = self.base_url + "accounts/me/addresses"
        contents = self.post(url, data_j = payload)
        return contents

    def delete_address_me_account(self, key):
        url = self.base_url + "accounts/me/addresses/%s" % key
        contents = self.delete(url)
        return contents
