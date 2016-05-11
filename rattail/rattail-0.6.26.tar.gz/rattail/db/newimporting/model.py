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

import logging

from sqlalchemy import orm

from rattail.db import model, cache, auth
from rattail.db.newimporting import Importer
from rattail.db.util import normalize_phone_number, format_phone_number


log = logging.getLogger(__name__)


class PersonImporter(Importer):
    """
    Person data importer.
    """
    model_class = model.Person


class PersonEmailAddressImporter(Importer):
    """
    Person email address data importer.
    """
    model_class = model.PersonEmailAddress

    @property
    def supported_fields(self):
        return self.simple_fields + [
            'preferred',
        ]

    def normalize_instance(self, email):
        data = super(PersonEmailAddressImporter, self).normalize_instance(email)
        data['preferred'] = email.preference == 1
        return data

    def update_instance(self, email, data, inst_data=None):
        email = super(PersonEmailAddressImporter, self).update_instance(email, data, inst_data)
        if 'preferred' in self.fields:
            if data['preferred']:
                if email.preference != 1:
                    person = email.person
                    if not person:
                        person = self.session.query(model.Person).get(email.parent_uuid)
                        assert person, "hm: " + email.parent_uuid
                    if email in person.emails:
                        person.emails.remove(email)
                    person.emails.insert(0, email)
                    person.emails.reorder()
            else:
                if email.preference == 1:
                    person = email.person
                    if not person:
                        person = self.session.query(model.Person).get(email.parent_uuid)
                        assert person, "hm: " + email.parent_uuid
                    if len(person.emails) > 1:
                        person.emails.remove(email)
                        person.emails.append(email)
                        person.emails.reorder()

        # If this is a new record, we may still need to establish its preference.
        if email.preference is None:
            person = email.person
            if not person:
                person = self.session.query(model.Person).get(email.parent_uuid)
                assert person, "hm: " + email.parent_uuid
            if email not in person.emails:
                person.emails.append(email)
            person.emails.reorder()

        return email


class PersonPhoneNumberImporter(Importer):
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

    def normalize_number(self, number):
        return normalize_phone_number(number)

    def format_number(self, number):
        return format_phone_number(number)

    def normalize_instance(self, phone):
        data = super(PersonPhoneNumberImporter, self).normalize_instance(phone)
        if 'normalized_number' in self.fields:
            data['normalized_number'] = self.normalize_number(phone.number)
        if 'preferred' in self.fields:
            data['preferred'] = phone.preference == 1
        return data

    def update_instance(self, phone, data, inst_data=None):
        phone = super(PersonPhoneNumberImporter, self).update_instance(phone, data, inst_data)
        if 'preferred' in self.fields:
            if data['preferred']:
                if phone.preference != 1:
                    person = phone.person
                    if not person:
                        person = self.session.query(model.Person).get(phone.parent_uuid)
                        assert person, "hm: " + phone.parent_uuid
                    if phone in person.phones:
                        person.phones.remove(phone)
                    person.phones.insert(0, phone)
                    person.phones.reorder()
            else:
                if phone.preference == 1:
                    person = phone.person
                    if not person:
                        person = self.session.query(model.Person).get(phone.parent_uuid)
                        assert person, "hm: " + phone.parent_uuid
                    if len(person.phones) > 1:
                        person.phones.remove(phone)
                        person.phones.append(phone)
                        person.phones.reorder()

        # If this is a new record, we may still need to establish its preference.
        if phone.preference is None:
            person = phone.person
            if not person:
                person = self.session.query(model.Person).get(phone.parent_uuid)
                assert person, "hm: " + phone.parent_uuid
            if phone not in person.phones:
                person.phones.append(phone)
            person.phones.reorder()

        return phone


class PersonMailingAddressImporter(Importer):
    """
    Person mailing address data importer.
    """
    model_class = model.PersonMailingAddress


class UserImporter(Importer):
    """
    User data importer.
    """
    model_class = model.User

    @property
    def supported_fields(self):
        return self.simple_fields + [
            'admin',
        ]

    def setup(self):
        self.admin = auth.administrator_role(self.session)

    def normalize_instance(self, user):
        data = super(UserImporter, self).normalize_instance(user)
        if 'admin' in self.fields:
            data['admin'] = self.admin in user.roles
        return data

    def update_instance(self, user, data, inst_data=None):
        user = super(UserImporter, self).update_instance(user, data, inst_data)
        if 'admin' in self.fields:
            if data['admin']:
                if self.admin not in user.roles:
                    user.roles.append(self.admin)
            else:
                if self.admin in user.roles:
                    user.roles.remove(self.admin)
        return user


class MessageImporter(Importer):
    """
    User message data importer.
    """
    model_class = model.Message


class MessageRecipientImporter(Importer):
    """
    User message recipient data importer.
    """
    model_class = model.MessageRecipient


