# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2016 Lance Edgar
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

from __future__ import unicode_literals, absolute_import

from rattail.db import model

import formencode as fe

from tailbone.db import Session


class ModelValidator(fe.validators.FancyValidator):
    """
    Generic validator for data model reference fields.
    """
    model_class = None

    @property
    def model_name(self):
        self.model_class.__name__

    def _to_python(self, value, state):
        if value:
            obj = Session.query(self.model_class).get(value)
            if obj:
                return obj
            raise fe.Invalid("{} not found".format(self.model_name), value, state)

    def _from_python(self, value, state):
        obj = value
        if not obj:
            return ''
        return obj.uuid

    def validate_python(self, value, state):
        obj = value
        if obj is not None and not isinstance(obj, self.model_class):
            raise fe.Invalid("Value must be a valid {} object".format(self.model_name), value, state)


class ValidStore(ModelValidator):
    """
    Validator for store field.
    """
    model_class = model.Store


class ValidCustomer(ModelValidator):
    """
    Validator for customer field.
    """
    model_class = model.Customer


class ValidDepartment(ModelValidator):
    """
    Validator for department field.
    """
    model_class = model.Department


class ValidEmployee(ModelValidator):
    """
    Validator for employee field.
    """
    model_class = model.Employee


class ValidProduct(ModelValidator):
    """
    Validator for product field.
    """
    model_class = model.Product


class ValidUser(ModelValidator):
    """
    Validator for user field.
    """
    model_class = model.User
