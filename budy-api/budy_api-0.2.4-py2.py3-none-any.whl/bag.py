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

class BagApi(object):

    def list_bags(self, *args, **kwargs):
        url = self.base_url + "bags"
        contents = self.get(
            url,
            **kwargs
        )
        return contents

    def create_bag(self, payload):
        url = self.base_url + "bags"
        contents = self.post(url, data_j = payload, auth = False)
        return contents

    def key_bag(self):
        url = self.base_url + "bags/key"
        contents = self.get(url, auth = False)
        return contents

    def get_bag(self, key):
        url = self.base_url + "bags/%s" % key
        contents = self.get(url, auth = False)
        return contents

    def merge_bag(self, key, target):
        url = self.base_url + "bags/%s/merge/%s" % (key, target)
        contents = self.put(url, auth = False)
        return contents

    def add_line_bag(self, key, payload):
        url = self.base_url + "bags/%s/lines" % key
        contents = self.post(url, data_j = payload, auth = False)
        return contents

    def remove_line_bag(self, key, line_id):
        url = self.base_url + "bags/%s/lines/%d" % (key, line_id)
        contents = self.delete(url, auth = False)
        return contents

    def add_update_line_bag(self, key, payload):
        url = self.base_url + "bags/%s/lines/add_update" % key
        contents = self.post(url, data_j = payload, auth = False)
        return contents

    def empty_bag(self, key):
        url = self.base_url + "bags/%s/empty" % key
        contents = self.get(url, auth = False)
        return contents

    def order_bag(self, key):
        url = self.base_url + "bags/%s/order" % key
        contents = self.get(url, auth = False)
        return contents