class StoreImporter(Importer):
    """
    Store data importer.
    """
    model_class = model.Store

    @property
    def supported_fields(self):
        return self.simple_fields + [
            'phone_number',
            'fax_number',
        ]

    def cache_query_options(self):
        if 'phone_number' in self.fields or 'fax_number' in self.fields:
            return [orm.joinedload(model.Store.phones)]

    def normalize_instance(self, store):
        data = super(StoreImporter, self).normalize_instance(store)

        if 'phone_number' in self.fields:
            data['phone_number'] = None
            for phone in store.phones:
                if phone.type == 'Voice':
                    data['phone_number'] = phone.number
                    break

        if 'fax_number' in self.fields:
            data['fax_number'] = None
            for phone in store.phones:
                if phone.type == 'Fax':
                    data['fax_number'] = phone.number
                    break

        return data

    def update_instance(self, store, data, inst_data=None):
        store = super(StoreImporter, self).update_instance(store, data, inst_data)

        if 'phone_number' in self.fields:
            number = data['phone_number'] or None
            if number:
                found = False
                for phone in store.phones:
                    if phone.type == 'Voice':
                        if phone.number != number:
                            phone.number = number
                        found = True
                        break
                if not found:
                    store.add_phone_number(number, type='Voice')
            else:
                for phone in list(store.phones):
                    if phone.type == 'Voice':
                        store.phones.remove(phone)

        if 'fax_number' in self.fields:
            number = data['fax_number'] or None
            if number:
                found = False
                for phone in store.phones:
                    if phone.type == 'Fax':
                        if phone.number != number:
                            phone.number = number
                        found = True
                        break
                if not found:
                    store.add_phone_number(number, type='Fax')
            else:
                for phone in list(store.phones):
                    if phone.type == 'Fax':
                        store.phones.remove(phone)

        return store


class StorePhoneNumberImporter(Importer):
    """
    Store phone data importer.
    """
    model_class = model.StorePhoneNumber


class EmployeeImporter(Importer):
    """
    Employee data importer.
    """
    model_class = model.Employee

    @property
    def supported_fields(self):
        return self.simple_fields + [
            'customer_id',
            'first_name',
            'last_name',
            'full_name',
            'phone_number',
            'phone_number_2',
            'email_address',
        ]

    def setup(self):
        if 'customer_id' in self.fields:
            self.customers = cache.cache_model(self.session, model.Customer, key='id',
                                               progress=self.progress)

    def cache_query_options(self):
        return [
            orm.joinedload(model.Employee.person).joinedload(model.Person._customers),
            orm.joinedload(model.Employee.phones),
            orm.joinedload(model.Employee.email),
        ]

    def normalize_instance(self, employee):
        data = super(EmployeeImporter, self).normalize_instance(employee)

        if set(self.fields) | set(['customer_id', 'first_name', 'last_name', 'full_name']):
            if not employee.person:
                self.session.flush()
                assert employee.person
            person = employee.person
            self.newval(data, 'first_name', person.first_name)
            self.newval(data, 'last_name', person.last_name)
            self.newval(data, 'full_name', person.display_name)
            if 'customer_id' in self.fields:
                customer = person.customers[0] if person.customers else None
                data['customer_id'] = customer.id if customer else None

        if 'phone_number' in self.fields:
            data['phone_number'] = None
            for phone in employee.phones:
                if phone.type == 'Home':
                    data['phone_number'] = phone.number
                    break

        if 'phone_number_2' in self.fields:
            data['phone_number_2'] = None
            first = False
            for phone in employee.phones:
                if phone.type == 'Home':
                    if first:
                        data['phone_number_2'] = phone.number
                        break
                    first = True

        if 'email_address' in self.fields:
            email = employee.email
            data['email_address'] = email.address if email else None

        return data

    def update_instance(self, employee, data, inst_data=None):
        employee = super(EmployeeImporter, self).update_instance(employee, data, inst_data)
        person = employee.person

        if 'first_name' in self.fields:
            employee.first_name = data['first_name']
        if 'last_name' in self.fields:
            employee.last_name = data['last_name']

        if 'full_name' in self.fields:
            if person.display_name != data['full_name']:
                person.display_name = data['full_name']

        if 'customer_id' in self.fields:
            id_ = data['customer_id']
            if id_:
                customer = self.customers.get(id_)
                if not customer:
                    customer = model.Customer()
                    customer.id = id_
                    customer.name = employee.display_name
                    self.session.add(customer)
                    self.customers[customer.id] = customer
                if person not in customer.people:
                    customer.people.append(person)
            else:
                for customer in list(person.customers):
                    if len(customer.people) > 1:
                        if person in customer.people:
                            customer.people.remove(person)

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

        if 'phone_number_2' in self.fields:
            number = data['phone_number_2']
            if number:
                found = False
                first = False
                for phone in employee.phones:
                    if phone.type == 'Home':
                        if first:
                            if phone.number != number:
                                phone.number = number
                            found = True
                            break
                        first = True
                if not found:
                    employee.add_phone_number(number, type='Home')
            else:
                first = False
                for phone in list(employee.phones):
                    if phone.type == 'Home':
                        if first:
                            employee.phones.remove(phone)
                            break
                        first = True

        if 'email_address' in self.fields:
            address = data['email_address']
            if address:
                if employee.email:
                    if employee.email.address != address:
                        employee.email.address = address
                else:
                    employee.add_email_address(address)
            else:
                if len(employee.emails):
                    del employee.emails[:]

        return employee


class EmployeeStoreImporter(Importer):
    """
    Employee/store data importer.
    """
    model_class = model.EmployeeStore


class EmployeeDepartmentImporter(Importer):
    """
    Employee/department data importer.
    """
    model_class = model.EmployeeDepartment


class EmployeeEmailAddressImporter(Importer):
    """
    Employee email data importer.
    """
    model_class = model.EmployeeEmailAddress


