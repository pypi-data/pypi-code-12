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

import appier

from . import bag
from . import color
from . import order
from . import account
from . import address
from . import country
from . import product
from . import voucher
from . import category
from . import collection
from . import subscription

BASE_URL = "http://localhost:8080/api/"
""" The default base url to be used when no other
base url value is provided to the constructor """

class Api(
    appier.Api,
    bag.BagApi,
    color.ColorApi,
    order.OrderApi,
    account.AccountApi,
    address.AddressApi,
    country.CountryApi,
    product.ProductApi,
    voucher.VoucherApi,
    category.CategoryApi,
    collection.CollectionApi,
    subscription.SubscriptionApi
):

    def __init__(self, *args, **kwargs):
        appier.Api.__init__(self, *args, **kwargs)
        self.base_url = appier.conf("BUDY_BASE_URL", BASE_URL)
        self.country = appier.conf("BUDY_COUNTRY", "US")
        self.currency = appier.conf("BUDY_CURRENCY", "USD")
        self.username = appier.conf("BUDY_USERNAME", None)
        self.password = appier.conf("BUDY_PASSWORD", None)
        self.base_url = kwargs.get("base_url", self.base_url)
        self.country = kwargs.get("country", self.country)
        self.currency = kwargs.get("currency", self.currency)
        self.username = kwargs.get("username", self.username)
        self.password = kwargs.get("password", self.password)
        self.session_id = kwargs.get("session_id", None)
        self.tokens = kwargs.get("tokens", None)

    def build(
        self,
        method,
        url,
        data = None,
        data_j = None,
        data_m = None,
        headers = None,
        params = None,
        mime = None,
        kwargs = None
    ):
        auth = kwargs.pop("auth", True)
        anonymous = kwargs.pop("anonymous", False)
        if auth: kwargs["session_id"] = self.get_session_id()
        if not anonymous: kwargs["session_id"] = self.session_id
        headers["X-Budy-Country"] = kwargs.pop("country", self.country)
        headers["X-Budy-Currency"] = kwargs.pop("currency", self.currency)

    def get_session_id(self):
        if self.session_id: return self.session_id
        return self.login()

    def auth_callback(self, params, headers):
        self.session_id = None
        session_id = self.get_session_id()
        params["session_id"] = session_id

    def login(self, username = None, password = None):
        username = username or self.username
        password = password or self.password
        url = self.base_url + "login"
        contents = self.post(
            url,
            callback = False,
            auth = False,
            username = username,
            password = password
        )
        self.username = contents.get("username", None)
        self.session_id = contents.get("session_id", None)
        self.tokens = contents.get("tokens", None)
        self.trigger("auth", contents)
        return self.session_id
