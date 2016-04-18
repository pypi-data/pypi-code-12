#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Story API
# Copyright (c) 2008-2016 Hive Solutions Lda.
#
# This file is part of Hive Story API.
#
# Hive Story API is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Story API is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Story API. If not, see <http://www.apache.org/licenses/>.

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

BASE_URL = "https://story.bemisc.com/api/"
""" The default base url to be used when no other
base url value is provided to the constructor """

class Api(appier.Api):
    """
    Implementation of the Story API specification
    for a simplified python client usage.
    """

    def __init__(self, *args, **kwargs):
        appier.Api.__init__(self, *args, **kwargs)
        self.base_url = appier.conf("STORY_BASE_URL", BASE_URL)
        self.key = appier.conf("STORY_KEY", None)
        self.base_url = kwargs.get("base_url", BASE_URL)

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
        if auth and self.key: headers["X-Secret-Key"] = self.key

    def ping(self):
        url = self.base_url + "ping"
        contents = self.get(url, auth = False)
        return contents
