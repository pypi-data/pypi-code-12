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
Rattail Model Importers
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model, auth
from rattail.importing import ToSQLAlchemy


class ToRattail(ToSQLAlchemy):
    """
    Base class for all Rattail model importers.
    """
    key = 'uuid'


class PersonImporter(ToRattail):
    """
    Person data importer.
    """
    model_class = model.Person


class PersonEmailAddressImporter(ToRattail):
    """
    Person email address data importer.
    """
    model_class = model.PersonEmailAddress


class PersonPhoneNumberImporter(ToRattail):
    """
    Person phone number data importer.
    """
    model_class = model.PersonPhoneNumber


class PersonMailingAddressImporter(ToRattail):
    """
    Person mailing address data importer.
    """
    model_class = model.PersonMailingAddress


class UserImporter(ToRattail):
    """
    User data importer.
    """
    model_class = model.User


class AdminUserImporter(UserImporter):
    """
    User data importer, plus 'admin' boolean field.
    """

    @property
    def supported_fields(self):
        return super(AdminUserImporter, self).supported_fields + ['admin']

    def get_admin(self, session=None):
        return auth.administrator_role(session or self.session)

    def normalize_local_object(self, user):
        data = super(AdminUserImporter, self).normalize_local_object(user)
        if 'admin' in self.fields:
            data['admin'] = self.get_admin() in user.roles
        return data

    def update_object(self, user, data, local_data=None):
        user = super(UserImporter, self).update_object(user, data, local_data)
        if user:
            if 'admin' in self.fields:
                admin = self.get_admin()
                if data['admin']:
                    if admin not in user.roles:
                        user.roles.append(admin)
                else:
                    if admin in user.roles:
                        user.roles.remove(admin)
            return user


class MessageImporter(ToRattail):
    """
    User message data importer.
    """
    model_class = model.Message


class MessageRecipientImporter(ToRattail):
    """
    User message recipient data importer.
    """
    model_class = model.MessageRecipient


class StoreImporter(ToRattail):
    """
    Store data importer.
    """
    model_class = model.Store


class StorePhoneNumberImporter(ToRattail):
    """
    Store phone data importer.
    """
    model_class = model.StorePhoneNumber


class EmployeeImporter(ToRattail):
    """
    Employee data importer.
    """
    model_class = model.Employee


class EmployeeStoreImporter(ToRattail):
    """
    Employee/store data importer.
    """
    model_class = model.EmployeeStore


class EmployeeDepartmentImporter(ToRattail):
    """
    Employee/department data importer.
    """
    model_class = model.EmployeeDepartment


class EmployeeEmailAddressImporter(ToRattail):
    """
    Employee email data importer.
    """
    model_class = model.EmployeeEmailAddress


class EmployeePhoneNumberImporter(ToRattail):
    """
    Employee phone data importer.
    """
    model_class = model.EmployeePhoneNumber


class ScheduledShiftImporter(ToRattail):
    """
    Imports employee scheduled shifts.
    """
    model_class = model.ScheduledShift


class WorkedShiftImporter(ToRattail):
    """
    Imports shifts worked by employees.
    """
    model_class = model.WorkedShift


class CustomerImporter(ToRattail):
    """
    Customer data importer.
    """
    model_class = model.Customer


class CustomerGroupImporter(ToRattail):
    """
    CustomerGroup data importer.
    """
    model_class = model.CustomerGroup


class CustomerGroupAssignmentImporter(ToRattail):
    """
    CustomerGroupAssignment data importer.
    """
    model_class = model.CustomerGroupAssignment


class CustomerPersonImporter(ToRattail):
    """
    CustomerPerson data importer.
    """
    model_class = model.CustomerPerson


class CustomerEmailAddressImporter(ToRattail):
    """
    Customer email address data importer.
    """
    model_class = model.CustomerEmailAddress


class CustomerPhoneNumberImporter(ToRattail):
    """
    Customer phone number data importer.
    """
    model_class = model.CustomerPhoneNumber


class VendorImporter(ToRattail):
    """
    Vendor data importer.
    """
    model_class = model.Vendor


class VendorEmailAddressImporter(ToRattail):
    """
    Vendor email data importer.
    """
    model_class = model.VendorEmailAddress


class VendorPhoneNumberImporter(ToRattail):
    """
    Vendor phone data importer.
    """
    model_class = model.VendorPhoneNumber


class VendorContactImporter(ToRattail):
    """
    Vendor contact data importer.
    """
    model_class = model.VendorContact


class DepartmentImporter(ToRattail):
    """
    Department data importer.
    """
    model_class = model.Department


class SubdepartmentImporter(ToRattail):
    """
    Subdepartment data importer.
    """
    model_class = model.Subdepartment


class CategoryImporter(ToRattail):
    """
    Category data importer.
    """
    model_class = model.Category


class FamilyImporter(ToRattail):
    """
    Family data importer.
    """
    model_class = model.Family


class ReportCodeImporter(ToRattail):
    """
    ReportCode data importer.
    """
    model_class = model.ReportCode


class DepositLinkImporter(ToRattail):
    """
    Deposit link data importer.
    """
    model_class = model.DepositLink


class TaxImporter(ToRattail):
    """
    Tax data importer.
    """
    model_class = model.Tax


class BrandImporter(ToRattail):
    """
    Brand data importer.
    """
    model_class = model.Brand


class ProductImporter(ToRattail):
    """
    Data importer for :class:`rattail.db.model.Product`.
    """
    model_class = model.Product


class ProductCodeImporter(ToRattail):
    """
    Data importer for :class:`rattail.db.model.ProductCode`.
    """
    model_class = model.ProductCode


class ProductCostImporter(ToRattail):
    """
    Data importer for :class:`rattail.db.model.ProductCost`.
    """
    model_class = model.ProductCost


class ProductPriceImporter(ToRattail):
    """
    Data importer for :class:`rattail.db.model.ProductPrice`.
    """
    model_class = model.ProductPrice
