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
Rattail -> Rattail Data Import
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import Session, newimporting as importing
from rattail.util import OrderedDict


class RattailImportHandler(importing.SQLAlchemyImportHandler):
    """
    Handler for Rattail -> Rattail data import.
    """
    host_title = "Rattail"
    dbkey = 'host'

    def make_host_session(self):
        return Session(bind=self.config.rattail_engines[self.dbkey])

    def get_importers(self):
        importers = OrderedDict()
        importers['Person'] = PersonImporter
        importers['PersonEmailAddress'] = PersonEmailAddressImporter
        importers['PersonPhoneNumber'] = PersonPhoneNumberImporter
        importers['PersonMailingAddress'] = PersonMailingAddressImporter
        importers['User'] = UserImporter
        importers['Message'] = MessageImporter
        importers['MessageRecipient'] = MessageRecipientImporter
        importers['Store'] = StoreImporter
        importers['StorePhoneNumber'] = StorePhoneNumberImporter
        importers['Employee'] = EmployeeImporter
        importers['EmployeeStore'] = EmployeeStoreImporter
        importers['EmployeeDepartment'] = EmployeeDepartmentImporter
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

    def get_importer_kwargs(self, key):
        kwargs = super(RattailImportHandler, self).get_importer_kwargs(key)
        kwargs['dbkey'] = self.dbkey
        return kwargs


class RattailImporter(importing.SQLAlchemyImporter):
    """
    Base class for Rattail -> Rattail data importers.
    """

    @property
    def host_model_class(self):
        return self.model_class

    @property
    def supported_fields(self):
        """
        We only need to support the simple fields in a Rattail->Rattail import,
        since all relevant tables should be covered and therefore no need to do
        crazy foreign key acrobatics etc.
        """
        return self.simple_fields

    @property
    def normalize_progress_message(self):
        return "Reading {} data from '{}' db".format(self.model_name, self.dbkey)

    def query(self):
        query = super(RattailImporter, self).query()
        options = self.cache_query_options()
        if options:
            for option in options:
                query = query.options(option)
        return query

    def normalize_source_record(self, host_instance):
        return self.normalize_instance(host_instance)


class PersonImporter(RattailImporter, importing.model.PersonImporter):
    pass

class PersonEmailAddressImporter(RattailImporter, importing.model.PersonEmailAddressImporter):
    pass

class PersonPhoneNumberImporter(RattailImporter, importing.model.PersonPhoneNumberImporter):
    pass

class PersonMailingAddressImporter(RattailImporter, importing.model.PersonMailingAddressImporter):
    pass

class UserImporter(RattailImporter, importing.model.UserImporter):
    pass

class MessageImporter(RattailImporter, importing.model.MessageImporter):
    pass

class MessageRecipientImporter(RattailImporter, importing.model.MessageRecipientImporter):
    pass

class StoreImporter(RattailImporter, importing.model.StoreImporter):
    pass

class StorePhoneNumberImporter(RattailImporter, importing.model.StorePhoneNumberImporter):
    pass

class EmployeeImporter(RattailImporter, importing.model.EmployeeImporter):
    pass

class EmployeeStoreImporter(RattailImporter, importing.model.EmployeeStoreImporter):
    pass

class EmployeeDepartmentImporter(RattailImporter, importing.model.EmployeeDepartmentImporter):
    pass

class EmployeeEmailAddressImporter(RattailImporter, importing.model.EmployeeEmailAddressImporter):
    pass

class EmployeePhoneNumberImporter(RattailImporter, importing.model.EmployeePhoneNumberImporter):
    pass

class ScheduledShiftImporter(RattailImporter, importing.model.ScheduledShiftImporter):
    pass

class WorkedShiftImporter(RattailImporter, importing.model.WorkedShiftImporter):
    pass

class CustomerImporter(RattailImporter, importing.model.CustomerImporter):
    pass

class CustomerGroupImporter(RattailImporter, importing.model.CustomerGroupImporter):
    pass

class CustomerGroupAssignmentImporter(RattailImporter, importing.model.CustomerGroupAssignmentImporter):
    pass

class CustomerPersonImporter(RattailImporter, importing.model.CustomerPersonImporter):
    pass

class CustomerEmailAddressImporter(RattailImporter, importing.model.CustomerEmailAddressImporter):
    pass

class CustomerPhoneNumberImporter(RattailImporter, importing.model.CustomerPhoneNumberImporter):
    pass

class VendorImporter(RattailImporter, importing.model.VendorImporter):
    pass

class VendorEmailAddressImporter(RattailImporter, importing.model.VendorEmailAddressImporter):
    pass

class VendorPhoneNumberImporter(RattailImporter, importing.model.VendorPhoneNumberImporter):
    pass

class VendorContactImporter(RattailImporter, importing.model.VendorContactImporter):
    pass

class DepartmentImporter(RattailImporter, importing.model.DepartmentImporter):
    pass

class SubdepartmentImporter(RattailImporter, importing.model.SubdepartmentImporter):
    pass

class CategoryImporter(RattailImporter, importing.model.CategoryImporter):
    pass

class FamilyImporter(RattailImporter, importing.model.FamilyImporter):
    pass

class ReportCodeImporter(RattailImporter, importing.model.ReportCodeImporter):
    pass

class DepositLinkImporter(RattailImporter, importing.model.DepositLinkImporter):
    pass

class TaxImporter(RattailImporter, importing.model.TaxImporter):
    pass

class BrandImporter(RattailImporter, importing.model.BrandImporter):
    pass

class ProductImporter(RattailImporter, importing.model.ProductImporter):
    pass

class ProductCodeImporter(RattailImporter, importing.model.ProductCodeImporter):
    pass

class ProductCostImporter(RattailImporter, importing.model.ProductCostImporter):
    pass

class ProductPriceImporter(RattailImporter, importing.model.ProductPriceImporter):
    pass