class EmployeePhoneNumberImporter(Importer):
    """
    Employee phone data importer.
    """
    model_class = model.EmployeePhoneNumber


class ScheduledShiftImporter(Importer):
    """
    Imports employee scheduled shifts.
    """
    model_class = model.ScheduledShift


class WorkedShiftImporter(Importer):
    """
    Imports shifts worked by employees.
    """
    model_class = model.WorkedShift


class CustomerImporter(Importer):
    """
    Customer data importer.
    """
    model_class = model.Customer

    @property
    def supported_fields(self):
        return self.simple_fields + [
            'first_name',
            'last_name',
            'phone_number',
            'phone_number_2',
            'email_address',
            'group_id',
            'group_id_2',
        ]

    def setup(self):
        if 'group_id' in self.fields or 'group_id_2' in self.fields:
            self.groups = cache.cache_model(self.session, model.CustomerGroup, key='id',
                                            progress=self.progress)

    def cache_query_options(self):
        options = []
        if 'first_name' in self.fields or 'last_name' in self.fields:
            options.append(orm.joinedload(model.Customer._people).joinedload(model.CustomerPerson.person))
        if 'phone_number' in self.fields or 'phone_number_2' in self.fields:
            options.append(orm.joinedload(model.Customer.phones))
        if 'email_address' in self.fields:
            options.append(orm.joinedload(model.Customer.email))
        if 'group_id' in self.fields or 'group_id_2' in self.fields:
            options.append(orm.joinedload_all(model.Customer._groups, model.CustomerGroupAssignment.group))
        return options

    def normalize_instance(self, customer):
        data = super(CustomerImporter, self).normalize_instance(customer)
        if 'first_name' in self.fields or 'last_name' in self.fields:
            person = customer.people[0] if customer.people else None
            self.newval(data, 'first_name', person.first_name if person else None)
            self.newval(data, 'last_name', person.last_name if person else None)

        if 'phone_number' in self.fields or 'phone_number_2' in self.fields:
            phones = filter(lambda p: p.type == 'Voice', customer.phones)
            self.newval(data, 'phone_number', phones[0].number if phones else None)
            self.newval(data, 'phone_number_2', phones[1].number if len(phones) > 1 else None)

        if 'email_address' in self.fields:
            email = customer.email
            data['email_address'] = email.address if email else None

        if 'group_id' in self.fields:
            group = customer.groups[0] if customer.groups else None
            data['group_id'] = group.id if group else None

        if 'group_id_2' in self.fields:
            group = customer.groups[1] if customer.groups and len(customer.groups) > 1 else None
            data['group_id_2'] = group.id if group else None

        return data

    def update_instance(self, customer, data, instance_data=None):
        customer = super(CustomerImporter, self).update_instance(customer, data, instance_data)

        if 'first_name' in self.fields or 'last_name' in self.fields:
            first_name = data['first_name']
            last_name = data['last_name']
            if not customer.people:
                customer.people.append(model.Person())
            person = customer.people[0]
            if 'first_name' in self.fields and person.first_name != first_name:
                person.first_name = first_name
            if 'last_name' in self.fields and person.last_name != last_name:
                person.last_name = last_name

        if 'phone_number' in self.fields:
            phones = filter(lambda p: p.type == 'Voice', customer.phones)
            number = data['phone_number']
            if number:
                if phones:
                    phone = phones[0]
                    if phone.number != number:
                        phone.number = number
                else:
                    customer.add_phone_number(number, type='Voice')
            else:
                for phone in phones:
                    customer.phones.remove(phone)

        if 'phone_number_2' in self.fields:
            phones = filter(lambda p: p.type == 'Voice', customer.phones)
            number = data['phone_number_2']
            if number:
                if len(phones) > 1:
                    phone = phones[1]
                    if phone.number != number:
                        phone.number = number
                else:
                    customer.add_phone_number(number, 'Voice')
            else:
                for phone in phones[1:]:
                    customer.phones.remove(phone)

        if 'email_address' in self.fields:
            address = data['email_address']
            if address:
                if customer.email:
                    if customer.email.address != address:
                        customer.email.address = address
                else:
                    customer.add_email_address(address)
            else:
                if len(customer.emails):
                    del customer.emails[:]

        if 'group_id' in self.fields:
            id_ = data['group_id']
            if id_:
                group = self.groups.get(id_)
                if not group:
                    group = model.CustomerGroup()
                    group.id = id_
                    group.name = "(auto-created)"
                    self.session.add(group)
                    self.groups[group.id] = group
                if group in customer.groups:
                    if group is not customer.groups[0]:
                        customer.groups.remove(group)
                        customer.groups.insert(0, group)
                else:
                    customer.groups.insert(0, group)
            else:
                if customer.groups:
                    del customer.groups[:]

        if 'group_id_2' in self.fields:
            id_ = data['group_id_2']
            if id_:
                group = self.groups.get(id_)
                if not group:
                    group = model.CustomerGroup()
                    group.id_ = id_
                    group.name = "(auto-created)"
                    self.session.add(group)
                    self.groups[group.id] = group
                if group in customer.groups:
                    if len(customer.groups) > 1:
                        if group is not customer.groups[1]:
                            customer.groups.remove(group)
                            customer.groups.insert(1, group)
                else:
                    if len(customer.groups) > 1:
                        customer.groups.insert(1, group)
                    else:
                        customer.groups.append(group)
            else:
                if len(customer.groups) > 1:
                    del customer.groups[1:]

        return customer


