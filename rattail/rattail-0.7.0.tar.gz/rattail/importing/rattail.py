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

from rattail import importing
from rattail.db import Session
from rattail.util import OrderedDict


class FromRattailToRattail(importing.FromSQLAlchemyHandler, importing.ToSQLAlchemyHandler):
    """
    Handler for Rattail -> Rattail data import.
    """
    local_title = "Rattail (local)"
    dbkey = 'host'

    @property
    def host_title(self):
        return "Rattail ({})".format(self.dbkey)

    def make_session(self):
        return Session()

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


class FromRattail(importing.FromSQLAlchemy):
    """
    Base class for Rattail -> Rattail data importers.
    """

    @property
    def host_model_class(self):
        return self.model_class

    def normalize_host_object(self, obj):
        return self.normalize_local_object(obj)


class PersonImporter(FromRattail, importing.model.PersonImporter):
    pass

class PersonEmailAddressImporter(FromRattail, importing.model.PersonEmailAddressImporter):
    pass

class PersonPhoneNumberImporter(FromRattail, importing.model.PersonPhoneNumberImporter):
    pass

class PersonMailingAddressImporter(FromRattail, importing.model.PersonMailingAddressImporter):
    pass

class UserImporter(FromRattail, importing.model.UserImporter):
    pass

class AdminUserImporter(FromRattail, importing.model.AdminUserImporter):

    def normalize_host_object(self, user):
        data = super(AdminUserImporter, self).normalize_local_object(user) # sic
        if 'admin' in self.fields:
            data['admin'] = self.get_admin(self.host_session) in user.roles
        return data


class MessageImporter(FromRattail, importing.model.MessageImporter):
    pass

class MessageRecipientImporter(FromRattail, importing.model.MessageRecipientImporter):
    pass

class StoreImporter(FromRattail, importing.model.StoreImporter):
    pass

class StorePhoneNumberImporter(FromRattail, importing.model.StorePhoneNumberImporter):
    pass

class EmployeeImporter(FromRattail, importing.model.EmployeeImporter):
    pass

class EmployeeStoreImporter(FromRattail, importing.model.EmployeeStoreImporter):
    pass

class EmployeeDepartmentImporter(FromRattail, importing.model.EmployeeDepartmentImporter):
    pass

class EmployeeEmailAddressImporter(FromRattail, importing.model.EmployeeEmailAddressImporter):
    pass

class EmployeePhoneNumberImporter(FromRattail, importing.model.EmployeePhoneNumberImporter):
    pass

class ScheduledShiftImporter(FromRattail, importing.model.ScheduledShiftImporter):
    pass

class WorkedShiftImporter(FromRattail, importing.model.WorkedShiftImporter):
    pass

class CustomerImporter(FromRattail, importing.model.CustomerImporter):
    pass

class CustomerGroupImporter(FromRattail, importing.model.CustomerGroupImporter):
    pass

class CustomerGroupAssignmentImporter(FromRattail, importing.model.CustomerGroupAssignmentImporter):
    pass

class CustomerPersonImporter(FromRattail, importing.model.CustomerPersonImporter):
    pass

class CustomerEmailAddressImporter(FromRattail, importing.model.CustomerEmailAddressImporter):
    pass

class CustomerPhoneNumberImporter(FromRattail, importing.model.CustomerPhoneNumberImporter):
    pass

class VendorImporter(FromRattail, importing.model.VendorImporter):
    pass

class VendorEmailAddressImporter(FromRattail, importing.model.VendorEmailAddressImporter):
    pass

class VendorPhoneNumberImporter(FromRattail, importing.model.VendorPhoneNumberImporter):
    pass

class VendorContactImporter(FromRattail, importing.model.VendorContactImporter):
    pass

class DepartmentImporter(FromRattail, importing.model.DepartmentImporter):
    pass

class SubdepartmentImporter(FromRattail, importing.model.SubdepartmentImporter):
    pass

class CategoryImporter(FromRattail, importing.model.CategoryImporter):
    pass

class FamilyImporter(FromRattail, importing.model.FamilyImporter):
    pass

class ReportCodeImporter(FromRattail, importing.model.ReportCodeImporter):
    pass

class DepositLinkImporter(FromRattail, importing.model.DepositLinkImporter):
    pass

class TaxImporter(FromRattail, importing.model.TaxImporter):
    pass

class BrandImporter(FromRattail, importing.model.BrandImporter):
    pass

class ProductImporter(FromRattail, importing.model.ProductImporter):
    pass

class ProductCodeImporter(FromRattail, importing.model.ProductCodeImporter):
    pass

class ProductCostImporter(FromRattail, importing.model.ProductCostImporter):
    pass

class ProductPriceImporter(FromRattail, importing.model.ProductPriceImporter):
    pass
