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
Rattail Data Normalization
"""

from __future__ import unicode_literals, absolute_import


class Normalizer(object):
    """
    Base class for data normalizers.
    """

    def normalize(self, instance):
        raise NotImplementedError


class UserNormalizer(Normalizer):
    """
    Normalizer for user data.
    """
    # Must set this to the administrator Role instance.
    admin = None

    def normalize(self, user):
        return {
            'uuid': user.uuid,
            'username': user.username,
            'password': user.password,
            'salt': user.salt,
            'person_uuid': user.person_uuid,
            'active': user.active,
            'admin': self.admin in user.roles,
        }


class DepartmentNormalizer(Normalizer):
    """
    Normalizer for department data.
    """

    def normalize(self, department):
        return {
            'uuid': department.uuid,
            'number': department.number,
            'name': department.name,
        }


class EmployeeNormalizer(Normalizer):
    """
    Normalizer for employee data.
    """

    def normalize(self, employee):
        person = employee.person
        customer = person.customers[0] if person.customers else None
        data = {
            'uuid': employee.uuid,
            'id': employee.id,
            'person_uuid': person.uuid,
            'customer_id': customer.id if customer else None,
            'status': employee.status,
            'first_name': person.first_name,
            'last_name': person.last_name,
            'display_name': employee.display_name,
            'person_display_name': person.display_name,
        }

        data['phone_number'] = None
        for phone in employee.phones:
            if phone.type == 'Home':
                data['phone_number'] = phone.number
                break

        data['phone_number_2'] = None
        first = False
        for phone in employee.phones:
            if phone.type == 'Home':
                if first:
                    data['phone_number_2'] = phone.number
                    break
                first = True

        email = employee.email
        data['email_address'] = email.address if email else None

        return data


class EmployeeStoreNormalizer(Normalizer):
    """
    Normalizer for employee_x_store data.
    """

    def normalize(self, emp_store):
        return {
            'uuid': emp_store.uuid,
            'employee_uuid': emp_store.employee_uuid,
            'store_uuid': emp_store.store_uuid,
        }


class EmployeeDepartmentNormalizer(Normalizer):
    """
    Normalizer for employee_x_department data.
    """

    def normalize(self, emp_dept):
        return {
            'uuid': emp_dept.uuid,
            'employee_uuid': emp_dept.employee_uuid,
            'department_uuid': emp_dept.department_uuid,
        }


class MessageNormalizer(Normalizer):
    """
    Normalizer for message data.
    """

    def normalize(self, message):
        return {
            'uuid': message.uuid,
            'sender_uuid': message.sender_uuid,
            'subject': message.subject,
            'body': message.body,
            'sent': message.sent,
        }


class MessageRecipientNormalizer(Normalizer):
    """
    Normalizer for message recipient data.
    """

    def normalize(self, recip):
        return {
            'uuid': recip.uuid,
            'message_uuid': recip.message_uuid,
            'recipient_uuid': recip.recipient_uuid,
            'status': recip.status,
        }
