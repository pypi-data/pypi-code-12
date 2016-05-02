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

from . import account
from . import address
from . import bag
from . import base
from . import category
from . import collection
from . import color
from . import country
from . import order
from . import product
from . import subscription
from . import voucher

from .account import AccountApi
from .address import AddressApi
from .bag import BagApi
from .base import Api
from .category import CategoryApi
from .collection import CollectionApi
from .color import ColorApi
from .country import CountryApi
from .order import OrderApi
from .product import ProductApi
from .subscription import SubscriptionApi
from .voucher import VoucherApi