class CustomerGroupImporter(Importer):
    """
    CustomerGroup data importer.
    """
    model_class = model.CustomerGroup


class CustomerGroupAssignmentImporter(Importer):
    """
    CustomerGroupAssignment data importer.
    """
    model_class = model.CustomerGroupAssignment


class CustomerPersonImporter(Importer):
    """
    CustomerPerson data importer.
    """
    model_class = model.CustomerPerson


class CustomerEmailAddressImporter(Importer):
    """
    Customer email address data importer.
    """
    model_class = model.CustomerEmailAddress


class CustomerPhoneNumberImporter(Importer):
    """
    Customer phone number data importer.
    """
    model_class = model.CustomerPhoneNumber


class VendorImporter(Importer):
    """
    Vendor data importer.
    """
    model_class = model.Vendor

    phone_fields = [
        'phone_number',
        'phone_number_2',
        'fax_number',
        'fax_number_2',
    ]
    contact_fields = [
        'contact_name',
        'contact_name_2',
    ]
    complex_fields = [
        'email_address',
    ]

    @property
    def supported_fields(self):
        return (self.simple_fields + self.phone_fields + self.contact_fields
                + self.complex_fields)

    def cache_query_options(self):
        options = []
        for field in self.phone_fields:
            if field in self.fields:
                options.append(orm.joinedload(model.Vendor.phones))
                break
        for field in self.contact_fields:
            if field in self.fields:
                options.append(orm.joinedload(model.Vendor._contacts))
                break
        if 'email_address' in self.fields:
            options.append(orm.joinedload(model.Vendor.email))
        return options

    def normalize_instance(self, vendor):
        data = super(VendorImporter, self).normalize_instance(vendor)

        if 'phone_number' in self.fields:
            data['phone_number'] = None
            for phone in vendor.phones:
                if phone.type == 'Voice':
                    data['phone_number'] = phone.number
                    break

        if 'phone_number_2' in self.fields:
            data['phone_number_2'] = None
            first = False
            for phone in vendor.phones:
                if phone.type == 'Voice':
                    if first:
                        data['phone_number_2'] = phone.number
                        break
                    first = True

        if 'fax_number' in self.fields:
            data['fax_number'] = None
            for phone in vendor.phones:
                if phone.type == 'Fax':
                    data['fax_number'] = phone.number
                    break

        if 'fax_number_2' in self.fields:
            data['fax_number_2'] = None
            first = False
            for phone in vendor.phones:
                if phone.type == 'Fax':
                    if first:
                        data['fax_number_2'] = phone.number
                        break
                    first = True

        if 'contact_name' in self.fields:
            contact = vendor.contact
            data['contact_name'] = contact.display_name if contact else None

        if 'contact_name_2' in self.fields:
            contact = vendor.contacts[1] if len(vendor.contacts) > 1 else None
            data['contact_name_2'] = contact.display_name if contact else None

        if 'email_address' in self.fields:
            email = vendor.email
            data['email_address'] = email.address if email else None

        return data

    def update_instance(self, vendor, data, inst_data=None):
        vendor = super(VendorImporter, self).update_instance(vendor, data, inst_data)

        if 'phone_number' in self.fields:
            number = data['phone_number'] or None
            if number:
                found = False
                for phone in vendor.phones:
                    if phone.type == 'Voice':
                        if phone.number != number:
                            phone.number = number
                        found = True
                        break
                if not found:
                    vendor.add_phone_number(number, type='Voice')
            else:
                for phone in list(vendor.phones):
                    if phone.type == 'Voice':
                        vendor.phones.remove(phone)

        if 'phone_number_2' in self.fields:
            number = data['phone_number_2'] or None
            if number:
                found = False
                first = False
                for phone in vendor.phones:
                    if phone.type == 'Voice':
                        if first:
                            if phone.number != number:
                                phone.number = number
                            found = True
                            break
                        first = True
                if not found:
                    vendor.add_phone_number(number, type='Voice')
            else:
                first = False
                for phone in list(vendor.phones):
                    if phone.type == 'Voice':
                        if first:
                            vendor.phones.remove(phone)
                            break
                        first = True

        if 'fax_number' in self.fields:
            number = data['fax_number'] or None
            if number:
                found = False
                for phone in vendor.phones:
                    if phone.type == 'Fax':
                        if phone.number != number:
                            phone.number = number
                        found = True
                        break
                if not found:
                    vendor.add_phone_number(number, type='Fax')
            else:
                for phone in list(vendor.phones):
                    if phone.type == 'Fax':
                        vendor.phones.remove(phone)

        if 'fax_number_2' in self.fields:
            number = data['fax_number_2'] or None
            if number:
                found = False
                first = False
                for phone in vendor.phones:
                    if phone.type == 'Fax':
                        if first:
                            if phone.number != number:
                                phone.number = number
                            found = True
                            break
                        first = True
                if not found:
                    vendor.add_phone_number(number, type='Fax')
            else:
                first = False
                for phone in list(vendor.phones):
                    if phone.type == 'Fax':
                        if first:
                            vendor.phones.remove(phone)
                            break
                        first = True

        if 'contact_name' in self.fields:
            if data['contact_name']:
                contact = vendor.contact
                if not contact:
                    contact = model.Person()
                    self.session.add(contact)
                    vendor.contacts.append(contact)
                contact.display_name = data['contact_name']
            else:
                if len(vendor.contacts):
                    del vendor.contacts[:]

        if 'contact_name_2' in self.fields:
            if data['contact_name_2']:
                contact = vendor.contacts[1] if len(vendor.contacts) > 1 else None
                if not contact:
                    contact = model.Person()
                    self.session.add(contact)
                    vendor.contacts.append(contact)
                contact.display_name = data['contact_name_2']
            else:
                if len(vendor.contacts) > 1:
                    del vendor.contacts[1:]

        if 'email_address' in self.fields:
            address = data['email_address'] or None
            if address:
                if vendor.email:
                    if vendor.email.address != address:
                        vendor.email.address = address
                else:
                    vendor.add_email_address(address)
            else:
                if len(vendor.emails):
                    del vendor.emails[:]

        return vendor


