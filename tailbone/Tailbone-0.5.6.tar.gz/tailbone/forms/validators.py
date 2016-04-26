# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2015 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Custom FormEncode Validators
"""

from __future__ import unicode_literals

from rattail.db import model

import formencode
from formencode import validators

from tailbone.db import Session


class ValidCustomer(validators.FancyValidator):
    """
    Validator for customer field.
    """

    def _to_python(self, value, state):
        if not value:
            return None
        customer = Session.query(model.Customer).get(value)
        if not customer:
            raise formencode.Invalid("Customer not found", value, state)
        return customer


class ValidProduct(validators.FancyValidator):
    """
    Validator for product field.
    """

    def _to_python(self, value, state):
        if not value:
            return None
        product = Session.query(model.Product).get(value)
        if not product:
            raise formencode.Invalid("Product not found", value, state)
        return product


class ValidUser(validators.FancyValidator):
    """
    Validator for product field.
    """

    def to_python(self, value, state):
        if not value:
            return None
        user = Session.query(model.User).get(value)
        if not user:
            raise formencode.Invalid("User not found.", value, state)
        return user
