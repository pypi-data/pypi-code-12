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

from sqlalchemy import orm

from rattail.db import model, auth
from rattail.importing import ToSQLAlchemy
from rattail.db.util import format_phone_number, normalize_phone_number


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

    @property
    def supported_fields(self):
        return self.simple_fields + [
            'preferred',
        ]

    def normalize_local_object(self, email):
        data = super(PersonEmailAddressImporter, self).normalize_local_object(email)
        if 'preferred' in self.fields:
            data['preferred'] = email.preference == 1
        return data

    def update_object(self, email, data, local_data=None):
        email = super(PersonEmailAddressImporter, self).update_object(email, data, local_data)
        if 'preferred' in self.fields:
            if data['preferred']:
                if email.preference != 1:
                    person = email.person
                    if not person:
                        person = self.session.query(model.Person).get(email.parent_uuid)
                    if email in person.emails:
                        person.emails.remove(email)
                    person.emails.insert(0, email)
                    person.emails.reorder()
            else:
                if email.preference == 1:
                    person = email.person
                    if not person:
                        person = self.session.query(model.Person).get(email.parent_uuid)
                    if len(person.emails) > 1:
                        person.emails.remove(email)
                        person.emails.append(email)
                        person.emails.reorder()

        # If this is a new record, we may still need to establish its preference.
        if email.preference is None:
            person = email.person
            if not person:
                person = self.session.query(model.Person).get(email.parent_uuid)
            if email not in person.emails:
                person.emails.append(email)
            person.emails.reorder()

        return email


class PersonPhoneNumberImporter(ToRattail):
    """
    Person phone number data importer.
    """
    model_class = model.PersonPhoneNumber

    @property
    def supported_fields(self):
        return self.simple_fields + [
            'normalized_number',
            'preferred',
        ]

    def format_number(self, number):
        return format_phone_number(number)

    def normalize_number(self, number):
        return normalize_phone_number(number)

    def normalize_local_object(self, phone):
        data = super(PersonPhoneNumberImporter, self).normalize_local_object(phone)
        if 'normalized_number' in self.fields:
            data['normalized_number'] = self.normalize_number(phone.number)
        if 'preferred' in self.fields:
            data['preferred'] = phone.preference == 1
        return data

    def update_object(self, phone, data, local_data=None):
        phone = super(PersonPhoneNumberImporter, self).update_object(phone, data, local_data)
        if 'preferred' in self.fields:
            if data['preferred']:
                if phone.preference != 1:
                    person = phone.person
                    if not person:
                        person = self.session.query(model.Person).get(phone.parent_uuid)
                    if phone in person.phones:
                        person.phones.remove(phone)
                    person.phones.insert(0, phone)
                    person.phones.reorder()
            else:
                if phone.preference == 1:
                    person = phone.person
                    if not person:
                        person = self.session.query(model.Person).get(phone.parent_uuid)
                    if len(person.phones) > 1:
                        person.phones.remove(phone)
                        person.phones.append(phone)
                        person.phones.reorder()

        # If this is a new record, we may still need to establish its preference.
        if phone.preference is None:
            person = phone.person
            if not person:
                person = self.session.query(model.Person).get(phone.parent_uuid)
            if phone not in person.phones:
                person.phones.append(phone)
            person.phones.reorder()

        return phone


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
    person_fields = [
        'first_name',
        'last_name',
        'full_name',
    ]

    @property
    def supported_fields(self):
        return self.simple_fields + self.person_fields + [
            'phone_number',
        ]

    @property
    def person_fields_active(self):
        for field in self.person_fields:
            if field in self.fields:
                return True
        return False

    def cache_query_options(self):
        options = []
        if self.person_fields_active:
            options.append(orm.joinedload(model.Employee.person))
        if 'phone_number' in self.fields:
            options.append(orm.joinedload(model.Employee.phones))
        return options

    def normalize_local_object(self, employee):
        data = super(EmployeeImporter, self).normalize_local_object(employee)

        if self.person_fields_active:
            person = employee.person
            if 'first_name' in self.fields:
                data['first_name'] = person.first_name
            if 'last_name' in self.fields:
                data['last_name'] = person.last_name
            if 'full_name' in self.fields:
                data['full_name'] = person.display_name

        if 'phone_number' in self.fields:
            data['phone_number'] = None
            for phone in employee.phones:
                if phone.type == 'Home':
                    data['phone_number'] = phone.number
                    break

        return data

    def update_object(self, employee, data, local_data=None):
        employee = super(EmployeeImporter, self).update_object(employee, data, local_data)

        if self.person_fields_active:
            person = employee.person
            if 'first_name' in self.fields and person.first_name != data['first_name']:
                person.first_name = data['first_name']
            if 'last_name' in self.fields and person.last_name != data['last_name']:
                person.last_name = data['last_name']
            if 'full_name' in self.fields and person.display_name != data['full_name']:
                person.display_name = data['full_name']

        if 'phone_number' in self.fields:
            number = data['phone_number']
            if number:
                found = False
                for phone in employee.phones:
                    if phone.type == 'Home':
                        if phone.number != number:
                            phone.number = number
                        found = True
                        break
                if not found:
                    employee.add_phone_number(number, type='Home')
            else:
                for phone in list(employee.phones):
                    if phone.type == 'Home':
                        employee.phones.remove(phone)

        return employee


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