class VendorEmailAddressImporter(Importer):
    """
    Vendor email data importer.
    """
    model_class = model.VendorEmailAddress


class VendorPhoneNumberImporter(Importer):
    """
    Vendor phone data importer.
    """
    model_class = model.VendorPhoneNumber


class VendorContactImporter(Importer):
    """
    Vendor contact data importer.
    """
    model_class = model.VendorContact


class DepartmentImporter(Importer):
    """
    Department data importer.
    """
    model_class = model.Department


class SubdepartmentImporter(Importer):
    """
    Subdepartment data importer.
    """
    model_class = model.Subdepartment

    @property
    def supported_fields(self):
        return self.simple_fields + [
            'department_number',
        ]

    def setup(self):
        self.departments = cache.cache_model(self.session, model.Department, key='number',
                                             progress=self.progress)

    def cache_query_options(self):
        if 'department_number' in self.fields:
            return [orm.joinedload(model.Subdepartment.department)]

    def normalize_instance(self, subdepartment):
        data = super(SubdepartmentImporter, self).normalize_instance(subdepartment)
        if 'department_number' in self.fields:
            dept = subdepartment.department
            data['department_number'] = dept.number if dept else None
        return data

    def update_instance(self, subdepartment, data, inst_data=None):
        subdepartment = super(SubdepartmentImporter, self).update_instance(subdepartment, data, inst_data)
        if 'department_number' in self.fields:
            dept = self.departments.get(data['department_number'])
            if not dept:
                dept = model.Department()
                dept.number = data['department_number']
                dept.name = "(auto-created)"
                self.session.add(dept)
                self.departments[dept.number] = dept
            subdepartment.department = dept
        return subdepartment


class CategoryImporter(Importer):
    """
    Category data importer.
    """
    model_class = model.Category


class FamilyImporter(Importer):
    """
    Family data importer.
    """
    model_class = model.Family


class ReportCodeImporter(Importer):
    """
    ReportCode data importer.
    """
    model_class = model.ReportCode


class DepositLinkImporter(Importer):
    """
    Deposit link data importer.
    """
    model_class = model.DepositLink


class TaxImporter(Importer):
    """
    Tax data importer.
    """
    model_class = model.Tax


class BrandImporter(Importer):
    """
    Brand data importer.
    """
    model_class = model.Brand


