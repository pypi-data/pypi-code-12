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

class OrderApi(object):

    def list_orders(self, *args, **kwargs):
        url = self.base_url + "orders"
        contents = self.get(
            url,
            **kwargs
        )
        return contents

    def get_order(self, key):
        url = self.base_url + "orders/%s" % key
        contents = self.get(url, auth = False)
        return contents

    def set_shipping_address_order(self, key, payload):
        url = self.base_url + "orders/%s/shipping_address" % key
        contents = self.put(url, data_j = payload)
        return contents

    def set_billing_address_order(self, key, payload):
        url = self.base_url + "orders/%s/billing_address" % key
        contents = self.put(url, data_j = payload)
        return contents

    def set_store_shipping_order(self, key):
        url = self.base_url + "orders/%s/store_shipping" % key
        contents = self.put(url)
        return contents

    def set_store_billing_order(self, key):
        url = self.base_url + "orders/%s/store_billing" % key
        contents = self.put(url)
        return contents

    def set_email_order(self, key, payload):
        url = self.base_url + "orders/%s/email" % key
        contents = self.put(url, data_j = payload)
        return contents

    def set_referral_order(self, key, payload):
        url = self.base_url + "orders/%s/referral" % key
        contents = self.put(url, data_j = payload)
        return contents

    def set_voucher_order(self, key, payload):
        url = self.base_url + "orders/%s/voucher" % key
        contents = self.put(url, data_j = payload)
        return contents

    def wait_payment_order(self, key, payload):
        url = self.base_url + "orders/%s/wait_payment" % key
        contents = self.put(url, data_j = payload)
        return contents

    def pay_order(self, key, payload):
        url = self.base_url + "orders/%s/pay" % key
        contents = self.put(url, data_j = payload)
        return contents
