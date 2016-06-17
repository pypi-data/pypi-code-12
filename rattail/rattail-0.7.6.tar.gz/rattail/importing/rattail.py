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
Rattail -> Rattail data import
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import Session
from rattail.importing import model
from rattail.importing.handlers import FromSQLAlchemyHandler, ToSQLAlchemyHandler
from rattail.importing.sqlalchemy import FromSQLAlchemy
from rattail.util import OrderedDict


class FromRattailHandler(FromSQLAlchemyHandler):
    """
    Base class for import handlers which target a Rattail database on the local side.
    """
    host_title = "Rattail"

    def make_host_session(self):
        return Session()


class ToRattailHandler(ToSQLAlchemyHandler):
    """
    Base class for import handlers which target a Rattail database on the local side.
    """
    local_title = "Rattail"

    def make_session(self):
        return Session()


class FromRattailToRattail(FromRattailHandler, ToRattailHandler):
    """
    Handler for Rattail -> Rattail data import.
    """
    local_title = "Rattail (local)"
    dbkey = 'host'

    @property
    def host_title(self):
        return "Rattail ({})".format(self.dbkey)

    def make_host_session(self):
        return Session(bind=self.config.rattail_engines[self.dbkey])

    def get_importers(self):
        importers = OrderedDict()
        importers['Person'] = PersonImporter
        importers['PersonEmailAddress'] = PersonEmailAddressImporter
        importers['PersonPhoneNumber'] = PersonPhoneNumberImporter
        importers['PersonMailingAddress'] = PersonMailingAddressImporter
        importers['User'] = UserImporter
        importers['AdminUser'] = AdminUserImporter
        importers['Message'] = MessageImporter
        importers['MessageRecipient'] = MessageRecipientImporter
        importers['Store'] = StoreImporter
        importers['StorePhoneNumber'] = StorePhoneNumberImporter
        importers['Employee'] = EmployeeImporter
        importers['EmployeeStore'] = EmployeeStoreImporter
        importers['EmployeeEmailAddress'] = EmployeeEmailAddressImporter
        importers['EmployeePhoneNumber'] = EmployeePhoneNumberImporter
        importers['ScheduledShift'] = ScheduledShiftImporter
        importers['WorkedShift'] = WorkedShiftImporter
        importers['Customer'] = CustomerImporter
        importers['CustomerGroup'] = CustomerGroupImporter
        importers['CustomerGroupAssignment'] = CustomerGroupAssignmentImporter
        importers['CustomerPerson'] = CustomerPersonImporter
        importers['CustomerEmailAddress'] = CustomerEmailAddressImporter
        importers['CustomerPhoneNumber'] = CustomerPhoneNumberImporter
        importers['Vendor'] = VendorImporter
        importers['VendorEmailAddress'] = VendorEmailAddressImporter
        importers['VendorPhoneNumber'] = VendorPhoneNumberImporter
        importers['VendorContact'] = VendorContactImporter
        importers['Department'] = DepartmentImporter
        importers['EmployeeDepartment'] = EmployeeDepartmentImporter
        importers['Subdepartment'] = SubdepartmentImporter
        importers['Category'] = CategoryImporter
        importers['Family'] = FamilyImporter
        importers['ReportCode'] = ReportCodeImporter
        importers['DepositLink'] = DepositLinkImporter
        importers['Tax'] = TaxImporter
        importers['Brand'] = BrandImporter
        importers['Product'] = ProductImporter
        importers['ProductCode'] = ProductCodeImporter
        importers['ProductCost'] = ProductCostImporter
        importers['ProductPrice'] = ProductPriceImporter
        return importers

    def get_default_keys(self):
        keys = self.get_importer_keys()
        if 'AdminUser' in keys:
            keys.remove('AdminUser')
        return keys


class FromRattail(FromSQLAlchemy):
    """
    Base class for Rattail -> Rattail data importers.
    """

    @property
    def host_model_class(self):
        return self.model_class

    def normalize_host_object(self, obj):
        return self.normalize_local_object(obj)


class PersonImporter(FromRattail, model.PersonImporter):
    pass

class PersonEmailAddressImporter(FromRattail, model.PersonEmailAddressImporter):
    pass

class PersonPhoneNumberImporter(FromRattail, model.PersonPhoneNumberImporter):
    pass

class PersonMailingAddressImporter(FromRattail, model.PersonMailingAddressImporter):
    pass

class UserImporter(FromRattail, model.UserImporter):
    pass

class AdminUserImporter(FromRattail, model.AdminUserImporter):

    def normalize_host_object(self, user):
        data = super(AdminUserImporter, self).normalize_local_object(user) # sic
        if 'admin' in self.fields:
            data['admin'] = self.get_admin(self.host_session) in user.roles
        return data


class MessageImporter(FromRattail, model.MessageImporter):
    pass

class MessageRecipientImporter(FromRattail, model.MessageRecipientImporter):
    pass

class StoreImporter(FromRattail, model.StoreImporter):
    pass

class StorePhoneNumberImporter(FromRattail, model.StorePhoneNumberImporter):
    pass

class EmployeeImporter(FromRattail, model.EmployeeImporter):
    pass

class EmployeeStoreImporter(FromRattail, model.EmployeeStoreImporter):
    pass

class EmployeeDepartmentImporter(FromRattail, model.EmployeeDepartmentImporter):
    pass

class EmployeeEmailAddressImporter(FromRattail, model.EmployeeEmailAddressImporter):
    pass

class EmployeePhoneNumberImporter(FromRattail, model.EmployeePhoneNumberImporter):
    pass

class ScheduledShiftImporter(FromRattail, model.ScheduledShiftImporter):
    pass

class WorkedShiftImporter(FromRattail, model.WorkedShiftImporter):
    pass

class CustomerImporter(FromRattail, model.CustomerImporter):
    pass

class CustomerGroupImporter(FromRattail, model.CustomerGroupImporter):
    pass

class CustomerGroupAssignmentImporter(FromRattail, model.CustomerGroupAssignmentImporter):
    pass

class CustomerPersonImporter(FromRattail, model.CustomerPersonImporter):
    pass

class CustomerEmailAddressImporter(FromRattail, model.CustomerEmailAddressImporter):
    pass

class CustomerPhoneNumberImporter(FromRattail, model.CustomerPhoneNumberImporter):
    pass

class VendorImporter(FromRattail, model.VendorImporter):
    pass

class VendorEmailAddressImporter(FromRattail, model.VendorEmailAddressImporter):
    pass

class VendorPhoneNumberImporter(FromRattail, model.VendorPhoneNumberImporter):
    pass

class VendorContactImporter(FromRattail, model.VendorContactImporter):
    pass

class DepartmentImporter(FromRattail, model.DepartmentImporter):
    pass

class SubdepartmentImporter(FromRattail, model.SubdepartmentImporter):
    pass

class CategoryImporter(FromRattail, model.CategoryImporter):
    pass

class FamilyImporter(FromRattail, model.FamilyImporter):
    pass

class ReportCodeImporter(FromRattail, model.ReportCodeImporter):
    pass

class DepositLinkImporter(FromRattail, model.DepositLinkImporter):
    pass

class TaxImporter(FromRattail, model.TaxImporter):
    pass

class BrandImporter(FromRattail, model.BrandImporter):
    pass

class ProductImporter(FromRattail, model.ProductImporter):
    pass

class ProductCodeImporter(FromRattail, model.ProductCodeImporter):
    pass

class ProductCostImporter(FromRattail, model.ProductCostImporter):
    pass

class ProductPriceImporter(FromRattail, model.ProductPriceImporter):
    pass