class ProductImporter(Importer):
    """
    Data importer for :class:`rattail.db.model.Product`.
    """
    model_class = model.Product

    regular_price_fields = [
        'regular_price_price',
        'regular_price_multiple',
        'regular_price_pack_price',
        'regular_price_pack_multiple',
        'regular_price_type',
        'regular_price_level',
        'regular_price_starts',
        'regular_price_ends',
    ]
    sale_price_fields = [
        'sale_price_price',
        'sale_price_multiple',
        'sale_price_pack_price',
        'sale_price_pack_multiple',
        'sale_price_type',
        'sale_price_level',
        'sale_price_starts',
        'sale_price_ends',
    ]

    @property
    def supported_fields(self):
        return self.simple_fields + self.regular_price_fields + self.sale_price_fields + [
            'brand_name',
            'department_number',
            'subdepartment_number',
            'category_number',
            'family_code',
            'report_code',
            'deposit_link_code',
            'tax_code',
            'vendor_id',
            'vendor_item_code',
            'vendor_case_cost',
        ]

    def setup(self):
        if 'brand_name' in self.fields:
            self.brands = cache.cache_model(self.session, model.Brand, key='name', progress=self.progress)
        if 'department_number' in self.fields:
            self.departments = cache.cache_model(self.session, model.Department, key='number', progress=self.progress)
        if 'subdepartment_number' in self.fields:
            self.subdepartments = cache.cache_model(self.session, model.Subdepartment, key='number', progress=self.progress)
        if 'category_number' in self.fields:
            self.categories = cache.cache_model(self.session, model.Category, key='number', progress=self.progress)
        if 'family_code' in self.fields:
            self.families = cache.cache_model(self.session, model.Family, key='code', progress=self.progress)
        if 'report_code' in self.fields:
            self.reportcodes = cache.cache_model(self.session, model.ReportCode, key='code', progress=self.progress)
        if 'deposit_link_code' in self.fields:
            self.depositlinks = cache.cache_model(self.session, model.DepositLink, key='code', progress=self.progress)
        if 'tax_code' in self.fields:
            self.taxes = cache.cache_model(self.session, model.Tax, key='code', progress=self.progress)
        if 'vendor_id' in self.fields:
            self.vendors = cache.cache_model(self.session, model.Vendor, key='id', progress=self.progress)

    def cache_query_options(self):
        options = []
        if 'brand_name' in self.fields:
            options.append(orm.joinedload(model.Product.brand))
        if 'department_number' in self.fields:
            options.append(orm.joinedload(model.Product.department))
        if 'subdepartment_number' in self.fields:
            options.append(orm.joinedload(model.Product.subdepartment))
        if 'category_number' in self.fields:
            options.append(orm.joinedload(model.Product.category))
        if 'family_code' in self.fields:
            options.append(orm.joinedload(model.Product.family))
        if 'report_code' in self.fields:
            options.append(orm.joinedload(model.Product.report_code))
        if 'deposit_link_code' in self.fields:
            options.append(orm.joinedload(model.Product.deposit_link))
        if 'tax_code' in self.fields:
            options.append(orm.joinedload(model.Product.tax))
        joined_prices = False
        for field in self.regular_price_fields:
            if field in self.fields:
                options.append(orm.joinedload(model.Product.prices))
                options.append(orm.joinedload(model.Product.regular_price))
                joined_prices = True
                break
        for field in self.sale_price_fields:
            if field in self.fields:
                if not joined_prices:
                    options.append(orm.joinedload(model.Product.prices))
                options.append(orm.joinedload(model.Product.current_price))
                break
        if set(self.fields) | set(['vendor_id', 'vendor_item_code', 'vendor_case_cost']):
            options.append(orm.joinedload(model.Product.cost))
            # options.append(orm.joinedload(model.Product.costs))
        return options

    def normalize_instance(self, product):
        data = super(ProductImporter, self).normalize_instance(product)

        if 'brand_name' in self.fields:
            data['brand_name'] = product.brand.name if product.brand else None
        if 'department_number' in self.fields:
            data['department_number'] = product.department.number if product.department else None
        if 'subdepartment_number' in self.fields:
            data['subdepartment_number'] = product.subdepartment.number if product.subdepartment else None
        if 'category_number' in self.fields:
            data['category_number'] = product.category.number if product.category else None
        if 'family_code' in self.fields:
            data['family_code'] = product.family.code if product.family else None
        if 'report_code' in self.fields:
            data['report_code'] = product.report_code.code if product.report_code else None
        if 'deposit_link_code' in self.fields:
            data['deposit_link_code'] = product.deposit_link.code if product.deposit_link else None
        if 'tax_code' in self.fields:
            data['tax_code'] = product.tax.code if product.tax else None

        for field in self.regular_price_fields:
            if field in self.fields:
                price = product.regular_price
                self.newval(data, 'regular_price_price', price.price if price else None)
                self.newval(data, 'regular_price_multiple', price.multiple if price else None)
                self.newval(data, 'regular_price_pack_price', price.pack_price if price else None)
                self.newval(data, 'regular_price_pack_multiple', price.pack_multiple if price else None)
                self.newval(data, 'regular_price_type', price.type if price else None)
                self.newval(data, 'regular_price_level', price.level if price else None)
                self.newval(data, 'regular_price_starts', price.starts if price else None)
                self.newval(data, 'regular_price_ends', price.ends if price else None)
                break

        for field in self.sale_price_fields:
            if field in self.fields:
                price = product.current_price
                self.newval(data, 'sale_price_price', price.price if price else None)
                self.newval(data, 'sale_price_multiple', price.multiple if price else None)
                self.newval(data, 'sale_price_pack_price', price.pack_price if price else None)
                self.newval(data, 'sale_price_pack_multiple', price.pack_multiple if price else None)
                self.newval(data, 'sale_price_type', price.type if price else None)
                self.newval(data, 'sale_price_level', price.level if price else None)
                self.newval(data, 'sale_price_starts', price.starts if price else None)
                self.newval(data, 'sale_price_ends', price.ends if price else None)
                break

        if set(self.fields) | set(['vendor_id', 'vendor_item_code', 'vendor_case_cost']):
            cost = product.cost
            self.newval(data, 'vendor_id', cost.vendor.id if cost else None)
            self.newval(data, 'vendor_item_code', cost.code if cost else None)
            self.newval(data, 'vendor_case_cost', cost.case_cost if cost else None)

        return data

    def update_instance(self, product, data, inst_data=None):
        product = super(ProductImporter, self).update_instance(product, data, inst_data)

        if 'brand_name' in self.fields:
            name = data['brand_name']
            if name:
                brand = self.brands.get(name)
                if not brand:
                    brand = model.Brand()
                    brand.name = name
                    self.session.add(brand)
                    self.brands[brand.name] = brand
                product.brand = brand
            else:
                if product.brand:
                    product.brand = None

        if 'department_number' in self.fields:
            number = data['department_number']
            if number:
                dept = self.departments.get(number)
                if not dept:
                    dept = model.Department()
                    dept.number = number
                    dept.name = "(auto-created)"
                    self.session.add(dept)
                    self.departments[dept.number] = dept
                product.department = dept
            else:
                if product.department:
                    product.department = None

        if 'subdepartment_number' in self.fields:
            number = data['subdepartment_number']
            if number:
                sub = self.subdepartments.get(number)
                if not sub:
                    sub = model.Subdepartment()
                    sub.number = number
                    sub.name = "(auto-created)"
                    self.session.add(sub)
                    self.subdepartments[number] = sub
                product.subdepartment = sub
            else:
                if product.subdepartment:
                    product.subdepartment = None

        if 'category_number' in self.fields:
            number = data['category_number']
            if number:
                cat = self.categories.get(number)
                if not cat:
                    cat = model.Category()
                    cat.number = number
                    cat.name = "(auto-created)"
                    self.session.add(cat)
                    self.categories[number] = cat
                product.category = cat
            else:
                if product.category:
                    product.category = None

        if 'family_code' in self.fields:
            code = data['family_code']
            if code:
                family = self.families.get(code)
                if not family:
                    family = model.Family()
                    family.code = code
                    family.name = "(auto-created)"
                    self.session.add(family)
                    self.families[family.code] = family
                product.family = family
            else:
                if product.family:
                    product.family = None

        if 'report_code' in self.fields:
            code = data['report_code']
            if code:
                rc = self.reportcodes.get(code)
                if not rc:
                    rc = model.ReportCode()
                    rc.code = code
                    rc.name = "(auto-created)"
                    self.session.add(rc)
                    self.reportcodes[rc.code] = rc
                product.report_code = rc
            else:
                if product.report_code:
                    product.report_code = None

        if 'deposit_link_code' in self.fields:
            code = data['deposit_link_code']
            if code:
                link = self.depositlinks.get(code)
                if not link:
                    link = model.DepositLink()
                    link.code = code
                    link.description = "(auto-created)"
                    self.session.add(link)
                    self.depositlinks[link.code] = link
                product.deposit_link = link
            else:
                if product.deposit_link:
                    product.deposit_link = None

        if 'tax_code' in self.fields:
            code = data['tax_code']
            if code:
                tax = self.taxes.get(code)
                if not tax:
                    tax = model.Tax()
                    tax.code = code
                    tax.description = "(auto-created)"
                    tax.rate = 0
                    self.session.add(tax)
                    self.taxes[tax.code] = tax
                product.tax = tax
            elif product.tax:
                product.tax = None

        create = False
        delete = False
        for field in self.regular_price_fields:
            if field in self.fields:
                delete = True
                if data[field] is not None:
                    create = True
                    break
        if create:
            price = product.regular_price
            if not price:
                price = model.ProductPrice()
                product.prices.append(price)
                product.regular_price = price
            if 'regular_price_price' in self.fields:
                price.price = data['regular_price_price']
            if 'regular_price_multiple' in self.fields:
                price.multiple = data['regular_price_multiple']
            if 'regular_price_pack_price' in self.fields:
                price.pack_price = data['regular_price_pack_price']
            if 'regular_price_pack_multiple' in self.fields:
                price.pack_multiple = data['regular_price_pack_multiple']
            if 'regular_price_type' in self.fields:
                price.type = data['regular_price_type']
            if 'regular_price_level' in self.fields:
                price.level = data['regular_price_level']
            if 'regular_price_starts' in self.fields:
                price.starts = data['regular_price_starts']
            if 'regular_price_ends' in self.fields:
                price.ends = data['regular_price_ends']
        elif delete:
            if product.regular_price:
                product.regular_price = None

        create = False
        delete = False
        for field in self.sale_price_fields:
            if field in self.fields:
                delete = True
                if data[field]:
                    create = True
                    break
        if create:
            price = product.current_price
            if not price:
                price = model.ProductPrice()
                product.prices.append(price)
                product.current_price = price
            if 'sale_price_price' in self.fields:
                price.price = data['sale_price_price']
            if 'sale_price_multiple' in self.fields:
                price.multiple = data['sale_price_multiple']
            if 'sale_price_pack_price' in self.fields:
                price.pack_price = data['sale_price_pack_price']
            if 'sale_price_pack_multiple' in self.fields:
                price.pack_multiple = data['sale_price_pack_multiple']
            if 'sale_price_type' in self.fields:
                price.type = data['sale_price_type']
            if 'sale_price_level' in self.fields:
                price.level = data['sale_price_level']
            if 'sale_price_starts' in self.fields:
                price.starts = data['sale_price_starts']
            if 'sale_price_ends' in self.fields:
                price.ends = data['sale_price_ends']
        elif delete:
            if product.current_price:
                product.current_price = None

        if 'vendor_id' in self.fields:
            id_ = data['vendor_id']
            if id_:
                vendor = self.vendors.get(id_)
                if not vendor:
                    vendor = model.Vendor()
                    vendor.id = id_
                    vendor.name = "(auto-created)"
                    self.session.add(vendor)
                    self.vendors[id_] = vendor
                if product.cost:
                    if product.cost.vendor is not vendor:
                        cost = product.cost_for_vendor(vendor)
                        if not cost:
                            cost = model.ProductCost()
                            cost.vendor = vendor
                        product.costs.insert(0, cost)
                else:
                    cost = model.ProductCost()
                    cost.vendor = vendor
                    product.costs.append(cost)
                    # TODO: This seems heavy-handed, but also seems necessary
                    # to populate the `Product.cost` relationship...
                    self.session.add(product)
                    self.session.flush()
                    self.session.refresh(product)
            else:
                if product.cost:
                    del product.costs[:]

        if 'vendor_item_code' in self.fields:
            code = data['vendor_item_code']
            if data.get('vendor_id'):
                if product.cost:
                    product.cost.code = code
                else:
                    log.warning("product has no cost, so can't set vendor_item_code: {0}".format(product))

        if 'vendor_case_cost' in self.fields:
            cost = data['vendor_case_cost']
            if data.get('vendor_id'):
                if product.cost:
                    product.cost.case_cost = cost
                else:
                    log.warning("product has no cost, so can't set vendor_case_cost: {0}".format(product))

        return product


class ProductCodeImporter(Importer):
    """
    Data importer for :class:`rattail.db.model.ProductCode`.
    """
    model_class = model.ProductCode

    @property
    def supported_fields(self):
        return self.simple_fields + [
            'product_upc',
            'primary',
        ]

    def setup(self):
        if 'product_upc' in self.fields:
            self.products = self.cache_model(model.Product, key='upc')

    def cache_query_options(self):
        if 'product_upc' in self.fields:
            return [orm.joinedload(model.ProductCode.product)]

    def normalize_instance(self, code):
        data = super(ProductCodeImporter, self).normalize_instance(code)
        if 'product_upc' in self.fields:
            data['product_upc'] = code.product.upc
        self.newval(data, 'primary', code.ordinal == 1)
        return data

    def new_instance(self, key):
        code = super(ProductCodeImporter, self).new_instance(key)
        if 'product_upc' in self.key:
            i = list(self.key).index('product_upc')
            product = self.products[key[i]]
            product._codes.append(code)
        return code

    def update_instance(self, code, data, instance_data=None):
        code = super(ProductCodeImporter, self).update_instance(code, data, instance_data)

        if 'product_upc' in self.fields and 'product_uuid' not in self.fields:
            upc = data['product_upc']
            assert upc, "Source data has no product_upc value: {0}".format(repr(data))
            product = self.products.get(upc)
            if not product:
                product = model.Product()
                product.upc = upc
                product.description = "(auto-created)"
                self.session.add(product)
                self.products[product.upc] = product
                product._codes.append(code)
            else:
                if code not in product._codes:
                    product._codes.append(code)

        if 'primary' in self.fields:
            if data['primary']:
                if code.ordinal != 1:
                    product = code.product
                    product._codes.remove(code)
                    product._codes.insert(0, code)
                    product._codes.reorder()
            elif code.ordinal == 1:
                product = code.product
                if len(product._codes) > 1:
                    product._codes.remove(code)
                    product._codes.append(code)
                    product._codes.reorder()

        return code


class ProductCostImporter(Importer):
    """
    Data importer for :class:`rattail.db.model.ProductCost`.
    """
    model_class = model.ProductCost

    @property
    def supported_fields(self):
        return self.simple_fields + [
            'product_upc',
            'vendor_id',
            'preferred',
        ]

    def setup(self):
        if 'product_upc' in self.fields:
            self.products = cache.cache_model(self.session, model.Product, key='upc',
                                              progress=self.progress)
        if 'vendor_id' in self.fields:
            self.vendors = cache.cache_model(self.session, model.Vendor, key='id',
                                             progress=self.progress)

    def cache_query_options(self):
        options = []
        if 'product_upc' in self.fields:
            options.append(orm.joinedload(model.ProductCost.product))
        if 'vendor_id' in self.fields:
            options.append(orm.joinedload(model.ProductCost.vendor))
        return options

    def normalize_instance(self, cost):
        data = super(ProductCostImporter, self).normalize_instance(cost)
        if 'product_upc' in self.fields:
            data['product_upc'] = cost.product.upc
        if 'vendor_id' in self.fields:
            data['vendor_id'] = cost.vendor.id
        self.newval(data, 'preferred', cost.preference == 1)
        return data
        
    def update_instance(self, cost, data, instance_data=None):
        cost = super(ProductCostImporter, self).update_instance(cost, data, instance_data)

        if 'product_upc' in self.fields and 'product_uuid' not in self.fields:
            upc = data['product_upc']
            assert upc, "Source data has no product_upc value: {0}".format(repr(data))
            product = self.products.get(upc)
            if not product:
                product = model.Product()
                product.upc = upc
                product.description = "(auto-created)"
                self.session.add(product)
                self.products[product.upc] = product
            if not cost.product:
                product.costs.append(cost)
            elif cost.product is not product:
                log.warning("duplicate products detected for UPC {0}".format(upc.pretty()))

        if 'vendor_id' in self.fields and 'vendor_uuid' not in self.fields:
            id_ = data['vendor_id']
            assert id_, "Source data has no vendor_id value: {0}".format(repr(data))
            vendor = self.vendors.get(id_)
            if not vendor:
                vendor = model.Vendor()
                vendor.id = id_
                vendor.name = "(auto-created)"
                self.session.add(vendor)
                self.vendors[vendor.id] = vendor
            cost.vendor = vendor

        if 'preferred' in self.fields:
            if data['preferred']:
                if cost.preference != 1:
                    product = cost.product
                    product.costs.remove(cost)
                    product.costs.insert(0, cost)
            else:
                if cost.preference == 1:
                    product = cost.product
                    if len(product.costs) > 1:
                        product.costs.remove(cost)
                        product.costs.append(cost)
                        product.costs.reorder()

        return cost


class ProductPriceImporter(Importer):
    """
    Data importer for :class:`rattail.db.model.ProductPrice`.
    """
    model_class = model.ProductPrice
