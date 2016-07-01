# -*- coding: utf-8 -*-

#
# Copyright (c) 2016 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import io

from ovirtsdk4 import Error
from ovirtsdk4 import http
from ovirtsdk4 import readers
from ovirtsdk4 import writers
from ovirtsdk4 import xml

from ovirtsdk4.service import Service
from ovirtsdk4.writer import Writer


class AffinityGroupService(Service):
    """
    """

    def __init__(self, connection, path):
        super(AffinityGroupService, self).__init__(connection, path)
        self._vms_service = None

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.AffinityGroupReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        group,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.AffinityGroupWriter.write_one(group, writer, 'group')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.AffinityGroupReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def vms_service(self):
        """
        """
        return AffinityGroupVmsService(self._connection, '%s/vms' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'vms':
            return self.vms_service()
        if path.startswith('vms/'):
            return self.vms_service().service(path[4:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'AffinityGroupService:%s' % self._path


class AffinityGroupVmService(Service):
    """
    """

    def __init__(self, connection, path):
        super(AffinityGroupVmService, self).__init__(connection, path)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'AffinityGroupVmService:%s' % self._path


class AffinityGroupVmsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(AffinityGroupVmsService, self).__init__(connection, path)
        self._vm_service = None

    def add(
        self,
        vm,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.VmWriter.write_one(vm, writer, 'vm')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.VmReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of virtual machines to return. If not specified all the virtual machines are
        returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.VmReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def vm_service(self, id):
        """
        """
        return AffinityGroupVmService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.vm_service(path)
        return self.vm_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'AffinityGroupVmsService:%s' % self._path


class AffinityGroupsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(AffinityGroupsService, self).__init__(connection, path)
        self._group_service = None

    def add(
        self,
        group,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.AffinityGroupWriter.write_one(group, writer, 'group')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.AffinityGroupReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of affinity groups to return. If not specified all the affinity groups are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.AffinityGroupReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def group_service(self, id):
        """
        """
        return AffinityGroupService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.group_service(path)
        return self.group_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'AffinityGroupsService:%s' % self._path


class AffinityLabelService(Service):
    """
    Single affinity label details.
    """

    def __init__(self, connection, path):
        super(AffinityLabelService, self).__init__(connection, path)
        self._hosts_service = None
        self._vms_service = None

    def get(
        self,
    ):
        """
        Retrieves details about a label.

        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.AffinityLabelReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
    ):
        """
        Removes a label from system and clears all assignments
        of the removed label.

        """
        query = {}
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        label,
    ):
        """
        Updates a label.
        This call will update all metadata like name
        or description.

        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.AffinityLabelWriter.write_one(label, writer, 'label')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.AffinityLabelReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def hosts_service(self):
        """
        List all Hosts with this label.
        """
        return AffinityLabelHostsService(self._connection, '%s/hosts' % self._path)

    def vms_service(self):
        """
        List all VMs with this label.
        """
        return AffinityLabelVmsService(self._connection, '%s/vms' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'hosts':
            return self.hosts_service()
        if path.startswith('hosts/'):
            return self.hosts_service().service(path[6:])
        if path == 'vms':
            return self.vms_service()
        if path.startswith('vms/'):
            return self.vms_service().service(path[4:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'AffinityLabelService:%s' % self._path


class AffinityLabelHostService(Service):
    """
    This service represents a host that has a specific
    label when accessed through the affinitylabels/hosts
    subcollection.
    """

    def __init__(self, connection, path):
        super(AffinityLabelHostService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        Retrieves details about a host that has this label assigned.

        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.HostReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
    ):
        """
        Remove a label from a host.

        """
        query = {}
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'AffinityLabelHostService:%s' % self._path


class AffinityLabelHostsService(Service):
    """
    This service represents list of hosts that have a specific
    label when accessed through the affinitylabels/hosts
    subcollection.
    """

    def __init__(self, connection, path):
        super(AffinityLabelHostsService, self).__init__(connection, path)
        self._host_service = None

    def add(
        self,
        host,
    ):
        """
        Add a label to a host.

        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.HostWriter.write_one(host, writer, 'host')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.HostReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
    ):
        """
        List all hosts with the label.

        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.HostReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def host_service(self, id):
        """
        A link to the specific label-host assignment to
        allow label removal.
        """
        return AffinityLabelHostService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.host_service(path)
        return self.host_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'AffinityLabelHostsService:%s' % self._path


class AffinityLabelVmService(Service):
    """
    This service represents a vm that has a specific
    label when accessed through the affinitylabels/vms
    subcollection.
    """

    def __init__(self, connection, path):
        super(AffinityLabelVmService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        Retrieves details about a vm that has this label assigned.

        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.VmReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
    ):
        """
        Remove a label from a vm.

        """
        query = {}
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'AffinityLabelVmService:%s' % self._path


class AffinityLabelVmsService(Service):
    """
    This service represents list of vms that have a specific
    label when accessed through the affinitylabels/vms
    subcollection.
    """

    def __init__(self, connection, path):
        super(AffinityLabelVmsService, self).__init__(connection, path)
        self._vm_service = None

    def add(
        self,
        vm,
    ):
        """
        Add a label to a vm.

        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.VmWriter.write_one(vm, writer, 'vm')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.VmReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
    ):
        """
        List all vms with the label.

        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.VmReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def vm_service(self, id):
        """
        A link to the specific label-vm assignment to
        allow label removal.
        """
        return AffinityLabelVmService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.vm_service(path)
        return self.vm_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'AffinityLabelVmsService:%s' % self._path


class AffinityLabelsService(Service):
    """
    Top level affinitylabels collection used to navigate
    all affinity labels and their assignments.
    """

    def __init__(self, connection, path):
        super(AffinityLabelsService, self).__init__(connection, path)
        self._label_service = None

    def add(
        self,
        label,
    ):
        """
        Creates a new label. The label is automatically attached
        to all entities mentioned in the vms or hosts lists.

        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.AffinityLabelWriter.write_one(label, writer, 'label')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.AffinityLabelReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Lists all labels present in the system.

        Keyword arguments:
        max -- Sets the maximum number of labels to return. If not specified all the tags are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.AffinityLabelReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def label_service(self, id):
        """
        Link to a single label details.
        """
        return AffinityLabelService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.label_service(path)
        return self.label_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'AffinityLabelsService:%s' % self._path


class AssignedAffinityLabelService(Service):
    """
    This service represents one label to entity assignment
    when accessed using the entities/affinitylabels subcollection.
    """

    def __init__(self, connection, path):
        super(AssignedAffinityLabelService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        Retrieves details about the attached label.

        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.AffinityLabelReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
    ):
        """
        Removes the label from an entity. Does not touch the label itself.

        """
        query = {}
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'AssignedAffinityLabelService:%s' % self._path


class AssignedAffinityLabelsService(Service):
    """
    This service is used to list and manipulate affinity labels that are
    assigned to supported entities when accessed using entities/affinitylabels.
    """

    def __init__(self, connection, path):
        super(AssignedAffinityLabelsService, self).__init__(connection, path)
        self._label_service = None

    def add(
        self,
        label,
    ):
        """
        Attaches a label to an entity.

        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.AffinityLabelWriter.write_one(label, writer, 'label')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.AffinityLabelReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
    ):
        """
        Lists all labels that are attached to an entity.

        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.AffinityLabelReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def label_service(self, id):
        """
        Link to the specific entity-label assignment to allow
        removal.
        """
        return AssignedAffinityLabelService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.label_service(path)
        return self.label_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'AssignedAffinityLabelsService:%s' % self._path


class AssignedCpuProfileService(Service):
    """
    """

    def __init__(self, connection, path):
        super(AssignedCpuProfileService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.CpuProfileReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'AssignedCpuProfileService:%s' % self._path


class AssignedCpuProfilesService(Service):
    """
    """

    def __init__(self, connection, path):
        super(AssignedCpuProfilesService, self).__init__(connection, path)
        self._profile_service = None

    def add(
        self,
        profile,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.CpuProfileWriter.write_one(profile, writer, 'profile')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.CpuProfileReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of profiles to return. If not specified all the profiles are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.CpuProfileReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def profile_service(self, id):
        """
        """
        return AssignedCpuProfileService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.profile_service(path)
        return self.profile_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'AssignedCpuProfilesService:%s' % self._path


class AssignedDiskProfileService(Service):
    """
    """

    def __init__(self, connection, path):
        super(AssignedDiskProfileService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.DiskProfileReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'AssignedDiskProfileService:%s' % self._path


class AssignedDiskProfilesService(Service):
    """
    """

    def __init__(self, connection, path):
        super(AssignedDiskProfilesService, self).__init__(connection, path)
        self._profile_service = None

    def add(
        self,
        profile,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.DiskProfileWriter.write_one(profile, writer, 'profile')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.DiskProfileReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of profiles to return. If not specified all the profiles are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.DiskProfileReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def profile_service(self, id):
        """
        """
        return AssignedDiskProfileService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.profile_service(path)
        return self.profile_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'AssignedDiskProfilesService:%s' % self._path


class AssignedNetworkService(Service):
    """
    """

    def __init__(self, connection, path):
        super(AssignedNetworkService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NetworkReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        network,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.NetworkWriter.write_one(network, writer, 'network')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NetworkReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'AssignedNetworkService:%s' % self._path


class AssignedNetworksService(Service):
    """
    """

    def __init__(self, connection, path):
        super(AssignedNetworksService, self).__init__(connection, path)
        self._network_service = None

    def add(
        self,
        network,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.NetworkWriter.write_one(network, writer, 'network')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NetworkReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of networks to return. If not specified all the networks are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NetworkReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def network_service(self, id):
        """
        """
        return AssignedNetworkService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.network_service(path)
        return self.network_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'AssignedNetworksService:%s' % self._path


class AssignedPermissionsService(Service):
    """
    Represents a permission sub-collection, scoped by User or some entity type.
    """

    def __init__(self, connection, path):
        super(AssignedPermissionsService, self).__init__(connection, path)
        self._permission_service = None

    def add(
        self,
        permission,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.PermissionWriter.write_one(permission, writer, 'permission')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.PermissionReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.PermissionReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def permission_service(self, id):
        """
        Sub-resource locator method, returns individual permission resource on which the remainder of the URI is
        dispatched.
        """
        return PermissionService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.permission_service(path)
        return self.permission_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'AssignedPermissionsService:%s' % self._path


class AssignedRolesService(Service):
    """
    Represents a roles sub-collection, for example scoped by user.
    """

    def __init__(self, connection, path):
        super(AssignedRolesService, self).__init__(connection, path)
        self._role_service = None

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of roles to return. If not specified all the roles are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.RoleReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def role_service(self, id):
        """
        Sub-resource locator method, returns individual role resource on which the remainder of the URI is dispatched.
        """
        return RoleService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.role_service(path)
        return self.role_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'AssignedRolesService:%s' % self._path


class AssignedTagService(Service):
    """
    """

    def __init__(self, connection, path):
        super(AssignedTagService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.TagReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'AssignedTagService:%s' % self._path


class AssignedTagsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(AssignedTagsService, self).__init__(connection, path)
        self._tag_service = None

    def add(
        self,
        tag,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.TagWriter.write_one(tag, writer, 'tag')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.TagReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of tags to return. If not specified all the tags are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.TagReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def tag_service(self, id):
        """
        """
        return AssignedTagService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.tag_service(path)
        return self.tag_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'AssignedTagsService:%s' % self._path


class AssignedVnicProfileService(Service):
    """
    """

    def __init__(self, connection, path):
        super(AssignedVnicProfileService, self).__init__(connection, path)
        self._permissions_service = None

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.VnicProfileReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def permissions_service(self):
        """
        """
        return AssignedPermissionsService(self._connection, '%s/permissions' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'permissions':
            return self.permissions_service()
        if path.startswith('permissions/'):
            return self.permissions_service().service(path[12:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'AssignedVnicProfileService:%s' % self._path


class AssignedVnicProfilesService(Service):
    """
    """

    def __init__(self, connection, path):
        super(AssignedVnicProfilesService, self).__init__(connection, path)
        self._profile_service = None

    def add(
        self,
        profile,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.VnicProfileWriter.write_one(profile, writer, 'profile')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.VnicProfileReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of profiles to return. If not specified all the profiles are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.VnicProfileReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def profile_service(self, id):
        """
        """
        return AssignedVnicProfileService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.profile_service(path)
        return self.profile_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'AssignedVnicProfilesService:%s' % self._path


class AttachedStorageDomainService(Service):
    """
    """

    def __init__(self, connection, path):
        super(AttachedStorageDomainService, self).__init__(connection, path)
        self._disks_service = None

    def activate(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the activation should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'activate'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def deactivate(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the deactivation should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'deactivate'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.StorageDomainReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def disks_service(self):
        """
        """
        return DisksService(self._connection, '%s/disks' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'disks':
            return self.disks_service()
        if path.startswith('disks/'):
            return self.disks_service().service(path[6:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'AttachedStorageDomainService:%s' % self._path


class AttachedStorageDomainsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(AttachedStorageDomainsService, self).__init__(connection, path)
        self._storage_domain_service = None

    def add(
        self,
        storage_domain,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.StorageDomainWriter.write_one(storage_domain, writer, 'storage_domain')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.StorageDomainReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of storage domains to return. If not specified all the storage domains are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.StorageDomainReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def storage_domain_service(self, id):
        """
        """
        return AttachedStorageDomainService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.storage_domain_service(path)
        return self.storage_domain_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'AttachedStorageDomainsService:%s' % self._path


class BalanceService(Service):
    """
    """

    def __init__(self, connection, path):
        super(BalanceService, self).__init__(connection, path)

    def get(
        self,
        filter=None,
    ):
        """
        Keyword arguments:
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        query = {}
        if filter is not None:
            filter = Writer.render_boolean(filter)
            query['filter'] = filter
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.BalanceReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'BalanceService:%s' % self._path


class BalancesService(Service):
    """
    """

    def __init__(self, connection, path):
        super(BalancesService, self).__init__(connection, path)
        self._balance_service = None

    def add(
        self,
        balance,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.BalanceWriter.write_one(balance, writer, 'balance')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.BalanceReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        filter=None,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of balances to return. If not specified all the balances are returned.
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        query = {}
        if filter is not None:
            filter = Writer.render_boolean(filter)
            query['filter'] = filter
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.BalanceReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def balance_service(self, id):
        """
        """
        return BalanceService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.balance_service(path)
        return self.balance_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'BalancesService:%s' % self._path


class BookmarkService(Service):
    """
    """

    def __init__(self, connection, path):
        super(BookmarkService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.BookmarkReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        bookmark,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.BookmarkWriter.write_one(bookmark, writer, 'bookmark')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.BookmarkReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'BookmarkService:%s' % self._path


class BookmarksService(Service):
    """
    """

    def __init__(self, connection, path):
        super(BookmarksService, self).__init__(connection, path)
        self._bookmark_service = None

    def add(
        self,
        bookmark,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.BookmarkWriter.write_one(bookmark, writer, 'bookmark')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.BookmarkReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of bookmarks to return. If not specified all the bookmarks are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.BookmarkReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def bookmark_service(self, id):
        """
        """
        return BookmarkService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.bookmark_service(path)
        return self.bookmark_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'BookmarksService:%s' % self._path


class ClusterService(Service):
    """
    """

    def __init__(self, connection, path):
        super(ClusterService, self).__init__(connection, path)
        self._affinity_groups_service = None
        self._cpu_profiles_service = None
        self._gluster_hooks_service = None
        self._gluster_volumes_service = None
        self._network_filters_service = None
        self._networks_service = None
        self._permissions_service = None

    def get(
        self,
        filter=None,
    ):
        """
        Keyword arguments:
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        query = {}
        if filter is not None:
            filter = Writer.render_boolean(filter)
            query['filter'] = filter
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.ClusterReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def reset_emulated_machine(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the reset should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'resetemulatedmachine'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def update(
        self,
        cluster,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.ClusterWriter.write_one(cluster, writer, 'cluster')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.ClusterReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def affinity_groups_service(self):
        """
        """
        return AffinityGroupsService(self._connection, '%s/affinitygroups' % self._path)

    def cpu_profiles_service(self):
        """
        """
        return AssignedCpuProfilesService(self._connection, '%s/cpuprofiles' % self._path)

    def gluster_hooks_service(self):
        """
        """
        return GlusterHooksService(self._connection, '%s/glusterhooks' % self._path)

    def gluster_volumes_service(self):
        """
        """
        return GlusterVolumesService(self._connection, '%s/glustervolumes' % self._path)

    def network_filters_service(self):
        """
        A sub collection with all the supported network filters for this cluster.
        """
        return NetworkFiltersService(self._connection, '%s/networkfilters' % self._path)

    def networks_service(self):
        """
        """
        return AssignedNetworksService(self._connection, '%s/networks' % self._path)

    def permissions_service(self):
        """
        """
        return AssignedPermissionsService(self._connection, '%s/permissions' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'affinitygroups':
            return self.affinity_groups_service()
        if path.startswith('affinitygroups/'):
            return self.affinity_groups_service().service(path[15:])
        if path == 'cpuprofiles':
            return self.cpu_profiles_service()
        if path.startswith('cpuprofiles/'):
            return self.cpu_profiles_service().service(path[12:])
        if path == 'glusterhooks':
            return self.gluster_hooks_service()
        if path.startswith('glusterhooks/'):
            return self.gluster_hooks_service().service(path[13:])
        if path == 'glustervolumes':
            return self.gluster_volumes_service()
        if path.startswith('glustervolumes/'):
            return self.gluster_volumes_service().service(path[15:])
        if path == 'networkfilters':
            return self.network_filters_service()
        if path.startswith('networkfilters/'):
            return self.network_filters_service().service(path[15:])
        if path == 'networks':
            return self.networks_service()
        if path.startswith('networks/'):
            return self.networks_service().service(path[9:])
        if path == 'permissions':
            return self.permissions_service()
        if path.startswith('permissions/'):
            return self.permissions_service().service(path[12:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'ClusterService:%s' % self._path


class ClusterLevelService(Service):
    """
    Provides information about a specific cluster level. See the <<ClusterLevels,services/cluster-levels>> service for
    more information.
    """

    def __init__(self, connection, path):
        super(ClusterLevelService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        Provides the information about the capabilities of the specific cluster level managed by this service.

        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.ClusterLevelReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'ClusterLevelService:%s' % self._path


class ClusterLevelsService(Service):
    """
    Provides information about the capabilities of different cluster levels supported by the engine. Version 4.0 of the
    engine supports levels 4.0 and 3.6. Each of these levels different sets of CPU types, for example. This service
    provides that information. For example, to find what CPU types are supported by level 3.6 the you can send a request
    like this:
    [source]
    ----
    GET /ovirt-engine/api/clusterlevels/3.6
    ----
    That will return a `ClusterLevel` object containing the CPU types, and other information describing the cluster
    level:
    [source,xml]
    ----
    <cluster_level id="3.6" href="/ovirt-engine/api/clusterlevel/3.6">
      <cpu_types>
        <cpu_type>
          <name>Intel Conroe Family</name>
          <level>3</level>
          <architecture>x86_64</architecture>
        </cpu_type>
        ...
      </cpu_types>
      ...
    </cluster_level>
    ----
    """

    def __init__(self, connection, path):
        super(ClusterLevelsService, self).__init__(connection, path)
        self._level_service = None

    def list(
        self,
    ):
        """
        Lists the cluster levels supported by the system.

        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.ClusterLevelReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def level_service(self, id):
        """
        Reference to the service that provides information about an specific cluster level.
        """
        return ClusterLevelService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.level_service(path)
        return self.level_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'ClusterLevelsService:%s' % self._path


class ClustersService(Service):
    """
    """

    def __init__(self, connection, path):
        super(ClustersService, self).__init__(connection, path)
        self._cluster_service = None

    def add(
        self,
        cluster,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.ClusterWriter.write_one(cluster, writer, 'cluster')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.ClusterReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        case_sensitive=None,
        filter=None,
        max=None,
        search=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of clusters to return. If not specified all the clusters are returned.
        search -- A query string used to restrict the returned clusters.
        case_sensitive -- Indicates if the search performed using the `search` parameter should be performed taking case into
        account. The default value is `true`, which means that case is taken into account. If you want to search
        ignoring case set it to `false`.
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        query = {}
        if case_sensitive is not None:
            case_sensitive = Writer.render_boolean(case_sensitive)
            query['case_sensitive'] = case_sensitive
        if filter is not None:
            filter = Writer.render_boolean(filter)
            query['filter'] = filter
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        if search is not None:
            query['search'] = search
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.ClusterReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def cluster_service(self, id):
        """
        """
        return ClusterService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.cluster_service(path)
        return self.cluster_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'ClustersService:%s' % self._path


class CopyableService(Service):
    """
    """

    def __init__(self, connection, path):
        super(CopyableService, self).__init__(connection, path)

    def copy(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the copy should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'copy'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'CopyableService:%s' % self._path


class CpuProfileService(Service):
    """
    """

    def __init__(self, connection, path):
        super(CpuProfileService, self).__init__(connection, path)
        self._permissions_service = None

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.CpuProfileReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        profile,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.CpuProfileWriter.write_one(profile, writer, 'profile')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.CpuProfileReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def permissions_service(self):
        """
        """
        return AssignedPermissionsService(self._connection, '%s/permissions' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'permissions':
            return self.permissions_service()
        if path.startswith('permissions/'):
            return self.permissions_service().service(path[12:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'CpuProfileService:%s' % self._path


class CpuProfilesService(Service):
    """
    """

    def __init__(self, connection, path):
        super(CpuProfilesService, self).__init__(connection, path)
        self._profile_service = None

    def add(
        self,
        profile,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.CpuProfileWriter.write_one(profile, writer, 'profile')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.CpuProfileReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of profiles to return. If not specified all the profiles are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.CpuProfileReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def profile_service(self, id):
        """
        """
        return CpuProfileService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.profile_service(path)
        return self.profile_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'CpuProfilesService:%s' % self._path


class DataCenterService(Service):
    """
    """

    def __init__(self, connection, path):
        super(DataCenterService, self).__init__(connection, path)
        self._clusters_service = None
        self._iscsi_bonds_service = None
        self._networks_service = None
        self._permissions_service = None
        self._qoss_service = None
        self._quotas_service = None
        self._storage_domains_service = None

    def get(
        self,
        filter=None,
    ):
        """
        Keyword arguments:
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        query = {}
        if filter is not None:
            filter = Writer.render_boolean(filter)
            query['filter'] = filter
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.DataCenterReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        data_center,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.DataCenterWriter.write_one(data_center, writer, 'data_center')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.DataCenterReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def clusters_service(self):
        """
        """
        return ClustersService(self._connection, '%s/clusters' % self._path)

    def iscsi_bonds_service(self):
        """
        """
        return IscsiBondsService(self._connection, '%s/iscsibonds' % self._path)

    def networks_service(self):
        """
        """
        return NetworksService(self._connection, '%s/networks' % self._path)

    def permissions_service(self):
        """
        """
        return AssignedPermissionsService(self._connection, '%s/permissions' % self._path)

    def qoss_service(self):
        """
        """
        return QossService(self._connection, '%s/qoss' % self._path)

    def quotas_service(self):
        """
        """
        return QuotasService(self._connection, '%s/quotas' % self._path)

    def storage_domains_service(self):
        """
        """
        return AttachedStorageDomainsService(self._connection, '%s/storagedomains' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'clusters':
            return self.clusters_service()
        if path.startswith('clusters/'):
            return self.clusters_service().service(path[9:])
        if path == 'iscsibonds':
            return self.iscsi_bonds_service()
        if path.startswith('iscsibonds/'):
            return self.iscsi_bonds_service().service(path[11:])
        if path == 'networks':
            return self.networks_service()
        if path.startswith('networks/'):
            return self.networks_service().service(path[9:])
        if path == 'permissions':
            return self.permissions_service()
        if path.startswith('permissions/'):
            return self.permissions_service().service(path[12:])
        if path == 'qoss':
            return self.qoss_service()
        if path.startswith('qoss/'):
            return self.qoss_service().service(path[5:])
        if path == 'quotas':
            return self.quotas_service()
        if path.startswith('quotas/'):
            return self.quotas_service().service(path[7:])
        if path == 'storagedomains':
            return self.storage_domains_service()
        if path.startswith('storagedomains/'):
            return self.storage_domains_service().service(path[15:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'DataCenterService:%s' % self._path


class DataCentersService(Service):
    """
    """

    def __init__(self, connection, path):
        super(DataCentersService, self).__init__(connection, path)
        self._data_center_service = None

    def add(
        self,
        data_center,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.DataCenterWriter.write_one(data_center, writer, 'data_center')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.DataCenterReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        case_sensitive=None,
        filter=None,
        max=None,
        search=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of data centers to return. If not specified all the data centers are returned.
        search -- A query string used to restrict the returned data centers.
        case_sensitive -- Indicates if the search performed using the `search` parameter should be performed taking case into
        account. The default value is `true`, which means that case is taken into account. If you want to search
        ignoring case set it to `false`.
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        query = {}
        if case_sensitive is not None:
            case_sensitive = Writer.render_boolean(case_sensitive)
            query['case_sensitive'] = case_sensitive
        if filter is not None:
            filter = Writer.render_boolean(filter)
            query['filter'] = filter
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        if search is not None:
            query['search'] = search
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.DataCenterReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def data_center_service(self, id):
        """
        """
        return DataCenterService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.data_center_service(path)
        return self.data_center_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'DataCentersService:%s' % self._path


class DiskAttachmentService(Service):
    """
    This disk manages the attachment of a disk to a virtual machine.
    """

    def __init__(self, connection, path):
        super(DiskAttachmentService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        Returns the details of the attachment, including the bootable flag and link to the disk.

        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.DiskAttachmentReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        detach_only=None,
    ):
        """
        Removes the disk attachment. This will only detach the disk from the virtual machine, but won't remove it from
        the system, unless the `detach_only` parameter is `false`.

        Keyword arguments:
        detach_only -- Indicates if the disk should only be detached from the virtual machine, but not removed from the system.
        The default value is `true`, which won't remove the disk from the system.
        """
        query = {}
        if detach_only is not None:
            detach_only = Writer.render_boolean(detach_only)
            query['detach_only'] = detach_only
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        disk_attachment,
    ):
        """
        Update the disk attachment and the disk properties within it.
        [source]
        ----
        PUT /vms/{vm:id}/disksattachments/{attachment:id}
        <disk_attachment>
          <bootable>true</bootable>
          <interface>ide</interface>
          <disk>
            <name>mydisk</name>
            <provisioned_size>1024</provisioned_size>
            ...
          </disk>
        </disk_attachment>
        ----

        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.DiskAttachmentWriter.write_one(disk_attachment, writer, 'disk_attachment')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.DiskAttachmentReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'DiskAttachmentService:%s' % self._path


class DiskAttachmentsService(Service):
    """
    This service manages the set of disks attached to a virtual machine. Each attached disk is represented by a
    <<DiskAttachment,types/disk-attachment>>, containing the bootable flag, the disk interface and the reference to
    the disk.
    """

    def __init__(self, connection, path):
        super(DiskAttachmentsService, self).__init__(connection, path)
        self._attachment_service = None

    def add(
        self,
        attachment,
    ):
        """
        Adds a new disk attachment to the virtual machine. The `attachment` parameter can contain just a reference, if
        the disk already exists:
        [source,xml]
        ----
        <disk_attachment>
          <bootable>true</bootable>
          <interface>ide</interface>
          <disk id="123"/>
        </disk_attachment>
        ----
        Or it can contain the complete representation of the disk, if the disk doesn't exist yet:
        [source,xml]
        ----
        <disk_attachment>
          <bootable>true</bootable>
          <interface>ide</interface>
          <disk>
            <name>mydisk</name>
            <provisioned_size>1024</provisioned_size>
            ...
          </disk>
        </disk_attachment>
        ----
        In this case the disk will be created and then attached to the virtual machine.

        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.DiskAttachmentWriter.write_one(attachment, writer, 'attachment')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.DiskAttachmentReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
    ):
        """
        List the disk that are attached to the virtual machine.

        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.DiskAttachmentReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def attachment_service(self, id):
        """
        Reference to the service that manages a specific attachment.
        """
        return DiskAttachmentService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.attachment_service(path)
        return self.attachment_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'DiskAttachmentsService:%s' % self._path


class DiskProfileService(Service):
    """
    """

    def __init__(self, connection, path):
        super(DiskProfileService, self).__init__(connection, path)
        self._permissions_service = None

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.DiskProfileReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        profile,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.DiskProfileWriter.write_one(profile, writer, 'profile')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.DiskProfileReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def permissions_service(self):
        """
        """
        return AssignedPermissionsService(self._connection, '%s/permissions' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'permissions':
            return self.permissions_service()
        if path.startswith('permissions/'):
            return self.permissions_service().service(path[12:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'DiskProfileService:%s' % self._path


class DiskProfilesService(Service):
    """
    """

    def __init__(self, connection, path):
        super(DiskProfilesService, self).__init__(connection, path)
        self._disk_profile_service = None

    def add(
        self,
        profile,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.DiskProfileWriter.write_one(profile, writer, 'profile')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.DiskProfileReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of profiles to return. If not specified all the profiles are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.DiskProfileReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def disk_profile_service(self, id):
        """
        """
        return DiskProfileService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.disk_profile_service(path)
        return self.disk_profile_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'DiskProfilesService:%s' % self._path


class DiskSnapshotService(Service):
    """
    """

    def __init__(self, connection, path):
        super(DiskSnapshotService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.DiskSnapshotReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'DiskSnapshotService:%s' % self._path


class DiskSnapshotsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(DiskSnapshotsService, self).__init__(connection, path)
        self._snapshot_service = None

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of snapshots to return. If not specified all the snapshots are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.DiskSnapshotReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def snapshot_service(self, id):
        """
        """
        return DiskSnapshotService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.snapshot_service(path)
        return self.snapshot_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'DiskSnapshotsService:%s' % self._path


class DisksService(Service):
    """
    """

    def __init__(self, connection, path):
        super(DisksService, self).__init__(connection, path)
        self._disk_service = None

    def add(
        self,
        disk,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.DiskWriter.write_one(disk, writer, 'disk')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.DiskReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        case_sensitive=None,
        max=None,
        search=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of disks to return. If not specified all the disks are returned.
        search -- A query string used to restrict the returned disks.
        case_sensitive -- Indicates if the search performed using the `search` parameter should be performed taking case into
        account. The default value is `true`, which means that case is taken into account. If you want to search
        ignoring case set it to `false`.
        """
        query = {}
        if case_sensitive is not None:
            case_sensitive = Writer.render_boolean(case_sensitive)
            query['case_sensitive'] = case_sensitive
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        if search is not None:
            query['search'] = search
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.DiskReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def disk_service(self, id):
        """
        """
        return DiskService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.disk_service(path)
        return self.disk_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'DisksService:%s' % self._path


class DomainService(Service):
    """
    """

    def __init__(self, connection, path):
        super(DomainService, self).__init__(connection, path)
        self._groups_service = None
        self._users_service = None

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.DomainReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def groups_service(self):
        """
        """
        return DomainGroupsService(self._connection, '%s/groups' % self._path)

    def users_service(self):
        """
        """
        return DomainUsersService(self._connection, '%s/users' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'groups':
            return self.groups_service()
        if path.startswith('groups/'):
            return self.groups_service().service(path[7:])
        if path == 'users':
            return self.users_service()
        if path.startswith('users/'):
            return self.users_service().service(path[6:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'DomainService:%s' % self._path


class DomainGroupService(Service):
    """
    """

    def __init__(self, connection, path):
        super(DomainGroupService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.GroupReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'DomainGroupService:%s' % self._path


class DomainGroupsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(DomainGroupsService, self).__init__(connection, path)
        self._group_service = None

    def list(
        self,
        case_sensitive=None,
        max=None,
        search=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of groups to return. If not specified all the groups are returned.
        search -- A query string used to restrict the returned groups.
        case_sensitive -- Indicates if the search performed using the `search` parameter should be performed taking case into
        account. The default value is `true`, which means that case is taken into account. If you want to search
        ignoring case set it to `false`.
        """
        query = {}
        if case_sensitive is not None:
            case_sensitive = Writer.render_boolean(case_sensitive)
            query['case_sensitive'] = case_sensitive
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        if search is not None:
            query['search'] = search
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.GroupReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def group_service(self, id):
        """
        """
        return DomainGroupService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.group_service(path)
        return self.group_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'DomainGroupsService:%s' % self._path


class DomainUserService(Service):
    """
    """

    def __init__(self, connection, path):
        super(DomainUserService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.UserReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'DomainUserService:%s' % self._path


class DomainUsersService(Service):
    """
    """

    def __init__(self, connection, path):
        super(DomainUsersService, self).__init__(connection, path)
        self._user_service = None

    def list(
        self,
        case_sensitive=None,
        max=None,
        search=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of users to return. If not specified all the users are returned.
        search -- A query string used to restrict the returned users.
        case_sensitive -- Indicates if the search performed using the `search` parameter should be performed taking case into
        account. The default value is `true`, which means that case is taken into account. If you want to search
        ignoring case set it to `false`.
        """
        query = {}
        if case_sensitive is not None:
            case_sensitive = Writer.render_boolean(case_sensitive)
            query['case_sensitive'] = case_sensitive
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        if search is not None:
            query['search'] = search
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.UserReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def user_service(self, id):
        """
        """
        return DomainUserService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.user_service(path)
        return self.user_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'DomainUsersService:%s' % self._path


class DomainsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(DomainsService, self).__init__(connection, path)
        self._domain_service = None

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of domains to return. If not specified all the domains are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.DomainReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def domain_service(self, id):
        """
        """
        return DomainService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.domain_service(path)
        return self.domain_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'DomainsService:%s' % self._path


class EventService(Service):
    """
    """

    def __init__(self, connection, path):
        super(EventService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.EventReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'EventService:%s' % self._path


class EventsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(EventsService, self).__init__(connection, path)
        self._event_service = None

    def add(
        self,
        event,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.EventWriter.write_one(event, writer, 'event')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.EventReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        case_sensitive=None,
        max=None,
        search=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of events to return. If not specified all the events are returned.
        search -- A query string used to restrict the returned events.
        case_sensitive -- Indicates if the search performed using the `search` parameter should be performed taking case into
        account. The default value is `true`, which means that case is taken into account. If you want to search
        ignoring case set it to `false`.
        """
        query = {}
        if case_sensitive is not None:
            case_sensitive = Writer.render_boolean(case_sensitive)
            query['case_sensitive'] = case_sensitive
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        if search is not None:
            query['search'] = search
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.EventReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def undelete(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the un-delete should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'undelete'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def event_service(self, id):
        """
        """
        return EventService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.event_service(path)
        return self.event_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'EventsService:%s' % self._path


class ExternalComputeResourceService(Service):
    """
    """

    def __init__(self, connection, path):
        super(ExternalComputeResourceService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.ExternalComputeResourceReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'ExternalComputeResourceService:%s' % self._path


class ExternalComputeResourcesService(Service):
    """
    """

    def __init__(self, connection, path):
        super(ExternalComputeResourcesService, self).__init__(connection, path)
        self._resource_service = None

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of resources to return. If not specified all the resources are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.ExternalComputeResourceReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def resource_service(self, id):
        """
        """
        return ExternalComputeResourceService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.resource_service(path)
        return self.resource_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'ExternalComputeResourcesService:%s' % self._path


class ExternalDiscoveredHostService(Service):
    """
    """

    def __init__(self, connection, path):
        super(ExternalDiscoveredHostService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.ExternalDiscoveredHostReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'ExternalDiscoveredHostService:%s' % self._path


class ExternalDiscoveredHostsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(ExternalDiscoveredHostsService, self).__init__(connection, path)
        self._host_service = None

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of hosts to return. If not specified all the hosts are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.ExternalDiscoveredHostReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def host_service(self, id):
        """
        """
        return ExternalDiscoveredHostService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.host_service(path)
        return self.host_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'ExternalDiscoveredHostsService:%s' % self._path


class ExternalHostService(Service):
    """
    """

    def __init__(self, connection, path):
        super(ExternalHostService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.ExternalHostReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'ExternalHostService:%s' % self._path


class ExternalHostGroupService(Service):
    """
    """

    def __init__(self, connection, path):
        super(ExternalHostGroupService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.ExternalHostGroupReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'ExternalHostGroupService:%s' % self._path


class ExternalHostGroupsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(ExternalHostGroupsService, self).__init__(connection, path)
        self._group_service = None

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of groups to return. If not specified all the groups are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.ExternalHostGroupReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def group_service(self, id):
        """
        """
        return ExternalHostGroupService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.group_service(path)
        return self.group_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'ExternalHostGroupsService:%s' % self._path


class ExternalHostProvidersService(Service):
    """
    """

    def __init__(self, connection, path):
        super(ExternalHostProvidersService, self).__init__(connection, path)
        self._provider_service = None

    def add(
        self,
        provider,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.ExternalHostProviderWriter.write_one(provider, writer, 'provider')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.ExternalHostProviderReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of providers to return. If not specified all the providers are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.ExternalHostProviderReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def provider_service(self, id):
        """
        """
        return ExternalHostProviderService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.provider_service(path)
        return self.provider_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'ExternalHostProvidersService:%s' % self._path


class ExternalHostsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(ExternalHostsService, self).__init__(connection, path)
        self._host_service = None

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of hosts to return. If not specified all the hosts are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.ExternalHostReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def host_service(self, id):
        """
        """
        return ExternalHostService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.host_service(path)
        return self.host_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'ExternalHostsService:%s' % self._path


class ExternalProviderService(Service):
    """
    """

    def __init__(self, connection, path):
        super(ExternalProviderService, self).__init__(connection, path)
        self._certificates_service = None

    def import_certificates(
        self,
        certificates=None,
    ):
        """
        Keyword arguments:
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if certificates is not None:
            writers.CertificateWriter.write_many(certificates, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'importcertificates'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def test_connectivity(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the test should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'testconnectivity'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def certificates_service(self):
        """
        """
        return ExternalProviderCertificatesService(self._connection, '%s/certificates' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'certificates':
            return self.certificates_service()
        if path.startswith('certificates/'):
            return self.certificates_service().service(path[13:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'ExternalProviderService:%s' % self._path


class ExternalProviderCertificateService(Service):
    """
    """

    def __init__(self, connection, path):
        super(ExternalProviderCertificateService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.CertificateReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'ExternalProviderCertificateService:%s' % self._path


class ExternalProviderCertificatesService(Service):
    """
    """

    def __init__(self, connection, path):
        super(ExternalProviderCertificatesService, self).__init__(connection, path)
        self._certificate_service = None

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of certificates to return. If not specified all the certificates are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.CertificateReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def certificate_service(self, id):
        """
        """
        return ExternalProviderCertificateService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.certificate_service(path)
        return self.certificate_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'ExternalProviderCertificatesService:%s' % self._path


class FenceAgentService(Service):
    """
    """

    def __init__(self, connection, path):
        super(FenceAgentService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.AgentReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        agent,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.AgentWriter.write_one(agent, writer, 'agent')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.AgentReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'FenceAgentService:%s' % self._path


class FenceAgentsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(FenceAgentsService, self).__init__(connection, path)
        self._agent_service = None

    def add(
        self,
        agent,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.AgentWriter.write_one(agent, writer, 'agent')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.AgentReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of agents to return. If not specified all the agents are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.AgentReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def agent_service(self, id):
        """
        """
        return FenceAgentService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.agent_service(path)
        return self.agent_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'FenceAgentsService:%s' % self._path


class FileService(Service):
    """
    """

    def __init__(self, connection, path):
        super(FileService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.FileReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'FileService:%s' % self._path


class FilesService(Service):
    """
    """

    def __init__(self, connection, path):
        super(FilesService, self).__init__(connection, path)
        self._file_service = None

    def list(
        self,
        case_sensitive=None,
        max=None,
        search=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of files to return. If not specified all the files are returned.
        search -- A query string used to restrict the returned files.
        case_sensitive -- Indicates if the search performed using the `search` parameter should be performed taking case into
        account. The default value is `true`, which means that case is taken into account. If you want to search
        ignoring case set it to `false`.
        """
        query = {}
        if case_sensitive is not None:
            case_sensitive = Writer.render_boolean(case_sensitive)
            query['case_sensitive'] = case_sensitive
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        if search is not None:
            query['search'] = search
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.FileReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def file_service(self, id):
        """
        """
        return FileService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.file_service(path)
        return self.file_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'FilesService:%s' % self._path


class FilterService(Service):
    """
    """

    def __init__(self, connection, path):
        super(FilterService, self).__init__(connection, path)

    def get(
        self,
        filter=None,
    ):
        """
        Keyword arguments:
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        query = {}
        if filter is not None:
            filter = Writer.render_boolean(filter)
            query['filter'] = filter
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.FilterReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'FilterService:%s' % self._path


class FiltersService(Service):
    """
    """

    def __init__(self, connection, path):
        super(FiltersService, self).__init__(connection, path)
        self._filter_service = None

    def add(
        self,
        filter,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.FilterWriter.write_one(filter, writer, 'filter')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.FilterReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        filter=None,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of filters to return. If not specified all the filters are returned.
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        query = {}
        if filter is not None:
            filter = Writer.render_boolean(filter)
            query['filter'] = filter
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.FilterReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def filter_service(self, id):
        """
        """
        return FilterService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.filter_service(path)
        return self.filter_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'FiltersService:%s' % self._path


class GlusterBricksService(Service):
    """
    """

    def __init__(self, connection, path):
        super(GlusterBricksService, self).__init__(connection, path)
        self._brick_service = None

    def activate(
        self,
        async=None,
        bricks=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the activation should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if bricks is not None:
            writers.GlusterBrickWriter.write_many(bricks, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'activate'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def add(
        self,
        bricks,
    ):
        """
        Adds given list of bricks to the volume, and updates the database accordingly. The properties `serverId` and
        `brickDir`are required.

        Keyword arguments:
        bricks -- The list of bricks to be added to the volume
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.GlusterBrickWriter.write_many(bricks, writer, 'bricks')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.GlusterBrickReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of bricks to return. If not specified all the bricks are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.GlusterBrickReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def migrate(
        self,
        async=None,
        bricks=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the migration should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if bricks is not None:
            writers.GlusterBrickWriter.write_many(bricks, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'migrate'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
        bricks=None,
    ):
        """
        Removes the given list of bricks brick from the volume and deletes them from the database.

        Keyword arguments:
        bricks -- The list of bricks to be removed
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        if bricks is not None:
            query['bricks'] = bricks
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def stop_migrate(
        self,
        async=None,
        bricks=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the action should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if bricks is not None:
            writers.GlusterBrickWriter.write_many(bricks, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'stopmigrate'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def brick_service(self, id):
        """
        """
        return GlusterBrickService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.brick_service(path)
        return self.brick_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'GlusterBricksService:%s' % self._path


class GlusterHookService(Service):
    """
    """

    def __init__(self, connection, path):
        super(GlusterHookService, self).__init__(connection, path)

    def disable(
        self,
        async=None,
    ):
        """
        Resolves status conflict of hook among servers in cluster by disabling Gluster hook in all servers of the
        cluster. This updates the hook status to `DISABLED` in database.

        Keyword arguments:
        async -- Indicates if the action should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'disable'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def enable(
        self,
        async=None,
    ):
        """
        Resolves status conflict of hook among servers in cluster by disabling Gluster hook in all servers of the
        cluster. This updates the hook status to `DISABLED` in database.

        Keyword arguments:
        async -- Indicates if the action should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'enable'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.GlusterHookReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Removes the this Gluster hook from all servers in cluster and deletes it from the database.

        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def resolve(
        self,
        async=None,
        host=None,
        resolution_type=None,
    ):
        """
        Resolves missing hook conflict depending on the resolution type.
        For `ADD` resolves by copying hook stored in engine database to all servers where the hook is missing. The
        engine maintains a list of all servers where hook is missing.
        For `COPY` resolves conflict in hook content by copying hook stored in engine database to all servers where
        the hook is missing. The engine maintains a list of all servers where the content is conflicting. If a host
        id is passed as parameter, the hook content from the server is used as the master to copy to other servers
        in cluster.

        Keyword arguments:
        async -- Indicates if the action should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if host is not None:
            writers.HostWriter.write_one(host, writer)
        if resolution_type is not None:
            writer.write_string('resolution_type', resolution_type)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'resolve'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'GlusterHookService:%s' % self._path


class GlusterHooksService(Service):
    """
    """

    def __init__(self, connection, path):
        super(GlusterHooksService, self).__init__(connection, path)
        self._hook_service = None

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of hooks to return. If not specified all the hooks are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.GlusterHookReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def hook_service(self, id):
        """
        """
        return GlusterHookService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.hook_service(path)
        return self.hook_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'GlusterHooksService:%s' % self._path


class GlusterVolumesService(Service):
    """
    """

    def __init__(self, connection, path):
        super(GlusterVolumesService, self).__init__(connection, path)
        self._volume_service = None

    def add(
        self,
        volume,
    ):
        """
        Creates a new Gluster volume and adds it to the database. The volume is created based on properties of the
        `volume` parameter. The properties `name`, `volumeType` and `bricks` are required.

        Keyword arguments:
        volume -- The Gluster volume definition from which to create the volume is passed as input and the newly created
        volume is returned.
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.GlusterVolumeWriter.write_one(volume, writer, 'volume')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.GlusterVolumeReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        case_sensitive=None,
        max=None,
        search=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of volumes to return. If not specified all the volumes are returned.
        search -- A query string used to restrict the returned volumes.
        case_sensitive -- Indicates if the search performed using the `search` parameter should be performed taking case into
        account. The default value is `true`, which means that case is taken into account. If you want to search
        ignoring case set it to `false`.
        """
        query = {}
        if case_sensitive is not None:
            case_sensitive = Writer.render_boolean(case_sensitive)
            query['case_sensitive'] = case_sensitive
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        if search is not None:
            query['search'] = search
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.GlusterVolumeReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def volume_service(self, id):
        """
        """
        return GlusterVolumeService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.volume_service(path)
        return self.volume_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'GlusterVolumesService:%s' % self._path


class GraphicsConsoleService(Service):
    """
    """

    def __init__(self, connection, path):
        super(GraphicsConsoleService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.GraphicsConsoleReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'GraphicsConsoleService:%s' % self._path


class GraphicsConsolesService(Service):
    """
    """

    def __init__(self, connection, path):
        super(GraphicsConsolesService, self).__init__(connection, path)
        self._console_service = None

    def add(
        self,
        console,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.GraphicsConsoleWriter.write_one(console, writer, 'console')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.GraphicsConsoleReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of consoles to return. If not specified all the consoles are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.GraphicsConsoleReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def console_service(self, id):
        """
        """
        return GraphicsConsoleService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.console_service(path)
        return self.console_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'GraphicsConsolesService:%s' % self._path


class GroupService(Service):
    """
    """

    def __init__(self, connection, path):
        super(GroupService, self).__init__(connection, path)
        self._permissions_service = None
        self._roles_service = None
        self._tags_service = None

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.GroupReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def permissions_service(self):
        """
        """
        return AssignedPermissionsService(self._connection, '%s/permissions' % self._path)

    def roles_service(self):
        """
        """
        return AssignedRolesService(self._connection, '%s/roles' % self._path)

    def tags_service(self):
        """
        """
        return AssignedTagsService(self._connection, '%s/tags' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'permissions':
            return self.permissions_service()
        if path.startswith('permissions/'):
            return self.permissions_service().service(path[12:])
        if path == 'roles':
            return self.roles_service()
        if path.startswith('roles/'):
            return self.roles_service().service(path[6:])
        if path == 'tags':
            return self.tags_service()
        if path.startswith('tags/'):
            return self.tags_service().service(path[5:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'GroupService:%s' % self._path


class GroupsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(GroupsService, self).__init__(connection, path)
        self._group_service = None

    def add(
        self,
        group,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.GroupWriter.write_one(group, writer, 'group')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.GroupReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        case_sensitive=None,
        max=None,
        search=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of groups to return. If not specified all the groups are returned.
        search -- A query string used to restrict the returned groups.
        case_sensitive -- Indicates if the search performed using the `search` parameter should be performed taking case into
        account. The default value is `true`, which means that case is taken into account. If you want to search
        ignoring case set it to `false`.
        """
        query = {}
        if case_sensitive is not None:
            case_sensitive = Writer.render_boolean(case_sensitive)
            query['case_sensitive'] = case_sensitive
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        if search is not None:
            query['search'] = search
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.GroupReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def group_service(self, id):
        """
        """
        return GroupService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.group_service(path)
        return self.group_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'GroupsService:%s' % self._path


class HostDeviceService(Service):
    """
    """

    def __init__(self, connection, path):
        super(HostDeviceService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.HostDeviceReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'HostDeviceService:%s' % self._path


class HostDevicesService(Service):
    """
    """

    def __init__(self, connection, path):
        super(HostDevicesService, self).__init__(connection, path)
        self._device_service = None

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of devices to return. If not specified all the devices are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.HostDeviceReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def device_service(self, id):
        """
        """
        return HostDeviceService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.device_service(path)
        return self.device_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'HostDevicesService:%s' % self._path


class HostHookService(Service):
    """
    """

    def __init__(self, connection, path):
        super(HostHookService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.HookReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'HostHookService:%s' % self._path


class HostHooksService(Service):
    """
    """

    def __init__(self, connection, path):
        super(HostHooksService, self).__init__(connection, path)
        self._hook_service = None

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of hooks to return. If not specified all the hooks are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.HookReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def hook_service(self, id):
        """
        """
        return HostHookService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.hook_service(path)
        return self.hook_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'HostHooksService:%s' % self._path


class HostNicsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(HostNicsService, self).__init__(connection, path)
        self._nic_service = None

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of NICs to return. If not specified all the NICs are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.HostNicReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def nic_service(self, id):
        """
        """
        return HostNicService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.nic_service(path)
        return self.nic_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'HostNicsService:%s' % self._path


class HostNumaNodesService(Service):
    """
    """

    def __init__(self, connection, path):
        super(HostNumaNodesService, self).__init__(connection, path)
        self._node_service = None

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of nodes to return. If not specified all the nodes are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NumaNodeReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def node_service(self, id):
        """
        """
        return HostNumaNodeService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.node_service(path)
        return self.node_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'HostNumaNodesService:%s' % self._path


class HostStorageService(Service):
    """
    """

    def __init__(self, connection, path):
        super(HostStorageService, self).__init__(connection, path)
        self._storage_service = None

    def list(
        self,
        report_status=None,
    ):
        """
        Keyword arguments:
        report_status -- Indicates if the status of the LUNs in the storage should be checked.
        Checking the status of the LUN is an heavy weight operation and
        this data is not always needed by the user.
        This parameter will give the option to not perform the status check of the LUNs.
        The default is `true` for backward compatibility.
        Here an example with the LUN status :
        [source,xml]
        ----
        <host_storage id="360014051136c20574f743bdbd28177fd">
          <logical_units>
            <logical_unit id="360014051136c20574f743bdbd28177fd">
              <lun_mapping>0</lun_mapping>
              <paths>1</paths>
              <product_id>lun0</product_id>
              <serial>SLIO-ORG_lun0_1136c205-74f7-43bd-bd28-177fd5ce6993</serial>
              <size>10737418240</size>
              <status>used</status>
              <vendor_id>LIO-ORG</vendor_id>
              <volume_group_id>O9Du7I-RahN-ECe1-dZ1w-nh0b-64io-MNzIBZ</volume_group_id>
            </logical_unit>
          </logical_units>
          <type>iscsi</type>
          <host id="8bb5ade5-e988-4000-8b93-dbfc6717fe50"/>
        </host_storage>
        ----
        Here an example without the LUN status :
        [source,xml]
        ----
        <host_storage id="360014051136c20574f743bdbd28177fd">
          <logical_units>
            <logical_unit id="360014051136c20574f743bdbd28177fd">
              <lun_mapping>0</lun_mapping>
              <paths>1</paths>
              <product_id>lun0</product_id>
              <serial>SLIO-ORG_lun0_1136c205-74f7-43bd-bd28-177fd5ce6993</serial>
              <size>10737418240</size>
              <vendor_id>LIO-ORG</vendor_id>
              <volume_group_id>O9Du7I-RahN-ECe1-dZ1w-nh0b-64io-MNzIBZ</volume_group_id>
            </logical_unit>
          </logical_units>
          <type>iscsi</type>
          <host id="8bb5ade5-e988-4000-8b93-dbfc6717fe50"/>
        </host_storage>
        ----
        """
        query = {}
        if report_status is not None:
            report_status = Writer.render_boolean(report_status)
            query['report_status'] = report_status
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.HostStorageReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def storage_service(self, id):
        """
        """
        return StorageService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.storage_service(path)
        return self.storage_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'HostStorageService:%s' % self._path


class HostsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(HostsService, self).__init__(connection, path)
        self._host_service = None

    def add(
        self,
        host,
    ):
        """
        Creates a new host and adds it to the database. The host is created based on the properties of the `host`
        parameter. The `name`, `address` `rootPassword` properties are required.

        Keyword arguments:
        host -- The host definition from which to create the new host is passed as parameter, and the newly created host
        is returned.
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.HostWriter.write_one(host, writer, 'host')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.HostReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        case_sensitive=None,
        filter=None,
        max=None,
        search=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of hosts to return. If not specified all the hosts are returned.
        search -- A query string used to restrict the returned hosts.
        case_sensitive -- Indicates if the search performed using the `search` parameter should be performed taking case into
        account. The default value is `true`, which means that case is taken into account. If you want to search
        ignoring case set it to `false`.
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        query = {}
        if case_sensitive is not None:
            case_sensitive = Writer.render_boolean(case_sensitive)
            query['case_sensitive'] = case_sensitive
        if filter is not None:
            filter = Writer.render_boolean(filter)
            query['filter'] = filter
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        if search is not None:
            query['search'] = search
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.HostReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def host_service(self, id):
        """
        """
        return HostService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.host_service(path)
        return self.host_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'HostsService:%s' % self._path


class IconService(Service):
    """
    """

    def __init__(self, connection, path):
        super(IconService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.IconReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'IconService:%s' % self._path


class IconsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(IconsService, self).__init__(connection, path)
        self._icon_service = None

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of icons to return. If not specified all the icons are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.IconReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def icon_service(self, id):
        """
        """
        return IconService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.icon_service(path)
        return self.icon_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'IconsService:%s' % self._path


class ImageService(Service):
    """
    """

    def __init__(self, connection, path):
        super(ImageService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.ImageReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def import_(
        self,
        async=None,
        cluster=None,
        disk=None,
        import_as_template=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the import should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if cluster is not None:
            writers.ClusterWriter.write_one(cluster, writer)
        if disk is not None:
            writers.DiskWriter.write_one(disk, writer)
        if import_as_template is not None:
            writer.write_boolean('import_as_template', import_as_template)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'import'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'ImageService:%s' % self._path


class ImagesService(Service):
    """
    """

    def __init__(self, connection, path):
        super(ImagesService, self).__init__(connection, path)
        self._image_service = None

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of images to return. If not specified all the images are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.ImageReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def image_service(self, id):
        """
        """
        return ImageService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.image_service(path)
        return self.image_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'ImagesService:%s' % self._path


class InstanceTypeService(Service):
    """
    """

    def __init__(self, connection, path):
        super(InstanceTypeService, self).__init__(connection, path)
        self._graphics_consoles_service = None
        self._nics_service = None
        self._watchdogs_service = None

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.InstanceTypeReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        instance_type,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.InstanceTypeWriter.write_one(instance_type, writer, 'instance_type')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.InstanceTypeReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def graphics_consoles_service(self):
        """
        """
        return GraphicsConsolesService(self._connection, '%s/graphicsconsoles' % self._path)

    def nics_service(self):
        """
        """
        return InstanceTypeNicsService(self._connection, '%s/nics' % self._path)

    def watchdogs_service(self):
        """
        """
        return InstanceTypeWatchdogsService(self._connection, '%s/watchdogs' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'graphicsconsoles':
            return self.graphics_consoles_service()
        if path.startswith('graphicsconsoles/'):
            return self.graphics_consoles_service().service(path[17:])
        if path == 'nics':
            return self.nics_service()
        if path.startswith('nics/'):
            return self.nics_service().service(path[5:])
        if path == 'watchdogs':
            return self.watchdogs_service()
        if path.startswith('watchdogs/'):
            return self.watchdogs_service().service(path[10:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'InstanceTypeService:%s' % self._path


class InstanceTypeNicService(Service):
    """
    """

    def __init__(self, connection, path):
        super(InstanceTypeNicService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NicReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        nic,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.NicWriter.write_one(nic, writer, 'nic')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NicReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'InstanceTypeNicService:%s' % self._path


class InstanceTypeNicsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(InstanceTypeNicsService, self).__init__(connection, path)
        self._nic_service = None

    def add(
        self,
        nic,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.NicWriter.write_one(nic, writer, 'nic')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NicReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of NICs to return. If not specified all the NICs are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NicReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def nic_service(self, id):
        """
        """
        return InstanceTypeNicService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.nic_service(path)
        return self.nic_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'InstanceTypeNicsService:%s' % self._path


class InstanceTypeWatchdogService(Service):
    """
    """

    def __init__(self, connection, path):
        super(InstanceTypeWatchdogService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.WatchdogReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        watchdog,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.WatchdogWriter.write_one(watchdog, writer, 'watchdog')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.WatchdogReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'InstanceTypeWatchdogService:%s' % self._path


class InstanceTypeWatchdogsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(InstanceTypeWatchdogsService, self).__init__(connection, path)
        self._watchdog_service = None

    def add(
        self,
        watchdog,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.WatchdogWriter.write_one(watchdog, writer, 'watchdog')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.WatchdogReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of watchdogs to return. If not specified all the watchdogs are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.WatchdogReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def watchdog_service(self, id):
        """
        """
        return InstanceTypeWatchdogService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.watchdog_service(path)
        return self.watchdog_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'InstanceTypeWatchdogsService:%s' % self._path


class InstanceTypesService(Service):
    """
    """

    def __init__(self, connection, path):
        super(InstanceTypesService, self).__init__(connection, path)
        self._instance_type_service = None

    def add(
        self,
        instance_type,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.InstanceTypeWriter.write_one(instance_type, writer, 'instance_type')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.InstanceTypeReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of instance types to return. If not specified all the instance types are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.InstanceTypeReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def instance_type_service(self, id):
        """
        """
        return InstanceTypeService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.instance_type_service(path)
        return self.instance_type_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'InstanceTypesService:%s' % self._path


class IscsiBondService(Service):
    """
    """

    def __init__(self, connection, path):
        super(IscsiBondService, self).__init__(connection, path)
        self._networks_service = None
        self._storage_server_connections_service = None

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.IscsiBondReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        bond,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.IscsiBondWriter.write_one(bond, writer, 'bond')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.IscsiBondReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def networks_service(self):
        """
        """
        return NetworksService(self._connection, '%s/networks' % self._path)

    def storage_server_connections_service(self):
        """
        """
        return StorageServerConnectionsService(self._connection, '%s/storageserverconnections' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'networks':
            return self.networks_service()
        if path.startswith('networks/'):
            return self.networks_service().service(path[9:])
        if path == 'storageserverconnections':
            return self.storage_server_connections_service()
        if path.startswith('storageserverconnections/'):
            return self.storage_server_connections_service().service(path[25:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'IscsiBondService:%s' % self._path


class IscsiBondsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(IscsiBondsService, self).__init__(connection, path)
        self._iscsi_bond_service = None

    def add(
        self,
        bond,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.IscsiBondWriter.write_one(bond, writer, 'bond')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.IscsiBondReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of bonds to return. If not specified all the bonds are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.IscsiBondReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def iscsi_bond_service(self, id):
        """
        """
        return IscsiBondService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.iscsi_bond_service(path)
        return self.iscsi_bond_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'IscsiBondsService:%s' % self._path


class JobService(Service):
    """
    """

    def __init__(self, connection, path):
        super(JobService, self).__init__(connection, path)
        self._steps_service = None

    def clear(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the action should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'clear'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def end(
        self,
        async=None,
        force=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the action should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if force is not None:
            writer.write_boolean('force', force)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'end'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.JobReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def steps_service(self):
        """
        """
        return StepsService(self._connection, '%s/steps' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'steps':
            return self.steps_service()
        if path.startswith('steps/'):
            return self.steps_service().service(path[6:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'JobService:%s' % self._path


class JobsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(JobsService, self).__init__(connection, path)
        self._job_service = None

    def add(
        self,
        job,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.JobWriter.write_one(job, writer, 'job')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.JobReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of jobs to return. If not specified all the jobs are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.JobReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def job_service(self, id):
        """
        """
        return JobService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.job_service(path)
        return self.job_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'JobsService:%s' % self._path


class KatelloErrataService(Service):
    """
    """

    def __init__(self, connection, path):
        super(KatelloErrataService, self).__init__(connection, path)
        self._katello_erratum_service = None

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of errata to return. If not specified all the errata are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.KatelloErratumReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def katello_erratum_service(self, id):
        """
        """
        return KatelloErratumService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.katello_erratum_service(path)
        return self.katello_erratum_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'KatelloErrataService:%s' % self._path


class KatelloErratumService(Service):
    """
    """

    def __init__(self, connection, path):
        super(KatelloErratumService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.KatelloErratumReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'KatelloErratumService:%s' % self._path


class MacPoolService(Service):
    """
    """

    def __init__(self, connection, path):
        super(MacPoolService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.MacPoolReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        pool,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.MacPoolWriter.write_one(pool, writer, 'pool')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.MacPoolReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'MacPoolService:%s' % self._path


class MacPoolsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(MacPoolsService, self).__init__(connection, path)
        self._mac_pool_service = None

    def add(
        self,
        pool,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.MacPoolWriter.write_one(pool, writer, 'pool')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.MacPoolReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of pools to return. If not specified all the pools are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.MacPoolReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def mac_pool_service(self, id):
        """
        """
        return MacPoolService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.mac_pool_service(path)
        return self.mac_pool_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'MacPoolsService:%s' % self._path


class MeasurableService(Service):
    """
    """

    def __init__(self, connection, path):
        super(MeasurableService, self).__init__(connection, path)
        self._statistics_service = None

    def statistics_service(self):
        """
        """
        return StatisticsService(self._connection, '%s/statistics' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'statistics':
            return self.statistics_service()
        if path.startswith('statistics/'):
            return self.statistics_service().service(path[11:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'MeasurableService:%s' % self._path


class MoveableService(Service):
    """
    """

    def __init__(self, connection, path):
        super(MoveableService, self).__init__(connection, path)

    def move(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the move should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'move'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'MoveableService:%s' % self._path


class NetworkService(Service):
    """
    """

    def __init__(self, connection, path):
        super(NetworkService, self).__init__(connection, path)
        self._network_labels_service = None
        self._permissions_service = None
        self._vnic_profiles_service = None

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NetworkReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        network,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.NetworkWriter.write_one(network, writer, 'network')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NetworkReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def network_labels_service(self):
        """
        """
        return NetworkLabelsService(self._connection, '%s/networklabels' % self._path)

    def permissions_service(self):
        """
        """
        return AssignedPermissionsService(self._connection, '%s/permissions' % self._path)

    def vnic_profiles_service(self):
        """
        """
        return AssignedVnicProfilesService(self._connection, '%s/vnicprofiles' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'networklabels':
            return self.network_labels_service()
        if path.startswith('networklabels/'):
            return self.network_labels_service().service(path[14:])
        if path == 'permissions':
            return self.permissions_service()
        if path.startswith('permissions/'):
            return self.permissions_service().service(path[12:])
        if path == 'vnicprofiles':
            return self.vnic_profiles_service()
        if path.startswith('vnicprofiles/'):
            return self.vnic_profiles_service().service(path[13:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'NetworkService:%s' % self._path


class NetworkAttachmentService(Service):
    """
    """

    def __init__(self, connection, path):
        super(NetworkAttachmentService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NetworkAttachmentReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        attachment,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.NetworkAttachmentWriter.write_one(attachment, writer, 'attachment')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NetworkAttachmentReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'NetworkAttachmentService:%s' % self._path


class NetworkAttachmentsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(NetworkAttachmentsService, self).__init__(connection, path)
        self._attachment_service = None

    def add(
        self,
        attachment,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.NetworkAttachmentWriter.write_one(attachment, writer, 'attachment')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NetworkAttachmentReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of attachments to return. If not specified all the attachments are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NetworkAttachmentReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def attachment_service(self, id):
        """
        """
        return NetworkAttachmentService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.attachment_service(path)
        return self.attachment_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'NetworkAttachmentsService:%s' % self._path


class NetworkFilterService(Service):
    """
    Manages a network filter.
    [source,xml]
    ----
    <network_filter id="00000019-0019-0019-0019-00000000026b">
      <name>example-network-filter-b</name>
      <version>
        <major>4</major>
        <minor>0</minor>
        <build>-1</build>
        <revision>-1</revision>
      </version>
    </network_filter>
    ----
    Please note that version is referring to the minimal support version for the specific filter.
    """

    def __init__(self, connection, path):
        super(NetworkFilterService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        Retrieves a representation of the network filter.

        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NetworkFilterReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'NetworkFilterService:%s' % self._path


class NetworkFiltersService(Service):
    """
    Represents a readonly network filters sub-collection.
    The network filter enables to filter packets send to/from the VM's nic according to defined rules.
    For more information please refer to <<services/network-filter,NetworkFilter>> service documentation
    Network filters are supported in different versions, starting from version 3.0.
    A network filter is defined for each vnic profile.
    A vnic profile is defined for a specific network.
    A network can be assigned to several different clusters. In the future, each network will be defined in
    cluster level.
    Currently, each network is being defined at data center level. Potential network filters for each network
    are determined by the network's data center compatibility version V.
    V must be >= the network filter version in order to configure this network filter for a specific network.
    Please note, that if a network is assigned to cluster with a version supporting a network filter, the filter
    may not be available due to the data center version being smaller then the network filter's version.
    Example of listing all of the supported network filters for a specific cluster:
    [source]
    ----
    GET http://localhost:8080/ovirt-engine/api/clusters/{cluster:id}/networkfilters
    ----
    Output:
    [source,xml]
    ----
    <network_filters>
      <network_filter id="00000019-0019-0019-0019-00000000026c">
        <name>example-network-filter-a</name>
        <version>
          <major>4</major>
          <minor>0</minor>
          <build>-1</build>
          <revision>-1</revision>
        </version>
      </network_filter>
      <network_filter id="00000019-0019-0019-0019-00000000026b">
        <name>example-network-filter-b</name>
        <version>
          <major>4</major>
          <minor>0</minor>
          <build>-1</build>
          <revision>-1</revision>
        </version>
      </network_filter>
      <network_filter id="00000019-0019-0019-0019-00000000026a">
        <name>example-network-filter-a</name>
        <version>
          <major>3</major>
          <minor>0</minor>
          <build>-1</build>
          <revision>-1</revision>
        </version>
      </network_filter>
    </network_filters>
    ----
    """

    def __init__(self, connection, path):
        super(NetworkFiltersService, self).__init__(connection, path)
        self._network_filter_service = None

    def list(
        self,
    ):
        """
        Retrieves the representations of the network filters.

        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NetworkFilterReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def network_filter_service(self, id):
        """
        """
        return NetworkFilterService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.network_filter_service(path)
        return self.network_filter_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'NetworkFiltersService:%s' % self._path


class NetworkLabelService(Service):
    """
    """

    def __init__(self, connection, path):
        super(NetworkLabelService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NetworkLabelReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'NetworkLabelService:%s' % self._path


class NetworkLabelsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(NetworkLabelsService, self).__init__(connection, path)
        self._label_service = None

    def add(
        self,
        label,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.NetworkLabelWriter.write_one(label, writer, 'label')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NetworkLabelReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of labels to return. If not specified all the labels are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NetworkLabelReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def label_service(self, id):
        """
        """
        return NetworkLabelService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.label_service(path)
        return self.label_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'NetworkLabelsService:%s' % self._path


class NetworksService(Service):
    """
    """

    def __init__(self, connection, path):
        super(NetworksService, self).__init__(connection, path)
        self._network_service = None

    def add(
        self,
        network,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.NetworkWriter.write_one(network, writer, 'network')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NetworkReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        case_sensitive=None,
        max=None,
        search=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of networks to return. If not specified all the networks are returned.
        search -- A query string used to restrict the returned networks.
        case_sensitive -- Indicates if the search performed using the `search` parameter should be performed taking case into
        account. The default value is `true`, which means that case is taken into account. If you want to search
        ignoring case set it to `false`.
        """
        query = {}
        if case_sensitive is not None:
            case_sensitive = Writer.render_boolean(case_sensitive)
            query['case_sensitive'] = case_sensitive
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        if search is not None:
            query['search'] = search
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NetworkReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def network_service(self, id):
        """
        """
        return NetworkService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.network_service(path)
        return self.network_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'NetworksService:%s' % self._path


class OpenstackImageService(Service):
    """
    """

    def __init__(self, connection, path):
        super(OpenstackImageService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.OpenStackImageReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def import_(
        self,
        async=None,
        disk=None,
        import_as_template=None,
        storage_domain=None,
        template=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the import should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if disk is not None:
            writers.DiskWriter.write_one(disk, writer)
        if import_as_template is not None:
            writer.write_boolean('import_as_template', import_as_template)
        if storage_domain is not None:
            writers.StorageDomainWriter.write_one(storage_domain, writer)
        if template is not None:
            writers.TemplateWriter.write_one(template, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'import'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'OpenstackImageService:%s' % self._path


class OpenstackImageProviderService(ExternalProviderService):
    """
    """

    def __init__(self, connection, path):
        super(OpenstackImageProviderService, self).__init__(connection, path)
        self._certificates_service = None
        self._images_service = None

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.OpenStackImageProviderReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def import_certificates(
        self,
        certificates=None,
    ):
        """
        Keyword arguments:
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if certificates is not None:
            writers.CertificateWriter.write_many(certificates, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'importcertificates'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def test_connectivity(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the test should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'testconnectivity'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def update(
        self,
        provider,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.OpenStackImageProviderWriter.write_one(provider, writer, 'provider')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.OpenStackImageProviderReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def certificates_service(self):
        """
        """
        return ExternalProviderCertificatesService(self._connection, '%s/certificates' % self._path)

    def images_service(self):
        """
        """
        return OpenstackImagesService(self._connection, '%s/images' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'certificates':
            return self.certificates_service()
        if path.startswith('certificates/'):
            return self.certificates_service().service(path[13:])
        if path == 'images':
            return self.images_service()
        if path.startswith('images/'):
            return self.images_service().service(path[7:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'OpenstackImageProviderService:%s' % self._path


class OpenstackImageProvidersService(Service):
    """
    """

    def __init__(self, connection, path):
        super(OpenstackImageProvidersService, self).__init__(connection, path)
        self._provider_service = None

    def add(
        self,
        provider,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.OpenStackImageProviderWriter.write_one(provider, writer, 'provider')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.OpenStackImageProviderReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of providers to return. If not specified all the providers are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.OpenStackImageProviderReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def provider_service(self, id):
        """
        """
        return OpenstackImageProviderService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.provider_service(path)
        return self.provider_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'OpenstackImageProvidersService:%s' % self._path


class OpenstackImagesService(Service):
    """
    """

    def __init__(self, connection, path):
        super(OpenstackImagesService, self).__init__(connection, path)
        self._image_service = None

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of images to return. If not specified all the images are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.OpenStackImageReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def image_service(self, id):
        """
        """
        return OpenstackImageService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.image_service(path)
        return self.image_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'OpenstackImagesService:%s' % self._path


class OpenstackNetworkService(Service):
    """
    """

    def __init__(self, connection, path):
        super(OpenstackNetworkService, self).__init__(connection, path)
        self._subnets_service = None

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.OpenStackNetworkReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def import_(
        self,
        async=None,
        data_center=None,
    ):
        """
        This operation imports an external network into oVirt.
        The network will be added to the data center specified.

        Keyword arguments:
        data_center -- The data center into which the network is to be imported.
        Data center is mandatory, and can be specified
        using the `id` or `name` attributes, the rest of
        the attributes will be ignored.
        async -- Indicates if the import should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if data_center is not None:
            writers.DataCenterWriter.write_one(data_center, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'import'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def subnets_service(self):
        """
        """
        return OpenstackSubnetsService(self._connection, '%s/subnets' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'subnets':
            return self.subnets_service()
        if path.startswith('subnets/'):
            return self.subnets_service().service(path[8:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'OpenstackNetworkService:%s' % self._path


class OpenstackNetworkProviderService(ExternalProviderService):
    """
    """

    def __init__(self, connection, path):
        super(OpenstackNetworkProviderService, self).__init__(connection, path)
        self._certificates_service = None
        self._networks_service = None

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.OpenStackNetworkProviderReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def import_certificates(
        self,
        certificates=None,
    ):
        """
        Keyword arguments:
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if certificates is not None:
            writers.CertificateWriter.write_many(certificates, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'importcertificates'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def test_connectivity(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the test should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'testconnectivity'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def update(
        self,
        provider,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.OpenStackNetworkProviderWriter.write_one(provider, writer, 'provider')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.OpenStackNetworkProviderReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def certificates_service(self):
        """
        """
        return ExternalProviderCertificatesService(self._connection, '%s/certificates' % self._path)

    def networks_service(self):
        """
        """
        return OpenstackNetworksService(self._connection, '%s/networks' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'certificates':
            return self.certificates_service()
        if path.startswith('certificates/'):
            return self.certificates_service().service(path[13:])
        if path == 'networks':
            return self.networks_service()
        if path.startswith('networks/'):
            return self.networks_service().service(path[9:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'OpenstackNetworkProviderService:%s' % self._path


class OpenstackNetworkProvidersService(Service):
    """
    """

    def __init__(self, connection, path):
        super(OpenstackNetworkProvidersService, self).__init__(connection, path)
        self._provider_service = None

    def add(
        self,
        provider,
    ):
        """
        The operation adds a new network provider to the system.
        If the `type` property is not present, a default value of `NEUTRON` will be used.

        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.OpenStackNetworkProviderWriter.write_one(provider, writer, 'provider')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.OpenStackNetworkProviderReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of providers to return. If not specified all the providers are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.OpenStackNetworkProviderReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def provider_service(self, id):
        """
        """
        return OpenstackNetworkProviderService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.provider_service(path)
        return self.provider_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'OpenstackNetworkProvidersService:%s' % self._path


class OpenstackNetworksService(Service):
    """
    """

    def __init__(self, connection, path):
        super(OpenstackNetworksService, self).__init__(connection, path)
        self._network_service = None

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of networks to return. If not specified all the networks are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.OpenStackNetworkReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def network_service(self, id):
        """
        """
        return OpenstackNetworkService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.network_service(path)
        return self.network_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'OpenstackNetworksService:%s' % self._path


class OpenstackSubnetService(Service):
    """
    """

    def __init__(self, connection, path):
        super(OpenstackSubnetService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.OpenStackSubnetReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'OpenstackSubnetService:%s' % self._path


class OpenstackSubnetsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(OpenstackSubnetsService, self).__init__(connection, path)
        self._subnet_service = None

    def add(
        self,
        subnet,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.OpenStackSubnetWriter.write_one(subnet, writer, 'subnet')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.OpenStackSubnetReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of sub-networks to return. If not specified all the sub-networks are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.OpenStackSubnetReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def subnet_service(self, id):
        """
        """
        return OpenstackSubnetService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.subnet_service(path)
        return self.subnet_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'OpenstackSubnetsService:%s' % self._path


class OpenstackVolumeAuthenticationKeyService(Service):
    """
    """

    def __init__(self, connection, path):
        super(OpenstackVolumeAuthenticationKeyService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.OpenstackVolumeAuthenticationKeyReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        key,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.OpenstackVolumeAuthenticationKeyWriter.write_one(key, writer, 'key')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.OpenstackVolumeAuthenticationKeyReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'OpenstackVolumeAuthenticationKeyService:%s' % self._path


class OpenstackVolumeAuthenticationKeysService(Service):
    """
    """

    def __init__(self, connection, path):
        super(OpenstackVolumeAuthenticationKeysService, self).__init__(connection, path)
        self._key_service = None

    def add(
        self,
        key,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.OpenstackVolumeAuthenticationKeyWriter.write_one(key, writer, 'key')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.OpenstackVolumeAuthenticationKeyReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of keys to return. If not specified all the keys are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.OpenstackVolumeAuthenticationKeyReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def key_service(self, id):
        """
        """
        return OpenstackVolumeAuthenticationKeyService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.key_service(path)
        return self.key_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'OpenstackVolumeAuthenticationKeysService:%s' % self._path


class OpenstackVolumeProviderService(ExternalProviderService):
    """
    """

    def __init__(self, connection, path):
        super(OpenstackVolumeProviderService, self).__init__(connection, path)
        self._authentication_keys_service = None
        self._certificates_service = None
        self._volume_types_service = None

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.OpenStackVolumeProviderReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def import_certificates(
        self,
        certificates=None,
    ):
        """
        Keyword arguments:
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if certificates is not None:
            writers.CertificateWriter.write_many(certificates, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'importcertificates'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def test_connectivity(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the test should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'testconnectivity'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def update(
        self,
        provider,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.OpenStackVolumeProviderWriter.write_one(provider, writer, 'provider')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.OpenStackVolumeProviderReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def authentication_keys_service(self):
        """
        """
        return OpenstackVolumeAuthenticationKeysService(self._connection, '%s/authenticationkeys' % self._path)

    def certificates_service(self):
        """
        """
        return ExternalProviderCertificatesService(self._connection, '%s/certificates' % self._path)

    def volume_types_service(self):
        """
        """
        return OpenstackVolumeTypesService(self._connection, '%s/volumetypes' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'authenticationkeys':
            return self.authentication_keys_service()
        if path.startswith('authenticationkeys/'):
            return self.authentication_keys_service().service(path[19:])
        if path == 'certificates':
            return self.certificates_service()
        if path.startswith('certificates/'):
            return self.certificates_service().service(path[13:])
        if path == 'volumetypes':
            return self.volume_types_service()
        if path.startswith('volumetypes/'):
            return self.volume_types_service().service(path[12:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'OpenstackVolumeProviderService:%s' % self._path


class OpenstackVolumeProvidersService(Service):
    """
    """

    def __init__(self, connection, path):
        super(OpenstackVolumeProvidersService, self).__init__(connection, path)
        self._provider_service = None

    def add(
        self,
        provider,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.OpenStackVolumeProviderWriter.write_one(provider, writer, 'provider')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.OpenStackVolumeProviderReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of providers to return. If not specified all the providers are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.OpenStackVolumeProviderReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def provider_service(self, id):
        """
        """
        return OpenstackVolumeProviderService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.provider_service(path)
        return self.provider_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'OpenstackVolumeProvidersService:%s' % self._path


class OpenstackVolumeTypeService(Service):
    """
    """

    def __init__(self, connection, path):
        super(OpenstackVolumeTypeService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.OpenStackVolumeTypeReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'OpenstackVolumeTypeService:%s' % self._path


class OpenstackVolumeTypesService(Service):
    """
    """

    def __init__(self, connection, path):
        super(OpenstackVolumeTypesService, self).__init__(connection, path)
        self._type_service = None

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of volume types to return. If not specified all the volume types are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.OpenStackVolumeTypeReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def type_service(self, id):
        """
        """
        return OpenstackVolumeTypeService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.type_service(path)
        return self.type_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'OpenstackVolumeTypesService:%s' % self._path


class OperatingSystemService(Service):
    """
    """

    def __init__(self, connection, path):
        super(OperatingSystemService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.OperatingSystemInfoReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'OperatingSystemService:%s' % self._path


class OperatingSystemsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(OperatingSystemsService, self).__init__(connection, path)
        self._operating_system_service = None

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of networks to return. If not specified all the networks are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.OperatingSystemInfoReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def operating_system_service(self, id):
        """
        """
        return OperatingSystemService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.operating_system_service(path)
        return self.operating_system_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'OperatingSystemsService:%s' % self._path


class PermissionService(Service):
    """
    """

    def __init__(self, connection, path):
        super(PermissionService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.PermissionReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'PermissionService:%s' % self._path


class PermitService(Service):
    """
    """

    def __init__(self, connection, path):
        super(PermitService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.PermitReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'PermitService:%s' % self._path


class PermitsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(PermitsService, self).__init__(connection, path)
        self._permit_service = None

    def add(
        self,
        permit,
    ):
        """
        Adds a permit to the set aggregated by parent role. The permit must be one retrieved from the capabilities
        resource.

        Keyword arguments:
        permit -- The permit to add.
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.PermitWriter.write_one(permit, writer, 'permit')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.PermitReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of permits to return. If not specified all the permits are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.PermitReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def permit_service(self, id):
        """
        Sub-resource locator method, returns individual permit resource on which the remainder of the URI is dispatched.
        """
        return PermitService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.permit_service(path)
        return self.permit_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'PermitsService:%s' % self._path


class QosService(Service):
    """
    """

    def __init__(self, connection, path):
        super(QosService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.QosReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        qos,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.QosWriter.write_one(qos, writer, 'qos')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.QosReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'QosService:%s' % self._path


class QossService(Service):
    """
    """

    def __init__(self, connection, path):
        super(QossService, self).__init__(connection, path)
        self._qos_service = None

    def add(
        self,
        qos,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.QosWriter.write_one(qos, writer, 'qos')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.QosReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of QoS descriptors to return. If not specified all the descriptors are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.QosReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def qos_service(self, id):
        """
        """
        return QosService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.qos_service(path)
        return self.qos_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'QossService:%s' % self._path


class QuotaService(Service):
    """
    """

    def __init__(self, connection, path):
        super(QuotaService, self).__init__(connection, path)
        self._permissions_service = None
        self._quota_cluster_limits_service = None
        self._quota_storage_limits_service = None

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.QuotaReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        quota,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.QuotaWriter.write_one(quota, writer, 'quota')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.QuotaReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def permissions_service(self):
        """
        """
        return AssignedPermissionsService(self._connection, '%s/permissions' % self._path)

    def quota_cluster_limits_service(self):
        """
        """
        return QuotaClusterLimitsService(self._connection, '%s/quotaclusterlimits' % self._path)

    def quota_storage_limits_service(self):
        """
        """
        return QuotaStorageLimitsService(self._connection, '%s/quotastoragelimits' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'permissions':
            return self.permissions_service()
        if path.startswith('permissions/'):
            return self.permissions_service().service(path[12:])
        if path == 'quotaclusterlimits':
            return self.quota_cluster_limits_service()
        if path.startswith('quotaclusterlimits/'):
            return self.quota_cluster_limits_service().service(path[19:])
        if path == 'quotastoragelimits':
            return self.quota_storage_limits_service()
        if path.startswith('quotastoragelimits/'):
            return self.quota_storage_limits_service().service(path[19:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'QuotaService:%s' % self._path


class QuotaClusterLimitService(Service):
    """
    """

    def __init__(self, connection, path):
        super(QuotaClusterLimitService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.QuotaClusterLimitReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'QuotaClusterLimitService:%s' % self._path


class QuotaClusterLimitsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(QuotaClusterLimitsService, self).__init__(connection, path)
        self._limit_service = None

    def add(
        self,
        limit,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.QuotaClusterLimitWriter.write_one(limit, writer, 'limit')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.QuotaClusterLimitReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of limits to return. If not specified all the limits are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.QuotaClusterLimitReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def limit_service(self, id):
        """
        """
        return QuotaClusterLimitService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.limit_service(path)
        return self.limit_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'QuotaClusterLimitsService:%s' % self._path


class QuotaStorageLimitService(Service):
    """
    """

    def __init__(self, connection, path):
        super(QuotaStorageLimitService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.QuotaStorageLimitReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the update should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'QuotaStorageLimitService:%s' % self._path


class QuotaStorageLimitsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(QuotaStorageLimitsService, self).__init__(connection, path)
        self._limit_service = None

    def add(
        self,
        limit,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.QuotaStorageLimitWriter.write_one(limit, writer, 'limit')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.QuotaStorageLimitReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of limits to return. If not specified all the limits are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.QuotaStorageLimitReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def limit_service(self, id):
        """
        """
        return QuotaStorageLimitService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.limit_service(path)
        return self.limit_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'QuotaStorageLimitsService:%s' % self._path


class QuotasService(Service):
    """
    """

    def __init__(self, connection, path):
        super(QuotasService, self).__init__(connection, path)
        self._quota_service = None

    def add(
        self,
        quota,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.QuotaWriter.write_one(quota, writer, 'quota')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.QuotaReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of quota descriptors to return. If not specified all the descriptors are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.QuotaReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def quota_service(self, id):
        """
        """
        return QuotaService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.quota_service(path)
        return self.quota_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'QuotasService:%s' % self._path


class RoleService(Service):
    """
    """

    def __init__(self, connection, path):
        super(RoleService, self).__init__(connection, path)
        self._permits_service = None

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.RoleReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        role,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.RoleWriter.write_one(role, writer, 'role')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.RoleReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def permits_service(self):
        """
        """
        return PermitsService(self._connection, '%s/permits' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'permits':
            return self.permits_service()
        if path.startswith('permits/'):
            return self.permits_service().service(path[8:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'RoleService:%s' % self._path


class RolesService(Service):
    """
    Provides read-only access to the global set of roles
    """

    def __init__(self, connection, path):
        super(RolesService, self).__init__(connection, path)
        self._role_service = None

    def add(
        self,
        role,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.RoleWriter.write_one(role, writer, 'role')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.RoleReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of roles to return. If not specified all the roles are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.RoleReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def role_service(self, id):
        """
        Sub-resource locator method, returns individual role resource on which the remainder of the URI is dispatched.
        """
        return RoleService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.role_service(path)
        return self.role_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'RolesService:%s' % self._path


class SchedulingPoliciesService(Service):
    """
    """

    def __init__(self, connection, path):
        super(SchedulingPoliciesService, self).__init__(connection, path)
        self._policy_service = None

    def add(
        self,
        policy,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.SchedulingPolicyWriter.write_one(policy, writer, 'policy')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.SchedulingPolicyReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        filter=None,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of policies to return. If not specified all the policies are returned.
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        query = {}
        if filter is not None:
            filter = Writer.render_boolean(filter)
            query['filter'] = filter
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.SchedulingPolicyReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def policy_service(self, id):
        """
        """
        return SchedulingPolicyService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.policy_service(path)
        return self.policy_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'SchedulingPoliciesService:%s' % self._path


class SchedulingPolicyService(Service):
    """
    """

    def __init__(self, connection, path):
        super(SchedulingPolicyService, self).__init__(connection, path)
        self._balances_service = None
        self._filters_service = None
        self._weights_service = None

    def get(
        self,
        filter=None,
    ):
        """
        Keyword arguments:
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        query = {}
        if filter is not None:
            filter = Writer.render_boolean(filter)
            query['filter'] = filter
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.SchedulingPolicyReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        policy,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.SchedulingPolicyWriter.write_one(policy, writer, 'policy')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.SchedulingPolicyReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def balances_service(self):
        """
        """
        return BalancesService(self._connection, '%s/balances' % self._path)

    def filters_service(self):
        """
        """
        return FiltersService(self._connection, '%s/filters' % self._path)

    def weights_service(self):
        """
        """
        return WeightsService(self._connection, '%s/weights' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'balances':
            return self.balances_service()
        if path.startswith('balances/'):
            return self.balances_service().service(path[9:])
        if path == 'filters':
            return self.filters_service()
        if path.startswith('filters/'):
            return self.filters_service().service(path[8:])
        if path == 'weights':
            return self.weights_service()
        if path.startswith('weights/'):
            return self.weights_service().service(path[8:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'SchedulingPolicyService:%s' % self._path


class SchedulingPolicyUnitService(Service):
    """
    """

    def __init__(self, connection, path):
        super(SchedulingPolicyUnitService, self).__init__(connection, path)

    def get(
        self,
        filter=None,
    ):
        """
        Keyword arguments:
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        query = {}
        if filter is not None:
            filter = Writer.render_boolean(filter)
            query['filter'] = filter
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.SchedulingPolicyUnitReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'SchedulingPolicyUnitService:%s' % self._path


class SchedulingPolicyUnitsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(SchedulingPolicyUnitsService, self).__init__(connection, path)
        self._unit_service = None

    def list(
        self,
        filter=None,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of policy units to return. If not specified all the policy units are returned.
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        query = {}
        if filter is not None:
            filter = Writer.render_boolean(filter)
            query['filter'] = filter
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.SchedulingPolicyUnitReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def unit_service(self, id):
        """
        """
        return SchedulingPolicyUnitService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.unit_service(path)
        return self.unit_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'SchedulingPolicyUnitsService:%s' % self._path


class SnapshotService(Service):
    """
    """

    def __init__(self, connection, path):
        super(SnapshotService, self).__init__(connection, path)
        self._cdroms_service = None
        self._disks_service = None
        self._nics_service = None

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.SnapshotReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def restore(
        self,
        async=None,
        disks=None,
        restore_memory=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the restore should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if disks is not None:
            writers.DiskWriter.write_many(disks, writer)
        if restore_memory is not None:
            writer.write_boolean('restore_memory', restore_memory)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'restore'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def cdroms_service(self):
        """
        """
        return SnapshotCdromsService(self._connection, '%s/cdroms' % self._path)

    def disks_service(self):
        """
        """
        return SnapshotDisksService(self._connection, '%s/disks' % self._path)

    def nics_service(self):
        """
        """
        return SnapshotNicsService(self._connection, '%s/nics' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'cdroms':
            return self.cdroms_service()
        if path.startswith('cdroms/'):
            return self.cdroms_service().service(path[7:])
        if path == 'disks':
            return self.disks_service()
        if path.startswith('disks/'):
            return self.disks_service().service(path[6:])
        if path == 'nics':
            return self.nics_service()
        if path.startswith('nics/'):
            return self.nics_service().service(path[5:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'SnapshotService:%s' % self._path


class SnapshotCdromService(Service):
    """
    """

    def __init__(self, connection, path):
        super(SnapshotCdromService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.CdromReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'SnapshotCdromService:%s' % self._path


class SnapshotCdromsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(SnapshotCdromsService, self).__init__(connection, path)
        self._cdrom_service = None

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of CDROMS to return. If not specified all the CDROMS are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.CdromReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def cdrom_service(self, id):
        """
        """
        return SnapshotCdromService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.cdrom_service(path)
        return self.cdrom_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'SnapshotCdromsService:%s' % self._path


class SnapshotDiskService(Service):
    """
    """

    def __init__(self, connection, path):
        super(SnapshotDiskService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.DiskReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'SnapshotDiskService:%s' % self._path


class SnapshotDisksService(Service):
    """
    """

    def __init__(self, connection, path):
        super(SnapshotDisksService, self).__init__(connection, path)
        self._disk_service = None

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of disks to return. If not specified all the disks are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.DiskReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def disk_service(self, id):
        """
        """
        return SnapshotDiskService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.disk_service(path)
        return self.disk_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'SnapshotDisksService:%s' % self._path


class SnapshotNicService(Service):
    """
    """

    def __init__(self, connection, path):
        super(SnapshotNicService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NicReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'SnapshotNicService:%s' % self._path


class SnapshotNicsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(SnapshotNicsService, self).__init__(connection, path)
        self._nic_service = None

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of NICs to return. If not specified all the NICs are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NicReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def nic_service(self, id):
        """
        """
        return SnapshotNicService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.nic_service(path)
        return self.nic_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'SnapshotNicsService:%s' % self._path


class SnapshotsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(SnapshotsService, self).__init__(connection, path)
        self._snapshot_service = None

    def add(
        self,
        snapshot,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.SnapshotWriter.write_one(snapshot, writer, 'snapshot')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.SnapshotReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of snapshots to return. If not specified all the snapshots are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.SnapshotReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def snapshot_service(self, id):
        """
        """
        return SnapshotService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.snapshot_service(path)
        return self.snapshot_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'SnapshotsService:%s' % self._path


class SshPublicKeyService(Service):
    """
    """

    def __init__(self, connection, path):
        super(SshPublicKeyService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.SshPublicKeyReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        key,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.SshPublicKeyWriter.write_one(key, writer, 'key')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.SshPublicKeyReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'SshPublicKeyService:%s' % self._path


class SshPublicKeysService(Service):
    """
    """

    def __init__(self, connection, path):
        super(SshPublicKeysService, self).__init__(connection, path)
        self._key_service = None

    def add(
        self,
        key,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.SshPublicKeyWriter.write_one(key, writer, 'key')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.SshPublicKeyReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of keys to return. If not specified all the keys are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.SshPublicKeyReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def key_service(self, id):
        """
        """
        return SshPublicKeyService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.key_service(path)
        return self.key_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'SshPublicKeysService:%s' % self._path


class StatisticService(Service):
    """
    """

    def __init__(self, connection, path):
        super(StatisticService, self).__init__(connection, path)

    def get(
        self,
        statistic=None,
    ):
        """
        Keyword arguments:
        """
        query = {}
        if statistic is not None:
            query['statistic'] = statistic
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.StatisticReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'StatisticService:%s' % self._path


class StatisticsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(StatisticsService, self).__init__(connection, path)
        self._statistic_service = None

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of statistics to return. If not specified all the statistics are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.StatisticReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def statistic_service(self, id):
        """
        """
        return StatisticService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.statistic_service(path)
        return self.statistic_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'StatisticsService:%s' % self._path


class StepService(MeasurableService):
    """
    """

    def __init__(self, connection, path):
        super(StepService, self).__init__(connection, path)
        self._statistics_service = None

    def end(
        self,
        async=None,
        force=None,
        succeeded=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the action should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if force is not None:
            writer.write_boolean('force', force)
        if succeeded is not None:
            writer.write_boolean('succeeded', succeeded)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'end'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.StepReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def statistics_service(self):
        """
        """
        return StatisticsService(self._connection, '%s/statistics' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'statistics':
            return self.statistics_service()
        if path.startswith('statistics/'):
            return self.statistics_service().service(path[11:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'StepService:%s' % self._path


class StepsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(StepsService, self).__init__(connection, path)
        self._step_service = None

    def add(
        self,
        step,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.StepWriter.write_one(step, writer, 'step')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.StepReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of steps to return. If not specified all the steps are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.StepReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def step_service(self, id):
        """
        """
        return StepService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.step_service(path)
        return self.step_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'StepsService:%s' % self._path


class StorageService(Service):
    """
    """

    def __init__(self, connection, path):
        super(StorageService, self).__init__(connection, path)

    def get(
        self,
        report_status=None,
    ):
        """
        Keyword arguments:
        report_status -- Indicates if the status of the LUNs in the storage should be checked.
        Checking the status of the LUN is an heavy weight operation and
        this data is not always needed by the user.
        This parameter will give the option to not perform the status check of the LUNs.
        The default is `true` for backward compatibility.
        Here an example with the LUN status :
        [source,xml]
        ----
        <host_storage id="360014051136c20574f743bdbd28177fd">
          <logical_units>
            <logical_unit id="360014051136c20574f743bdbd28177fd">
              <lun_mapping>0</lun_mapping>
              <paths>1</paths>
              <product_id>lun0</product_id>
              <serial>SLIO-ORG_lun0_1136c205-74f7-43bd-bd28-177fd5ce6993</serial>
              <size>10737418240</size>
              <status>used</status>
              <vendor_id>LIO-ORG</vendor_id>
              <volume_group_id>O9Du7I-RahN-ECe1-dZ1w-nh0b-64io-MNzIBZ</volume_group_id>
            </logical_unit>
          </logical_units>
          <type>iscsi</type>
          <host id="8bb5ade5-e988-4000-8b93-dbfc6717fe50"/>
        </host_storage>
        ----
        Here an example without the LUN status :
        [source,xml]
        ----
        <host_storage id="360014051136c20574f743bdbd28177fd">
          <logical_units>
            <logical_unit id="360014051136c20574f743bdbd28177fd">
              <lun_mapping>0</lun_mapping>
              <paths>1</paths>
              <product_id>lun0</product_id>
              <serial>SLIO-ORG_lun0_1136c205-74f7-43bd-bd28-177fd5ce6993</serial>
              <size>10737418240</size>
              <vendor_id>LIO-ORG</vendor_id>
              <volume_group_id>O9Du7I-RahN-ECe1-dZ1w-nh0b-64io-MNzIBZ</volume_group_id>
            </logical_unit>
          </logical_units>
          <type>iscsi</type>
          <host id="8bb5ade5-e988-4000-8b93-dbfc6717fe50"/>
        </host_storage>
        ----
        """
        query = {}
        if report_status is not None:
            report_status = Writer.render_boolean(report_status)
            query['report_status'] = report_status
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.HostStorageReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'StorageService:%s' % self._path


class StorageDomainService(Service):
    """
    """

    def __init__(self, connection, path):
        super(StorageDomainService, self).__init__(connection, path)
        self._disk_profiles_service = None
        self._disk_snapshots_service = None
        self._disks_service = None
        self._files_service = None
        self._images_service = None
        self._permissions_service = None
        self._storage_connections_service = None
        self._templates_service = None
        self._vms_service = None

    def get(
        self,
        filter=None,
    ):
        """
        Keyword arguments:
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        query = {}
        if filter is not None:
            filter = Writer.render_boolean(filter)
            query['filter'] = filter
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.StorageDomainReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def is_attached(
        self,
        async=None,
        host=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the action should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if host is not None:
            writers.HostWriter.write_one(host, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'isattached'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            action = self._check_action(response)
            return action.is_attached
        else:
            self._check_fault(response)

    def refresh_luns(
        self,
        async=None,
        logical_units=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the refresh should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if logical_units is not None:
            writers.LogicalUnitWriter.write_many(logical_units, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'refreshluns'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
        destroy=None,
        format=None,
        host=None,
    ):
        """
        Removes the storage domain.
        Without any special parameters, the storage domain is detached from the system and removed fro the database. The
        storage domain can then be imported to the same or different setup, with all the data on it. If the storage isn't
        accessible the operation will fail.
        If the `destroy` parameter is `true` then the operation will always succeed, even if the storage isn't
        accessible, the failure is just ignored and the storage domain is removed from the database anyway.
        If the `format` parameter is `true` then the actual storage is formatted, and the metadata is removed from the
        LUN or directory, so it can no longer be imported to the same or a different setup.

        Keyword arguments:
        host -- Indicates what host should be used to remove the storage domain.
        This parameter is mandatory, and it can contain the name or the identifier of the host. For example, to use
        the host named `myhost` to remove the storage domain with identifer `123` send a request like this:
        [source]
        ----
        DELETE /ovirt-engine/api/storagedomains/123?host=myhost
        ----
        format -- Indicates if the actual storage should be formatted, removing all the metadata from the underlying LUN or
        directory.
        This parameter is optional, and the default value is `false`.
        destroy -- Indicates if the operation should succeed, and the storage domain removed from the database, even if the
        storage isn't accessible.
        This parameter is optiona, and the default value is `false`.
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        if destroy is not None:
            destroy = Writer.render_boolean(destroy)
            query['destroy'] = destroy
        if format is not None:
            format = Writer.render_boolean(format)
            query['format'] = format
        if host is not None:
            query['host'] = host
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        storage_domain,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.StorageDomainWriter.write_one(storage_domain, writer, 'storage_domain')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.StorageDomainReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def update_ovf_store(
        self,
        async=None,
    ):
        """
        This operation forces the update of the `OVF_STORE`
        of this storage domain.
        The `OVF_STORE` is a disk image that contains the meta-data
        of virtual machines and disks that reside in the
        storage domain. This meta-data is used in case the
        domain is imported or exported to or from a different
        data center or a different installation.
        By default the `OVF_STORE` is updated periodically
        (set by default to 60 minutes) but users might want to force an
        update after an important change, or when the they believe the
        `OVF_STORE` is corrupt.
        When initiated by the user, `OVF_STORE` update will be performed whether
        an update is needed or not.

        Keyword arguments:
        async -- Indicates if the `OVF_STORE` update should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'updateovfstore'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def disk_profiles_service(self):
        """
        """
        return AssignedDiskProfilesService(self._connection, '%s/diskprofiles' % self._path)

    def disk_snapshots_service(self):
        """
        """
        return DiskSnapshotsService(self._connection, '%s/disksnapshots' % self._path)

    def disks_service(self):
        """
        """
        return DisksService(self._connection, '%s/disks' % self._path)

    def files_service(self):
        """
        """
        return FilesService(self._connection, '%s/files' % self._path)

    def images_service(self):
        """
        """
        return ImagesService(self._connection, '%s/images' % self._path)

    def permissions_service(self):
        """
        """
        return AssignedPermissionsService(self._connection, '%s/permissions' % self._path)

    def storage_connections_service(self):
        """
        """
        return StorageDomainServerConnectionsService(self._connection, '%s/storageconnections' % self._path)

    def templates_service(self):
        """
        """
        return StorageDomainTemplatesService(self._connection, '%s/templates' % self._path)

    def vms_service(self):
        """
        """
        return StorageDomainVmsService(self._connection, '%s/vms' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'diskprofiles':
            return self.disk_profiles_service()
        if path.startswith('diskprofiles/'):
            return self.disk_profiles_service().service(path[13:])
        if path == 'disksnapshots':
            return self.disk_snapshots_service()
        if path.startswith('disksnapshots/'):
            return self.disk_snapshots_service().service(path[14:])
        if path == 'disks':
            return self.disks_service()
        if path.startswith('disks/'):
            return self.disks_service().service(path[6:])
        if path == 'files':
            return self.files_service()
        if path.startswith('files/'):
            return self.files_service().service(path[6:])
        if path == 'images':
            return self.images_service()
        if path.startswith('images/'):
            return self.images_service().service(path[7:])
        if path == 'permissions':
            return self.permissions_service()
        if path.startswith('permissions/'):
            return self.permissions_service().service(path[12:])
        if path == 'storageconnections':
            return self.storage_connections_service()
        if path.startswith('storageconnections/'):
            return self.storage_connections_service().service(path[19:])
        if path == 'templates':
            return self.templates_service()
        if path.startswith('templates/'):
            return self.templates_service().service(path[10:])
        if path == 'vms':
            return self.vms_service()
        if path.startswith('vms/'):
            return self.vms_service().service(path[4:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'StorageDomainService:%s' % self._path


class StorageDomainContentDiskService(Service):
    """
    """

    def __init__(self, connection, path):
        super(StorageDomainContentDiskService, self).__init__(connection, path)

    def get(
        self,
        filter=None,
    ):
        """
        Keyword arguments:
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        query = {}
        if filter is not None:
            filter = Writer.render_boolean(filter)
            query['filter'] = filter
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.DiskReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'StorageDomainContentDiskService:%s' % self._path


class StorageDomainContentDisksService(Service):
    """
    """

    def __init__(self, connection, path):
        super(StorageDomainContentDisksService, self).__init__(connection, path)
        self._disk_service = None

    def list(
        self,
        case_sensitive=None,
        max=None,
        search=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of disks to return. If not specified all the disks are returned.
        search -- A query string used to restrict the returned disks.
        case_sensitive -- Indicates if the search performed using the `search` parameter should be performed taking case into
        account. The default value is `true`, which means that case is taken into account. If you want to search
        ignoring case set it to `false`.
        """
        query = {}
        if case_sensitive is not None:
            case_sensitive = Writer.render_boolean(case_sensitive)
            query['case_sensitive'] = case_sensitive
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        if search is not None:
            query['search'] = search
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.DiskReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def disk_service(self, id):
        """
        """
        return StorageDomainContentDiskService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.disk_service(path)
        return self.disk_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'StorageDomainContentDisksService:%s' % self._path


class StorageDomainServerConnectionService(Service):
    """
    """

    def __init__(self, connection, path):
        super(StorageDomainServerConnectionService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.StorageConnectionReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the action should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'StorageDomainServerConnectionService:%s' % self._path


class StorageDomainServerConnectionsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(StorageDomainServerConnectionsService, self).__init__(connection, path)
        self._connection_service = None

    def add(
        self,
        connection,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.StorageConnectionWriter.write_one(connection, writer, 'connection')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.StorageConnectionReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of connections to return. If not specified all the connections are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.StorageConnectionReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def connection_service(self, id):
        """
        """
        return StorageDomainServerConnectionService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.connection_service(path)
        return self.connection_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'StorageDomainServerConnectionsService:%s' % self._path


class StorageDomainTemplateService(Service):
    """
    """

    def __init__(self, connection, path):
        super(StorageDomainTemplateService, self).__init__(connection, path)
        self._disks_service = None

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.TemplateReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def import_(
        self,
        async=None,
        clone=None,
        cluster=None,
        exclusive=None,
        storage_domain=None,
        template=None,
        vm=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the import should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if clone is not None:
            writer.write_boolean('clone', clone)
        if cluster is not None:
            writers.ClusterWriter.write_one(cluster, writer)
        if exclusive is not None:
            writer.write_boolean('exclusive', exclusive)
        if storage_domain is not None:
            writers.StorageDomainWriter.write_one(storage_domain, writer)
        if template is not None:
            writers.TemplateWriter.write_one(template, writer)
        if vm is not None:
            writers.VmWriter.write_one(vm, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'import'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def register(
        self,
        async=None,
        clone=None,
        cluster=None,
        exclusive=None,
        template=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the registration should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if clone is not None:
            writer.write_boolean('clone', clone)
        if cluster is not None:
            writers.ClusterWriter.write_one(cluster, writer)
        if exclusive is not None:
            writer.write_boolean('exclusive', exclusive)
        if template is not None:
            writers.TemplateWriter.write_one(template, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'register'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def disks_service(self):
        """
        """
        return StorageDomainContentDisksService(self._connection, '%s/disks' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'disks':
            return self.disks_service()
        if path.startswith('disks/'):
            return self.disks_service().service(path[6:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'StorageDomainTemplateService:%s' % self._path


class StorageDomainTemplatesService(Service):
    """
    """

    def __init__(self, connection, path):
        super(StorageDomainTemplatesService, self).__init__(connection, path)
        self._template_service = None

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of templates to return. If not specified all the templates are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.TemplateReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def template_service(self, id):
        """
        """
        return StorageDomainTemplateService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.template_service(path)
        return self.template_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'StorageDomainTemplatesService:%s' % self._path


class StorageDomainVmService(Service):
    """
    """

    def __init__(self, connection, path):
        super(StorageDomainVmService, self).__init__(connection, path)
        self._disks_service = None

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.VmReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def import_(
        self,
        async=None,
        clone=None,
        cluster=None,
        collapse_snapshots=None,
        storage_domain=None,
        vm=None,
    ):
        """
        Keyword arguments:
        clone -- Indicates if the identifiers of the imported virtual machine
        should be regenerated.
        By default when a virtual machine is imported the identifiers
        are preserved. This means that the same virtual machine can't
        be imported multiple times, as that identifiers needs to be
        unique. To allow importing the same machine multiple times set
        this parameter to `true`, as the default is `false`.
        collapse_snapshots -- Indicates of the snapshots of the virtual machine that is imported
        should be collapsed, so that the result will be a virtual machine
        without snapshots.
        This parameter is optional, and if it isn't explicity specified the
        default value is `false`.
        async -- Indicates if the import should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if clone is not None:
            writer.write_boolean('clone', clone)
        if cluster is not None:
            writers.ClusterWriter.write_one(cluster, writer)
        if collapse_snapshots is not None:
            writer.write_boolean('collapse_snapshots', collapse_snapshots)
        if storage_domain is not None:
            writers.StorageDomainWriter.write_one(storage_domain, writer)
        if vm is not None:
            writers.VmWriter.write_one(vm, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'import'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def register(
        self,
        async=None,
        clone=None,
        cluster=None,
        vm=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the registration should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if clone is not None:
            writer.write_boolean('clone', clone)
        if cluster is not None:
            writers.ClusterWriter.write_one(cluster, writer)
        if vm is not None:
            writers.VmWriter.write_one(vm, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'register'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def disks_service(self):
        """
        """
        return StorageDomainContentDisksService(self._connection, '%s/disks' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'disks':
            return self.disks_service()
        if path.startswith('disks/'):
            return self.disks_service().service(path[6:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'StorageDomainVmService:%s' % self._path


class StorageDomainVmsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(StorageDomainVmsService, self).__init__(connection, path)
        self._vm_service = None

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of virtual machines to return. If not specified all the virtual machines are
        returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.VmReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def vm_service(self, id):
        """
        """
        return StorageDomainVmService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.vm_service(path)
        return self.vm_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'StorageDomainVmsService:%s' % self._path


class StorageDomainsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(StorageDomainsService, self).__init__(connection, path)
        self._storage_domain_service = None

    def add(
        self,
        storage_domain,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.StorageDomainWriter.write_one(storage_domain, writer, 'storage_domain')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.StorageDomainReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        case_sensitive=None,
        filter=None,
        max=None,
        search=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of storage domains to return. If not specified all the storage domains are returned.
        search -- A query string used to restrict the returned storage domains.
        case_sensitive -- Indicates if the search performed using the `search` parameter should be performed taking case into
        account. The default value is `true`, which means that case is taken into account. If you want to search
        ignoring case set it to `false`.
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        query = {}
        if case_sensitive is not None:
            case_sensitive = Writer.render_boolean(case_sensitive)
            query['case_sensitive'] = case_sensitive
        if filter is not None:
            filter = Writer.render_boolean(filter)
            query['filter'] = filter
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        if search is not None:
            query['search'] = search
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.StorageDomainReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def storage_domain_service(self, id):
        """
        """
        return StorageDomainService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.storage_domain_service(path)
        return self.storage_domain_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'StorageDomainsService:%s' % self._path


class StorageServerConnectionService(Service):
    """
    """

    def __init__(self, connection, path):
        super(StorageServerConnectionService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.StorageConnectionReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        connection,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.StorageConnectionWriter.write_one(connection, writer, 'connection')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.StorageConnectionReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'StorageServerConnectionService:%s' % self._path


class StorageServerConnectionExtensionService(Service):
    """
    """

    def __init__(self, connection, path):
        super(StorageServerConnectionExtensionService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.StorageConnectionExtensionReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        extension,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.StorageConnectionExtensionWriter.write_one(extension, writer, 'extension')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.StorageConnectionExtensionReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'StorageServerConnectionExtensionService:%s' % self._path


class StorageServerConnectionExtensionsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(StorageServerConnectionExtensionsService, self).__init__(connection, path)
        self._storage_connection_extension_service = None

    def add(
        self,
        extension,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.StorageConnectionExtensionWriter.write_one(extension, writer, 'extension')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.StorageConnectionExtensionReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of extensions to return. If not specified all the extensions are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.StorageConnectionExtensionReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def storage_connection_extension_service(self, id):
        """
        """
        return StorageServerConnectionExtensionService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.storage_connection_extension_service(path)
        return self.storage_connection_extension_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'StorageServerConnectionExtensionsService:%s' % self._path


class StorageServerConnectionsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(StorageServerConnectionsService, self).__init__(connection, path)
        self._storage_connection_service = None

    def add(
        self,
        connection,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.StorageConnectionWriter.write_one(connection, writer, 'connection')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.StorageConnectionReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of connections to return. If not specified all the connections are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.StorageConnectionReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def storage_connection_service(self, id):
        """
        """
        return StorageServerConnectionService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.storage_connection_service(path)
        return self.storage_connection_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'StorageServerConnectionsService:%s' % self._path


class SystemService(Service):
    """
    """

    def __init__(self, connection, path):
        super(SystemService, self).__init__(connection, path)
        self._affinity_labels_service = None
        self._bookmarks_service = None
        self._cluster_levels_service = None
        self._clusters_service = None
        self._cpu_profiles_service = None
        self._data_centers_service = None
        self._disk_profiles_service = None
        self._disks_service = None
        self._domains_service = None
        self._events_service = None
        self._external_host_providers_service = None
        self._groups_service = None
        self._hosts_service = None
        self._icons_service = None
        self._instance_types_service = None
        self._jobs_service = None
        self._katello_errata_service = None
        self._mac_pools_service = None
        self._network_filters_service = None
        self._networks_service = None
        self._openstack_image_providers_service = None
        self._openstack_network_providers_service = None
        self._openstack_volume_providers_service = None
        self._operating_systems_service = None
        self._permissions_service = None
        self._roles_service = None
        self._scheduling_policies_service = None
        self._scheduling_policy_units_service = None
        self._storage_connections_service = None
        self._storage_domains_service = None
        self._tags_service = None
        self._templates_service = None
        self._users_service = None
        self._vm_pools_service = None
        self._vms_service = None
        self._vnic_profiles_service = None

    def get(
        self,
    ):
        """
        Returns basic information describing the API, like the product name, the version number and a summary of the
        number of relevant objects.

        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.ApiReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def reload_configurations(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the reload should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'reloadconfigurations'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def affinity_labels_service(self):
        """
        List all known affinity labels.
        """
        return AffinityLabelsService(self._connection, '%s/affinitylabels' % self._path)

    def bookmarks_service(self):
        """
        """
        return BookmarksService(self._connection, '%s/bookmarks' % self._path)

    def cluster_levels_service(self):
        """
        Reference to the service that provides information about the cluster levels supported by the system.
        """
        return ClusterLevelsService(self._connection, '%s/clusterlevels' % self._path)

    def clusters_service(self):
        """
        """
        return ClustersService(self._connection, '%s/clusters' % self._path)

    def cpu_profiles_service(self):
        """
        """
        return CpuProfilesService(self._connection, '%s/cpuprofiles' % self._path)

    def data_centers_service(self):
        """
        """
        return DataCentersService(self._connection, '%s/datacenters' % self._path)

    def disk_profiles_service(self):
        """
        """
        return DiskProfilesService(self._connection, '%s/diskprofiles' % self._path)

    def disks_service(self):
        """
        """
        return DisksService(self._connection, '%s/disks' % self._path)

    def domains_service(self):
        """
        """
        return DomainsService(self._connection, '%s/domains' % self._path)

    def events_service(self):
        """
        """
        return EventsService(self._connection, '%s/events' % self._path)

    def external_host_providers_service(self):
        """
        """
        return ExternalHostProvidersService(self._connection, '%s/externalhostproviders' % self._path)

    def groups_service(self):
        """
        """
        return GroupsService(self._connection, '%s/groups' % self._path)

    def hosts_service(self):
        """
        """
        return HostsService(self._connection, '%s/hosts' % self._path)

    def icons_service(self):
        """
        """
        return IconsService(self._connection, '%s/icons' % self._path)

    def instance_types_service(self):
        """
        """
        return InstanceTypesService(self._connection, '%s/instancetypes' % self._path)

    def jobs_service(self):
        """
        """
        return JobsService(self._connection, '%s/jobs' % self._path)

    def katello_errata_service(self):
        """
        """
        return EngineKatelloErrataService(self._connection, '%s/katelloerrata' % self._path)

    def mac_pools_service(self):
        """
        """
        return MacPoolsService(self._connection, '%s/macpools' % self._path)

    def network_filters_service(self):
        """
        Network filters will enhance the admin ability to manage the network packets traffic from/to the participated
        VMs.
        """
        return NetworkFiltersService(self._connection, '%s/networkfilters' % self._path)

    def networks_service(self):
        """
        """
        return NetworksService(self._connection, '%s/networks' % self._path)

    def openstack_image_providers_service(self):
        """
        """
        return OpenstackImageProvidersService(self._connection, '%s/openstackimageproviders' % self._path)

    def openstack_network_providers_service(self):
        """
        """
        return OpenstackNetworkProvidersService(self._connection, '%s/openstacknetworkproviders' % self._path)

    def openstack_volume_providers_service(self):
        """
        """
        return OpenstackVolumeProvidersService(self._connection, '%s/openstackvolumeproviders' % self._path)

    def operating_systems_service(self):
        """
        """
        return OperatingSystemsService(self._connection, '%s/operatingsystems' % self._path)

    def permissions_service(self):
        """
        """
        return SystemPermissionsService(self._connection, '%s/permissions' % self._path)

    def roles_service(self):
        """
        """
        return RolesService(self._connection, '%s/roles' % self._path)

    def scheduling_policies_service(self):
        """
        """
        return SchedulingPoliciesService(self._connection, '%s/schedulingpolicies' % self._path)

    def scheduling_policy_units_service(self):
        """
        """
        return SchedulingPolicyUnitsService(self._connection, '%s/schedulingpolicyunits' % self._path)

    def storage_connections_service(self):
        """
        """
        return StorageServerConnectionsService(self._connection, '%s/storageconnections' % self._path)

    def storage_domains_service(self):
        """
        """
        return StorageDomainsService(self._connection, '%s/storagedomains' % self._path)

    def tags_service(self):
        """
        """
        return TagsService(self._connection, '%s/tags' % self._path)

    def templates_service(self):
        """
        """
        return TemplatesService(self._connection, '%s/templates' % self._path)

    def users_service(self):
        """
        """
        return UsersService(self._connection, '%s/users' % self._path)

    def vm_pools_service(self):
        """
        """
        return VmPoolsService(self._connection, '%s/vmpools' % self._path)

    def vms_service(self):
        """
        """
        return VmsService(self._connection, '%s/vms' % self._path)

    def vnic_profiles_service(self):
        """
        """
        return VnicProfilesService(self._connection, '%s/vnicprofiles' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'affinitylabels':
            return self.affinity_labels_service()
        if path.startswith('affinitylabels/'):
            return self.affinity_labels_service().service(path[15:])
        if path == 'bookmarks':
            return self.bookmarks_service()
        if path.startswith('bookmarks/'):
            return self.bookmarks_service().service(path[10:])
        if path == 'clusterlevels':
            return self.cluster_levels_service()
        if path.startswith('clusterlevels/'):
            return self.cluster_levels_service().service(path[14:])
        if path == 'clusters':
            return self.clusters_service()
        if path.startswith('clusters/'):
            return self.clusters_service().service(path[9:])
        if path == 'cpuprofiles':
            return self.cpu_profiles_service()
        if path.startswith('cpuprofiles/'):
            return self.cpu_profiles_service().service(path[12:])
        if path == 'datacenters':
            return self.data_centers_service()
        if path.startswith('datacenters/'):
            return self.data_centers_service().service(path[12:])
        if path == 'diskprofiles':
            return self.disk_profiles_service()
        if path.startswith('diskprofiles/'):
            return self.disk_profiles_service().service(path[13:])
        if path == 'disks':
            return self.disks_service()
        if path.startswith('disks/'):
            return self.disks_service().service(path[6:])
        if path == 'domains':
            return self.domains_service()
        if path.startswith('domains/'):
            return self.domains_service().service(path[8:])
        if path == 'events':
            return self.events_service()
        if path.startswith('events/'):
            return self.events_service().service(path[7:])
        if path == 'externalhostproviders':
            return self.external_host_providers_service()
        if path.startswith('externalhostproviders/'):
            return self.external_host_providers_service().service(path[22:])
        if path == 'groups':
            return self.groups_service()
        if path.startswith('groups/'):
            return self.groups_service().service(path[7:])
        if path == 'hosts':
            return self.hosts_service()
        if path.startswith('hosts/'):
            return self.hosts_service().service(path[6:])
        if path == 'icons':
            return self.icons_service()
        if path.startswith('icons/'):
            return self.icons_service().service(path[6:])
        if path == 'instancetypes':
            return self.instance_types_service()
        if path.startswith('instancetypes/'):
            return self.instance_types_service().service(path[14:])
        if path == 'jobs':
            return self.jobs_service()
        if path.startswith('jobs/'):
            return self.jobs_service().service(path[5:])
        if path == 'katelloerrata':
            return self.katello_errata_service()
        if path.startswith('katelloerrata/'):
            return self.katello_errata_service().service(path[14:])
        if path == 'macpools':
            return self.mac_pools_service()
        if path.startswith('macpools/'):
            return self.mac_pools_service().service(path[9:])
        if path == 'networkfilters':
            return self.network_filters_service()
        if path.startswith('networkfilters/'):
            return self.network_filters_service().service(path[15:])
        if path == 'networks':
            return self.networks_service()
        if path.startswith('networks/'):
            return self.networks_service().service(path[9:])
        if path == 'openstackimageproviders':
            return self.openstack_image_providers_service()
        if path.startswith('openstackimageproviders/'):
            return self.openstack_image_providers_service().service(path[24:])
        if path == 'openstacknetworkproviders':
            return self.openstack_network_providers_service()
        if path.startswith('openstacknetworkproviders/'):
            return self.openstack_network_providers_service().service(path[26:])
        if path == 'openstackvolumeproviders':
            return self.openstack_volume_providers_service()
        if path.startswith('openstackvolumeproviders/'):
            return self.openstack_volume_providers_service().service(path[25:])
        if path == 'operatingsystems':
            return self.operating_systems_service()
        if path.startswith('operatingsystems/'):
            return self.operating_systems_service().service(path[17:])
        if path == 'permissions':
            return self.permissions_service()
        if path.startswith('permissions/'):
            return self.permissions_service().service(path[12:])
        if path == 'roles':
            return self.roles_service()
        if path.startswith('roles/'):
            return self.roles_service().service(path[6:])
        if path == 'schedulingpolicies':
            return self.scheduling_policies_service()
        if path.startswith('schedulingpolicies/'):
            return self.scheduling_policies_service().service(path[19:])
        if path == 'schedulingpolicyunits':
            return self.scheduling_policy_units_service()
        if path.startswith('schedulingpolicyunits/'):
            return self.scheduling_policy_units_service().service(path[22:])
        if path == 'storageconnections':
            return self.storage_connections_service()
        if path.startswith('storageconnections/'):
            return self.storage_connections_service().service(path[19:])
        if path == 'storagedomains':
            return self.storage_domains_service()
        if path.startswith('storagedomains/'):
            return self.storage_domains_service().service(path[15:])
        if path == 'tags':
            return self.tags_service()
        if path.startswith('tags/'):
            return self.tags_service().service(path[5:])
        if path == 'templates':
            return self.templates_service()
        if path.startswith('templates/'):
            return self.templates_service().service(path[10:])
        if path == 'users':
            return self.users_service()
        if path.startswith('users/'):
            return self.users_service().service(path[6:])
        if path == 'vmpools':
            return self.vm_pools_service()
        if path.startswith('vmpools/'):
            return self.vm_pools_service().service(path[8:])
        if path == 'vms':
            return self.vms_service()
        if path.startswith('vms/'):
            return self.vms_service().service(path[4:])
        if path == 'vnicprofiles':
            return self.vnic_profiles_service()
        if path.startswith('vnicprofiles/'):
            return self.vnic_profiles_service().service(path[13:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'SystemService:%s' % self._path


class SystemPermissionsService(AssignedPermissionsService):
    """
    This service doesn't add any new methods, it is just a placeholder for the annotation that specifies the path of the
    resource that manages the permissions assigned to the system object.
    """

    def __init__(self, connection, path):
        super(SystemPermissionsService, self).__init__(connection, path)
        self._permission_service = None

    def add(
        self,
        permission,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.PermissionWriter.write_one(permission, writer, 'permission')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.PermissionReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.PermissionReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def permission_service(self, id):
        """
        Sub-resource locator method, returns individual permission resource on which the remainder of the URI is
        dispatched.
        """
        return PermissionService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.permission_service(path)
        return self.permission_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'SystemPermissionsService:%s' % self._path


class TagService(Service):
    """
    """

    def __init__(self, connection, path):
        super(TagService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.TagReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        tag,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.TagWriter.write_one(tag, writer, 'tag')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.TagReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'TagService:%s' % self._path


class TagsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(TagsService, self).__init__(connection, path)
        self._tag_service = None

    def add(
        self,
        tag,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.TagWriter.write_one(tag, writer, 'tag')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.TagReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of tags to return. If not specified all the tags are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.TagReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def tag_service(self, id):
        """
        """
        return TagService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.tag_service(path)
        return self.tag_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'TagsService:%s' % self._path


class TemplateService(Service):
    """
    """

    def __init__(self, connection, path):
        super(TemplateService, self).__init__(connection, path)
        self._cdroms_service = None
        self._disks_service = None
        self._graphics_consoles_service = None
        self._nics_service = None
        self._permissions_service = None
        self._tags_service = None
        self._watchdogs_service = None

    def export(
        self,
        exclussive=None,
        storage_domain=None,
    ):
        """
        Keyword arguments:
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if exclussive is not None:
            writer.write_boolean('exclussive', exclussive)
        if storage_domain is not None:
            writers.StorageDomainWriter.write_one(storage_domain, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'export'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def get(
        self,
        filter=None,
    ):
        """
        Keyword arguments:
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        query = {}
        if filter is not None:
            filter = Writer.render_boolean(filter)
            query['filter'] = filter
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.TemplateReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        template,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.TemplateWriter.write_one(template, writer, 'template')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.TemplateReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def cdroms_service(self):
        """
        """
        return TemplateCdromsService(self._connection, '%s/cdroms' % self._path)

    def disks_service(self):
        """
        """
        return TemplateDisksService(self._connection, '%s/disks' % self._path)

    def graphics_consoles_service(self):
        """
        """
        return GraphicsConsolesService(self._connection, '%s/graphicsconsoles' % self._path)

    def nics_service(self):
        """
        """
        return TemplateNicsService(self._connection, '%s/nics' % self._path)

    def permissions_service(self):
        """
        """
        return AssignedPermissionsService(self._connection, '%s/permissions' % self._path)

    def tags_service(self):
        """
        """
        return AssignedTagsService(self._connection, '%s/tags' % self._path)

    def watchdogs_service(self):
        """
        """
        return TemplateWatchdogsService(self._connection, '%s/watchdogs' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'cdroms':
            return self.cdroms_service()
        if path.startswith('cdroms/'):
            return self.cdroms_service().service(path[7:])
        if path == 'disks':
            return self.disks_service()
        if path.startswith('disks/'):
            return self.disks_service().service(path[6:])
        if path == 'graphicsconsoles':
            return self.graphics_consoles_service()
        if path.startswith('graphicsconsoles/'):
            return self.graphics_consoles_service().service(path[17:])
        if path == 'nics':
            return self.nics_service()
        if path.startswith('nics/'):
            return self.nics_service().service(path[5:])
        if path == 'permissions':
            return self.permissions_service()
        if path.startswith('permissions/'):
            return self.permissions_service().service(path[12:])
        if path == 'tags':
            return self.tags_service()
        if path.startswith('tags/'):
            return self.tags_service().service(path[5:])
        if path == 'watchdogs':
            return self.watchdogs_service()
        if path.startswith('watchdogs/'):
            return self.watchdogs_service().service(path[10:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'TemplateService:%s' % self._path


class TemplateCdromService(Service):
    """
    """

    def __init__(self, connection, path):
        super(TemplateCdromService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.CdromReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'TemplateCdromService:%s' % self._path


class TemplateCdromsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(TemplateCdromsService, self).__init__(connection, path)
        self._cdrom_service = None

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of CDROMs to return. If not specified all the CDROMs are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.CdromReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def cdrom_service(self, id):
        """
        """
        return TemplateCdromService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.cdrom_service(path)
        return self.cdrom_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'TemplateCdromsService:%s' % self._path


class TemplateDiskService(Service):
    """
    """

    def __init__(self, connection, path):
        super(TemplateDiskService, self).__init__(connection, path)

    def copy(
        self,
        async=None,
        filter=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the copy should be performed asynchronously.
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if filter is not None:
            writer.write_boolean('filter', filter)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'copy'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def export(
        self,
        async=None,
        filter=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the export should be performed asynchronously.
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if filter is not None:
            writer.write_boolean('filter', filter)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'export'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.DiskReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'TemplateDiskService:%s' % self._path


class TemplateDisksService(Service):
    """
    """

    def __init__(self, connection, path):
        super(TemplateDisksService, self).__init__(connection, path)
        self._disk_service = None

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of disks to return. If not specified all the disks are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.DiskReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def disk_service(self, id):
        """
        """
        return TemplateDiskService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.disk_service(path)
        return self.disk_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'TemplateDisksService:%s' % self._path


class TemplateNicService(Service):
    """
    """

    def __init__(self, connection, path):
        super(TemplateNicService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NicReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        nic,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.NicWriter.write_one(nic, writer, 'nic')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NicReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'TemplateNicService:%s' % self._path


class TemplateNicsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(TemplateNicsService, self).__init__(connection, path)
        self._nic_service = None

    def add(
        self,
        nic,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.NicWriter.write_one(nic, writer, 'nic')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NicReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of NICs to return. If not specified all the NICs are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NicReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def nic_service(self, id):
        """
        """
        return TemplateNicService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.nic_service(path)
        return self.nic_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'TemplateNicsService:%s' % self._path


class TemplateWatchdogService(Service):
    """
    """

    def __init__(self, connection, path):
        super(TemplateWatchdogService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.WatchdogReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        watchdog,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.WatchdogWriter.write_one(watchdog, writer, 'watchdog')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.WatchdogReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'TemplateWatchdogService:%s' % self._path


class TemplateWatchdogsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(TemplateWatchdogsService, self).__init__(connection, path)
        self._watchdog_service = None

    def add(
        self,
        watchdog,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.WatchdogWriter.write_one(watchdog, writer, 'watchdog')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.WatchdogReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of watchdogs to return. If not specified all the watchdogs are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.WatchdogReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def watchdog_service(self, id):
        """
        """
        return TemplateWatchdogService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.watchdog_service(path)
        return self.watchdog_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'TemplateWatchdogsService:%s' % self._path


class TemplatesService(Service):
    """
    """

    def __init__(self, connection, path):
        super(TemplatesService, self).__init__(connection, path)
        self._template_service = None

    def add(
        self,
        template,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.TemplateWriter.write_one(template, writer, 'template')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.TemplateReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        case_sensitive=None,
        filter=None,
        max=None,
        search=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of templates to return. If not specified all the templates are returned.
        search -- A query string used to restrict the returned templates.
        case_sensitive -- Indicates if the search performed using the `search` parameter should be performed taking case into
        account. The default value is `true`, which means that case is taken into account. If you want to search
        ignoring case set it to `false`.
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        query = {}
        if case_sensitive is not None:
            case_sensitive = Writer.render_boolean(case_sensitive)
            query['case_sensitive'] = case_sensitive
        if filter is not None:
            filter = Writer.render_boolean(filter)
            query['filter'] = filter
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        if search is not None:
            query['search'] = search
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.TemplateReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def template_service(self, id):
        """
        """
        return TemplateService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.template_service(path)
        return self.template_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'TemplatesService:%s' % self._path


class UnmanagedNetworkService(Service):
    """
    """

    def __init__(self, connection, path):
        super(UnmanagedNetworkService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.UnmanagedNetworkReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'UnmanagedNetworkService:%s' % self._path


class UnmanagedNetworksService(Service):
    """
    """

    def __init__(self, connection, path):
        super(UnmanagedNetworksService, self).__init__(connection, path)
        self._unmanaged_network_service = None

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of networks to return. If not specified all the networks are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.UnmanagedNetworkReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def unmanaged_network_service(self, id):
        """
        """
        return UnmanagedNetworkService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.unmanaged_network_service(path)
        return self.unmanaged_network_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'UnmanagedNetworksService:%s' % self._path


class UserService(Service):
    """
    """

    def __init__(self, connection, path):
        super(UserService, self).__init__(connection, path)
        self._permissions_service = None
        self._roles_service = None
        self._ssh_public_keys_service = None
        self._tags_service = None

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.UserReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def permissions_service(self):
        """
        """
        return AssignedPermissionsService(self._connection, '%s/permissions' % self._path)

    def roles_service(self):
        """
        """
        return AssignedRolesService(self._connection, '%s/roles' % self._path)

    def ssh_public_keys_service(self):
        """
        """
        return SshPublicKeysService(self._connection, '%s/sshpublickeys' % self._path)

    def tags_service(self):
        """
        """
        return AssignedTagsService(self._connection, '%s/tags' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'permissions':
            return self.permissions_service()
        if path.startswith('permissions/'):
            return self.permissions_service().service(path[12:])
        if path == 'roles':
            return self.roles_service()
        if path.startswith('roles/'):
            return self.roles_service().service(path[6:])
        if path == 'sshpublickeys':
            return self.ssh_public_keys_service()
        if path.startswith('sshpublickeys/'):
            return self.ssh_public_keys_service().service(path[14:])
        if path == 'tags':
            return self.tags_service()
        if path.startswith('tags/'):
            return self.tags_service().service(path[5:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'UserService:%s' % self._path


class UsersService(Service):
    """
    """

    def __init__(self, connection, path):
        super(UsersService, self).__init__(connection, path)
        self._user_service = None

    def add(
        self,
        user,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.UserWriter.write_one(user, writer, 'user')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.UserReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        case_sensitive=None,
        max=None,
        search=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of users to return. If not specified all the users are returned.
        search -- A query string used to restrict the returned users.
        case_sensitive -- Indicates if the search performed using the `search` parameter should be performed taking case into
        account. The default value is `true`, which means that case is taken into account. If you want to search
        ignoring case set it to `false`.
        """
        query = {}
        if case_sensitive is not None:
            case_sensitive = Writer.render_boolean(case_sensitive)
            query['case_sensitive'] = case_sensitive
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        if search is not None:
            query['search'] = search
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.UserReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def user_service(self, id):
        """
        """
        return UserService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.user_service(path)
        return self.user_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'UsersService:%s' % self._path


class VirtualFunctionAllowedNetworkService(Service):
    """
    """

    def __init__(self, connection, path):
        super(VirtualFunctionAllowedNetworkService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NetworkReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'VirtualFunctionAllowedNetworkService:%s' % self._path


class VirtualFunctionAllowedNetworksService(Service):
    """
    """

    def __init__(self, connection, path):
        super(VirtualFunctionAllowedNetworksService, self).__init__(connection, path)
        self._network_service = None

    def add(
        self,
        network,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.NetworkWriter.write_one(network, writer, 'network')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NetworkReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of networks to return. If not specified all the networks are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NetworkReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def network_service(self, id):
        """
        """
        return VirtualFunctionAllowedNetworkService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.network_service(path)
        return self.network_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'VirtualFunctionAllowedNetworksService:%s' % self._path


class VmService(MeasurableService):
    """
    """

    def __init__(self, connection, path):
        super(VmService, self).__init__(connection, path)
        self._affinity_labels_service = None
        self._applications_service = None
        self._cdroms_service = None
        self._disk_attachments_service = None
        self._disks_service = None
        self._graphics_consoles_service = None
        self._host_devices_service = None
        self._katello_errata_service = None
        self._nics_service = None
        self._numa_nodes_service = None
        self._permissions_service = None
        self._reported_devices_service = None
        self._sessions_service = None
        self._snapshots_service = None
        self._statistics_service = None
        self._tags_service = None
        self._watchdogs_service = None

    def cancel_migration(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the migration should cancelled asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'cancelmigration'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def clone(
        self,
        async=None,
        vm=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the clone should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if vm is not None:
            writers.VmWriter.write_one(vm, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'clone'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def commit_snapshot(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the snapshots should be committed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'commitsnapshot'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def detach(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the detach should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'detach'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def export(
        self,
        async=None,
        discard_snapshots=None,
        exclusive=None,
        storage_domain=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the export should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if discard_snapshots is not None:
            writer.write_boolean('discard_snapshots', discard_snapshots)
        if exclusive is not None:
            writer.write_boolean('exclusive', exclusive)
        if storage_domain is not None:
            writers.StorageDomainWriter.write_one(storage_domain, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'export'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def freeze_filesystems(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the freeze should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'freezefilesystems'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def get(
        self,
        filter=None,
        next_run=None,
    ):
        """
        Retrieves the description of the virtual machine.
        Note that some elements of the description of the virtual machine won't be returned unless the `All-Content`
        header is present in the request and has the value `true`. The elements that aren't currently returned are
        the following:
        - `console`
        - `initialization.configuration.data` - The OVF document describing the virtual machine.
        - `rng_source`
        - `soundcard`
        - `virtio_scsi`
        With the Python SDK the `All-Content` header can be set using the `all_content` parameter of the `get`
        method:
        [source,python]
        ----
        api.vms.get(name="myvm", all_content=True)
        ----
        Note that the reason for not including these elements is performance: they are seldom used and they require
        additional queries in the server. So try to use the `All-Content` header only when it is really needed.

        Keyword arguments:
        next_run -- Indicates if the returned result describes the virtual machine as it is currently running, or if describes
        it with the modifications that have already been performed but that will have effect only when it is
        restarted. By default the values is `false`.
        If the parameter is included in the request, but without a value, it is assumed that the value is `true`, so
        the following request:
        [source]
        ----
        GET /vms/{vm:id};next_run
        ----
        Is equivalent to using the value `true`:
        [source]
        ----
        GET /vms/{vm:id};next_run=true
        ----
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        query = {}
        if filter is not None:
            filter = Writer.render_boolean(filter)
            query['filter'] = filter
        if next_run is not None:
            next_run = Writer.render_boolean(next_run)
            query['next_run'] = next_run
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.VmReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def logon(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the logon should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'logon'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def maintenance(
        self,
        async=None,
        maintenance_enabled=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the action should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if maintenance_enabled is not None:
            writer.write_boolean('maintenance_enabled', maintenance_enabled)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'maintenance'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def migrate(
        self,
        async=None,
        cluster=None,
        force=None,
        host=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the migration should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if cluster is not None:
            writers.ClusterWriter.write_one(cluster, writer)
        if force is not None:
            writer.write_boolean('force', force)
        if host is not None:
            writers.HostWriter.write_one(host, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'migrate'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def preview_snapshot(
        self,
        async=None,
        disks=None,
        restore_memory=None,
        snapshot=None,
        vm=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the preview should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if disks is not None:
            writers.DiskWriter.write_many(disks, writer)
        if restore_memory is not None:
            writer.write_boolean('restore_memory', restore_memory)
        if snapshot is not None:
            writers.SnapshotWriter.write_one(snapshot, writer)
        if vm is not None:
            writers.VmWriter.write_one(vm, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'previewsnapshot'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def reboot(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the reboot should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'reboot'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def reorder_mac_addresses(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the action should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'reordermacaddresses'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def shutdown(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the shutdown should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'shutdown'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def start(
        self,
        async=None,
        filter=None,
        pause=None,
        use_cloud_init=None,
        use_sysprep=None,
        vm=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the action should be performed asynchronously.
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if filter is not None:
            writer.write_boolean('filter', filter)
        if pause is not None:
            writer.write_boolean('pause', pause)
        if use_cloud_init is not None:
            writer.write_boolean('use_cloud_init', use_cloud_init)
        if use_sysprep is not None:
            writer.write_boolean('use_sysprep', use_sysprep)
        if vm is not None:
            writers.VmWriter.write_one(vm, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'start'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def stop(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the action should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'stop'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def suspend(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the action should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'suspend'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def thaw_filesystems(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the action should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'thawfilesystems'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def ticket(
        self,
        async=None,
        ticket=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the generation of the ticket should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if ticket is not None:
            writers.TicketWriter.write_one(ticket, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'ticket'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            action = self._check_action(response)
            return action.ticket
        else:
            self._check_fault(response)

    def undo_snapshot(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the action should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'undosnapshot'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def update(
        self,
        vm,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.VmWriter.write_one(vm, writer, 'vm')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.VmReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def affinity_labels_service(self):
        """
        List of scheduling labels assigned to this VM.
        """
        return AssignedAffinityLabelsService(self._connection, '%s/affinitylabels' % self._path)

    def applications_service(self):
        """
        """
        return VmApplicationsService(self._connection, '%s/applications' % self._path)

    def cdroms_service(self):
        """
        """
        return VmCdromsService(self._connection, '%s/cdroms' % self._path)

    def disk_attachments_service(self):
        """
        List of disks attached to this virtual machine.
        """
        return DiskAttachmentsService(self._connection, '%s/diskattachments' % self._path)

    def disks_service(self):
        """
        """
        return VmDisksService(self._connection, '%s/disks' % self._path)

    def graphics_consoles_service(self):
        """
        """
        return GraphicsConsolesService(self._connection, '%s/graphicsconsoles' % self._path)

    def host_devices_service(self):
        """
        """
        return VmHostDevicesService(self._connection, '%s/hostdevices' % self._path)

    def katello_errata_service(self):
        """
        """
        return KatelloErrataService(self._connection, '%s/katelloerrata' % self._path)

    def nics_service(self):
        """
        """
        return VmNicsService(self._connection, '%s/nics' % self._path)

    def numa_nodes_service(self):
        """
        """
        return VmNumaNodesService(self._connection, '%s/numanodes' % self._path)

    def permissions_service(self):
        """
        """
        return AssignedPermissionsService(self._connection, '%s/permissions' % self._path)

    def reported_devices_service(self):
        """
        """
        return VmReportedDevicesService(self._connection, '%s/reporteddevices' % self._path)

    def sessions_service(self):
        """
        """
        return VmSessionsService(self._connection, '%s/sessions' % self._path)

    def snapshots_service(self):
        """
        """
        return SnapshotsService(self._connection, '%s/snapshots' % self._path)

    def statistics_service(self):
        """
        """
        return StatisticsService(self._connection, '%s/statistics' % self._path)

    def tags_service(self):
        """
        """
        return AssignedTagsService(self._connection, '%s/tags' % self._path)

    def watchdogs_service(self):
        """
        """
        return VmWatchdogsService(self._connection, '%s/watchdogs' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'affinitylabels':
            return self.affinity_labels_service()
        if path.startswith('affinitylabels/'):
            return self.affinity_labels_service().service(path[15:])
        if path == 'applications':
            return self.applications_service()
        if path.startswith('applications/'):
            return self.applications_service().service(path[13:])
        if path == 'cdroms':
            return self.cdroms_service()
        if path.startswith('cdroms/'):
            return self.cdroms_service().service(path[7:])
        if path == 'diskattachments':
            return self.disk_attachments_service()
        if path.startswith('diskattachments/'):
            return self.disk_attachments_service().service(path[16:])
        if path == 'disks':
            return self.disks_service()
        if path.startswith('disks/'):
            return self.disks_service().service(path[6:])
        if path == 'graphicsconsoles':
            return self.graphics_consoles_service()
        if path.startswith('graphicsconsoles/'):
            return self.graphics_consoles_service().service(path[17:])
        if path == 'hostdevices':
            return self.host_devices_service()
        if path.startswith('hostdevices/'):
            return self.host_devices_service().service(path[12:])
        if path == 'katelloerrata':
            return self.katello_errata_service()
        if path.startswith('katelloerrata/'):
            return self.katello_errata_service().service(path[14:])
        if path == 'nics':
            return self.nics_service()
        if path.startswith('nics/'):
            return self.nics_service().service(path[5:])
        if path == 'numanodes':
            return self.numa_nodes_service()
        if path.startswith('numanodes/'):
            return self.numa_nodes_service().service(path[10:])
        if path == 'permissions':
            return self.permissions_service()
        if path.startswith('permissions/'):
            return self.permissions_service().service(path[12:])
        if path == 'reporteddevices':
            return self.reported_devices_service()
        if path.startswith('reporteddevices/'):
            return self.reported_devices_service().service(path[16:])
        if path == 'sessions':
            return self.sessions_service()
        if path.startswith('sessions/'):
            return self.sessions_service().service(path[9:])
        if path == 'snapshots':
            return self.snapshots_service()
        if path.startswith('snapshots/'):
            return self.snapshots_service().service(path[10:])
        if path == 'statistics':
            return self.statistics_service()
        if path.startswith('statistics/'):
            return self.statistics_service().service(path[11:])
        if path == 'tags':
            return self.tags_service()
        if path.startswith('tags/'):
            return self.tags_service().service(path[5:])
        if path == 'watchdogs':
            return self.watchdogs_service()
        if path.startswith('watchdogs/'):
            return self.watchdogs_service().service(path[10:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'VmService:%s' % self._path


class VmApplicationService(Service):
    """
    """

    def __init__(self, connection, path):
        super(VmApplicationService, self).__init__(connection, path)

    def get(
        self,
        filter=None,
    ):
        """
        Keyword arguments:
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        query = {}
        if filter is not None:
            filter = Writer.render_boolean(filter)
            query['filter'] = filter
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.ApplicationReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'VmApplicationService:%s' % self._path


class VmApplicationsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(VmApplicationsService, self).__init__(connection, path)
        self._application_service = None

    def list(
        self,
        filter=None,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of applications to return. If not specified all the applications are returned.
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        query = {}
        if filter is not None:
            filter = Writer.render_boolean(filter)
            query['filter'] = filter
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.ApplicationReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def application_service(self, id):
        """
        """
        return VmApplicationService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.application_service(path)
        return self.application_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'VmApplicationsService:%s' % self._path


class VmCdromService(Service):
    """
    """

    def __init__(self, connection, path):
        super(VmCdromService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.CdromReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        cdorm,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.CdromWriter.write_one(cdorm, writer, 'cdorm')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.CdromReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'VmCdromService:%s' % self._path


class VmCdromsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(VmCdromsService, self).__init__(connection, path)
        self._cdrom_service = None

    def add(
        self,
        cdrom,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.CdromWriter.write_one(cdrom, writer, 'cdrom')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.CdromReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of CDROMs to return. If not specified all the CDROMs are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.CdromReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def cdrom_service(self, id):
        """
        """
        return VmCdromService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.cdrom_service(path)
        return self.cdrom_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'VmCdromsService:%s' % self._path


class VmDiskService(MeasurableService):
    """
    """

    def __init__(self, connection, path):
        super(VmDiskService, self).__init__(connection, path)
        self._permissions_service = None
        self._statistics_service = None

    def activate(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the activation should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'activate'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def deactivate(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the deactivation should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'deactivate'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def export(
        self,
        async=None,
        filter=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the export should be performed asynchronously.
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if filter is not None:
            writer.write_boolean('filter', filter)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'export'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.DiskReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def move(
        self,
        async=None,
        filter=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the move should be performed asynchronously.
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if filter is not None:
            writer.write_boolean('filter', filter)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'move'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Detach the disk from the virtual machine.
        NOTE: In version 3 of the API this used to also remove the disk completely from the system, but starting with
        version 4 it doesn't. If you need to remove it completely use the <<services/disk/methods/remove,remove
        method of the top level disk service>>.

        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        disk,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.DiskWriter.write_one(disk, writer, 'disk')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.DiskReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def permissions_service(self):
        """
        """
        return AssignedPermissionsService(self._connection, '%s/permissions' % self._path)

    def statistics_service(self):
        """
        """
        return StatisticsService(self._connection, '%s/statistics' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'permissions':
            return self.permissions_service()
        if path.startswith('permissions/'):
            return self.permissions_service().service(path[12:])
        if path == 'statistics':
            return self.statistics_service()
        if path.startswith('statistics/'):
            return self.statistics_service().service(path[11:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'VmDiskService:%s' % self._path


class VmDisksService(Service):
    """
    """

    def __init__(self, connection, path):
        super(VmDisksService, self).__init__(connection, path)
        self._disk_service = None

    def add(
        self,
        disk,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.DiskWriter.write_one(disk, writer, 'disk')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.DiskReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of disks to return. If not specified all the disks are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.DiskReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def disk_service(self, id):
        """
        """
        return VmDiskService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.disk_service(path)
        return self.disk_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'VmDisksService:%s' % self._path


class VmGraphicsConsoleService(GraphicsConsoleService):
    """
    """

    def __init__(self, connection, path):
        super(VmGraphicsConsoleService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.GraphicsConsoleReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def proxy_ticket(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the generation of the ticket should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'proxyticket'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            action = self._check_action(response)
            return action.proxy_ticket
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'VmGraphicsConsoleService:%s' % self._path


class VmHostDeviceService(Service):
    """
    """

    def __init__(self, connection, path):
        super(VmHostDeviceService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.HostDeviceReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'VmHostDeviceService:%s' % self._path


class VmHostDevicesService(Service):
    """
    """

    def __init__(self, connection, path):
        super(VmHostDevicesService, self).__init__(connection, path)
        self._device_service = None

    def add(
        self,
        device,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.HostDeviceWriter.write_one(device, writer, 'device')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.HostDeviceReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of devices to return. If not specified all the devices are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.HostDeviceReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def device_service(self, id):
        """
        """
        return VmHostDeviceService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.device_service(path)
        return self.device_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'VmHostDevicesService:%s' % self._path


class VmNicService(MeasurableService):
    """
    """

    def __init__(self, connection, path):
        super(VmNicService, self).__init__(connection, path)
        self._reported_devices_service = None
        self._statistics_service = None

    def activate(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the activation should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'activate'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def deactivate(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the deactivation should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'deactivate'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NicReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        nic,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.NicWriter.write_one(nic, writer, 'nic')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NicReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def reported_devices_service(self):
        """
        """
        return VmReportedDevicesService(self._connection, '%s/reporteddevices' % self._path)

    def statistics_service(self):
        """
        """
        return StatisticsService(self._connection, '%s/statistics' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'reporteddevices':
            return self.reported_devices_service()
        if path.startswith('reporteddevices/'):
            return self.reported_devices_service().service(path[16:])
        if path == 'statistics':
            return self.statistics_service()
        if path.startswith('statistics/'):
            return self.statistics_service().service(path[11:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'VmNicService:%s' % self._path


class VmNicsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(VmNicsService, self).__init__(connection, path)
        self._nic_service = None

    def add(
        self,
        nic,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.NicWriter.write_one(nic, writer, 'nic')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NicReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of NICs to return. If not specified all the NICs are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NicReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def nic_service(self, id):
        """
        """
        return VmNicService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.nic_service(path)
        return self.nic_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'VmNicsService:%s' % self._path


class VmNumaNodeService(Service):
    """
    """

    def __init__(self, connection, path):
        super(VmNumaNodeService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.VirtualNumaNodeReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        node,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.VirtualNumaNodeWriter.write_one(node, writer, 'node')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.VirtualNumaNodeReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'VmNumaNodeService:%s' % self._path


class VmNumaNodesService(Service):
    """
    """

    def __init__(self, connection, path):
        super(VmNumaNodesService, self).__init__(connection, path)
        self._node_service = None

    def add(
        self,
        node,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.VirtualNumaNodeWriter.write_one(node, writer, 'node')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.VirtualNumaNodeReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of nodes to return. If not specified all the nodes are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.VirtualNumaNodeReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def node_service(self, id):
        """
        """
        return VmNumaNodeService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.node_service(path)
        return self.node_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'VmNumaNodesService:%s' % self._path


class VmPoolService(Service):
    """
    """

    def __init__(self, connection, path):
        super(VmPoolService, self).__init__(connection, path)
        self._permissions_service = None

    def allocate_vm(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the allocation should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'allocatevm'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def get(
        self,
        filter=None,
    ):
        """
        Keyword arguments:
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        query = {}
        if filter is not None:
            filter = Writer.render_boolean(filter)
            query['filter'] = filter
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.VmPoolReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        pool,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.VmPoolWriter.write_one(pool, writer, 'pool')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.VmPoolReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def permissions_service(self):
        """
        """
        return AssignedPermissionsService(self._connection, '%s/permissions' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'permissions':
            return self.permissions_service()
        if path.startswith('permissions/'):
            return self.permissions_service().service(path[12:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'VmPoolService:%s' % self._path


class VmPoolsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(VmPoolsService, self).__init__(connection, path)
        self._pool_service = None

    def add(
        self,
        pool,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.VmPoolWriter.write_one(pool, writer, 'pool')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.VmPoolReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        case_sensitive=None,
        filter=None,
        max=None,
        search=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of pools to return. If this value is not specified, all of the pools are returned.
        search -- A query string used to restrict the returned pools.
        case_sensitive -- Indicates if the search performed using the `search` parameter should be performed taking case into
        account. The default value is `true`, which means that case is taken into account. If you want to search
        ignoring case set it to `false`.
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        query = {}
        if case_sensitive is not None:
            case_sensitive = Writer.render_boolean(case_sensitive)
            query['case_sensitive'] = case_sensitive
        if filter is not None:
            filter = Writer.render_boolean(filter)
            query['filter'] = filter
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        if search is not None:
            query['search'] = search
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.VmPoolReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def pool_service(self, id):
        """
        """
        return VmPoolService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.pool_service(path)
        return self.pool_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'VmPoolsService:%s' % self._path


class VmReportedDeviceService(Service):
    """
    """

    def __init__(self, connection, path):
        super(VmReportedDeviceService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.ReportedDeviceReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'VmReportedDeviceService:%s' % self._path


class VmReportedDevicesService(Service):
    """
    """

    def __init__(self, connection, path):
        super(VmReportedDevicesService, self).__init__(connection, path)
        self._reported_device_service = None

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of devices to return. If not specified all the devices are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.ReportedDeviceReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def reported_device_service(self, id):
        """
        """
        return VmReportedDeviceService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.reported_device_service(path)
        return self.reported_device_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'VmReportedDevicesService:%s' % self._path


class VmSessionService(Service):
    """
    """

    def __init__(self, connection, path):
        super(VmSessionService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.SessionReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'VmSessionService:%s' % self._path


class VmSessionsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(VmSessionsService, self).__init__(connection, path)
        self._session_service = None

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of sessions to return. If not specified all the sessions are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.SessionReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def session_service(self, id):
        """
        """
        return VmSessionService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.session_service(path)
        return self.session_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'VmSessionsService:%s' % self._path


class VmWatchdogService(Service):
    """
    """

    def __init__(self, connection, path):
        super(VmWatchdogService, self).__init__(connection, path)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.WatchdogReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        watchdog,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.WatchdogWriter.write_one(watchdog, writer, 'watchdog')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.WatchdogReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'VmWatchdogService:%s' % self._path


class VmWatchdogsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(VmWatchdogsService, self).__init__(connection, path)
        self._watchdog_service = None

    def add(
        self,
        watchdog,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.WatchdogWriter.write_one(watchdog, writer, 'watchdog')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.WatchdogReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of watchdogs to return. If not specified all the watchdogs are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.WatchdogReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def watchdog_service(self, id):
        """
        """
        return VmWatchdogService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.watchdog_service(path)
        return self.watchdog_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'VmWatchdogsService:%s' % self._path


class VmsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(VmsService, self).__init__(connection, path)
        self._vm_service = None

    def add(
        self,
        vm,
    ):
        """
        Creates a new virtual machine.
        The virtual machine can be created in different ways:
        - From a template. In this case the identifier or name of the template must be provided. For example, using a
          plain shell script and XML:
        [source,bash]
        ----
        #!/bin/sh -ex
        url="https://engine.example.com/ovirt-engine/api"
        user="admin@internal"
        password="..."
        curl \
        --verbose \
        --cacert /etc/pki/ovirt-engine/ca.pem \
        --user "${user}:${password}" \
        --request POST \
        --header "Content-Type: application/xml" \
        --header "Accept: application/xml" \
        --data '
        <vm>
          <name>myvm</name>
          <template>
            <name>Blank</name>
          </template>
          <cluster>
            <name>mycluster</name>
          </cluster>
        </vm>
        ' \
        "${url}/vms"
        ----
        - From a snapshot. In this case the identifier of the snapshot has to be provided. For example, using a plain
          shel script and XML:
        [source,bash]
        ----
        #!/bin/sh -ex
        url="https://engine.example.com/ovirt-engine/api"
        user="admin@internal"
        password="..."
        curl \
        --verbose \
        --cacert /etc/pki/ovirt-engine/ca.pem \
        --user "${user}:${password}" \
        --request POST \
        --header "Content-Type: application/xml" \
        --header "Accept: application/xml" \
        --data '
        <vm>
          <name>myvm</name>
          <snapshots>
            <snapshot id="266742a5-6a65-483c-816d-d2ce49746680"/>
          </snapshots>
          <cluster>
            <name>mycluster</name>
          </cluster>
        </vm>
        ' \
        "${url}/vms"
        ----
        When creating a virtual machine from a template or from a snapshot it is usually useful to explicitly indicate
        in what storage domain to create the disks for the virtual machine. If the virtual machine is created from
        a template then this is achieved passing a set of `disk` elements that indicate the mapping:
        [source,xml]
        ----
        <vm>
          ...
          <disks>
            <disk id="8d4bd566-6c86-4592-a4a7-912dbf93c298">
              <storage_domains>
                <storage_domain id="9cb6cb0a-cf1d-41c2-92ca-5a6d665649c9"/>
              </storage_domains>
            </disk>
          </disks>
        </vm>
        ----
        When the virtual machine is created from a snapshot this set of disks is sligthly different, it uses the
        `imageId` attribute instead of `id`.
        [source,xml]
        ----
        <vm>
          ...
          <disks>
            <disk>
              <image_id>8d4bd566-6c86-4592-a4a7-912dbf93c298</image_id>
              <storage_domains>
                <storage_domain id="9cb6cb0a-cf1d-41c2-92ca-5a6d665649c9"/>
              </storage_domains>
            </disk>
          </disks>
        </vm>
        ----
        In all cases the name or identifier of the cluster where the virtual machine will be created is mandatory.
        This is an example of how creating a virtual machine from a snapshot with the disks in a different storage
        domain can be done with the Python SDK:
        [source,python]
        ----
        # Find the VM:
        vm = api.vms.get(name="myvm")
        # Find the snapshot:
        snapshot = None
        for current in vm.snapshots.list():
          if current.get_description() == 'mysnap':
            snapshot = current
            break
        # Find the identifiers of the disks of the snapshot, as we need them in
        # order to explicitly indicate that we want them created in a different storage
        # domain:
        disk_ids = []
        for current in snapshot.disks.list():
          disk_ids.append(current.get_id())
        # Find the storage domain where the disks should be created:
        sd = api.storagedomains.get(name="yourdata")
        # Prepare the list of disks for the operation to create the snapshot,
        # explicitly indicating for each of them the storage domain where it should be
        # created:
        disk_list = []
        for disk_id in disk_ids:
          disk = params.Disk(
            image_id=disk_id,
            storage_domains=params.StorageDomains(
              storage_domain=[
                params.StorageDomain(
                  id=sd.get_id(),
                ),
              ],
            ),
          )
          disk_list.append(disk)
        # Create the VM from the snapshot:
        api.vms.add(
          params.VM(
            name="myclone",
            cluster=params.Cluster(name="mycluster"),
            snapshots=params.Snapshots(
              snapshot=[
                params.Snapshot(
                  id=snapshot.get_id(),
                ),
              ],
            ),
            disks=params.Disks(
              disk=disk_list,
            ),
          )
        )
        ----

        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.VmWriter.write_one(vm, writer, 'vm')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.VmReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        case_sensitive=None,
        filter=None,
        max=None,
        search=None,
    ):
        """
        Keyword arguments:
        search -- A query string used to restrict the returned virtual machines.
        max -- The maximum number of results to return.
        case_sensitive -- Indicates if the search performed using the `search` parameter should be performed taking case into
        account. The default value is `true`, which means that case is taken into account. If you want to search
        ignoring case set it to `false`.
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        query = {}
        if case_sensitive is not None:
            case_sensitive = Writer.render_boolean(case_sensitive)
            query['case_sensitive'] = case_sensitive
        if filter is not None:
            filter = Writer.render_boolean(filter)
            query['filter'] = filter
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        if search is not None:
            query['search'] = search
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.VmReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def vm_service(self, id):
        """
        """
        return VmService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.vm_service(path)
        return self.vm_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'VmsService:%s' % self._path


class VnicProfileService(Service):
    """
    Since 4.0 it is possible to have a customized network filter to each VNIC profile.
    Please note that there is a default network filter to each VNIC profile.
    For more details of how the default network filter is calculated please refer to
    the documentation in <<services/network-filters, NetworkFilters>>.
    The basic POST command of adding a new VNIC profile is as follows:
    [source]
    ----
    http://{engine_ip_address}:8080/ovirt-engine/api/networks/{network_id}/vnicprofiles
    ----
    The output of creating a new VNIC profile depends in the  body  arguments that were given.
    In case no network filter was given, the default network filter will be configured. For example:
    [source,xml]
    ----
    <vnic_profile>
      <name>use_default_network_filter</name>
      <network id="00000000-0000-0000-0000-000000000009"/>
    </vnic_profile>
    ----
    In case an empty network filter was given, no network filter will be configured for the specific VNIC profile
    regardless of the VNIC profile's default network filter. For example:
    [source,xml]
    ----
    <vnic_profile>
      <name>no_network_filter</name>
      <network id="00000000-0000-0000-0000-000000000009"/>
      <network_filter/>
    </vnic_profile>
    ----
    In case that a specific valid network filter id was given, the VNIC profile will be configured with the given
    network filter regardless of the VNIC profiles's default network filter. For example:
    [source,xml]
    ----
    <vnic_profile>
      <name>user_choice_network_filter</name>
      <network id="00000000-0000-0000-0000-000000000009"/>
      <network_filter id= "0000001b-001b-001b-001b-0000000001d5"/>
    </vnic_profile>
    ----
    """

    def __init__(self, connection, path):
        super(VnicProfileService, self).__init__(connection, path)
        self._permissions_service = None

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.VnicProfileReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def update(
        self,
        profile,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.VnicProfileWriter.write_one(profile, writer, 'profile')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.VnicProfileReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def permissions_service(self):
        """
        """
        return AssignedPermissionsService(self._connection, '%s/permissions' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'permissions':
            return self.permissions_service()
        if path.startswith('permissions/'):
            return self.permissions_service().service(path[12:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'VnicProfileService:%s' % self._path


class VnicProfilesService(Service):
    """
    """

    def __init__(self, connection, path):
        super(VnicProfilesService, self).__init__(connection, path)
        self._profile_service = None

    def add(
        self,
        profile,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.VnicProfileWriter.write_one(profile, writer, 'profile')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.VnicProfileReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of profiles to return. If not specified all the profiles are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.VnicProfileReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def profile_service(self, id):
        """
        """
        return VnicProfileService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.profile_service(path)
        return self.profile_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'VnicProfilesService:%s' % self._path


class WeightService(Service):
    """
    """

    def __init__(self, connection, path):
        super(WeightService, self).__init__(connection, path)

    def get(
        self,
        filter=None,
    ):
        """
        Keyword arguments:
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        query = {}
        if filter is not None:
            filter = Writer.render_boolean(filter)
            query['filter'] = filter
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.WeightReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'WeightService:%s' % self._path


class WeightsService(Service):
    """
    """

    def __init__(self, connection, path):
        super(WeightsService, self).__init__(connection, path)
        self._weight_service = None

    def add(
        self,
        weight,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='POST', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.WeightWriter.write_one(weight, writer, 'weight')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [201, 202]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.WeightReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def list(
        self,
        filter=None,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of weights to return. If not specified all the weights are returned.
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        query = {}
        if filter is not None:
            filter = Writer.render_boolean(filter)
            query['filter'] = filter
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.WeightReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def weight_service(self, id):
        """
        """
        return WeightService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.weight_service(path)
        return self.weight_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'WeightsService:%s' % self._path


class DiskService(MeasurableService):
    """
    """

    def __init__(self, connection, path):
        super(DiskService, self).__init__(connection, path)
        self._permissions_service = None
        self._statistics_service = None

    def copy(
        self,
        async=None,
        disk=None,
        filter=None,
        storage_domain=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the copy should be performed asynchronously.
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if disk is not None:
            writers.DiskWriter.write_one(disk, writer)
        if filter is not None:
            writer.write_boolean('filter', filter)
        if storage_domain is not None:
            writers.StorageDomainWriter.write_one(storage_domain, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'copy'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def export(
        self,
        async=None,
        filter=None,
        storage_domain=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the export should be performed asynchronously.
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if filter is not None:
            writer.write_boolean('filter', filter)
        if storage_domain is not None:
            writers.StorageDomainWriter.write_one(storage_domain, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'export'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.DiskReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def move(
        self,
        async=None,
        filter=None,
        storage_domain=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the move should be performed asynchronously.
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if filter is not None:
            writer.write_boolean('filter', filter)
        if storage_domain is not None:
            writers.StorageDomainWriter.write_one(storage_domain, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'move'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def permissions_service(self):
        """
        """
        return AssignedPermissionsService(self._connection, '%s/permissions' % self._path)

    def statistics_service(self):
        """
        """
        return StatisticsService(self._connection, '%s/statistics' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'permissions':
            return self.permissions_service()
        if path.startswith('permissions/'):
            return self.permissions_service().service(path[12:])
        if path == 'statistics':
            return self.statistics_service()
        if path.startswith('statistics/'):
            return self.statistics_service().service(path[11:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'DiskService:%s' % self._path


class EngineKatelloErrataService(KatelloErrataService):
    """
    This service doesn't add any new methods, it is just a placeholder for the annotation that specifies the path of the
    resource that manages the Katello errata assigned to the engine.
    """

    def __init__(self, connection, path):
        super(EngineKatelloErrataService, self).__init__(connection, path)
        self._katello_erratum_service = None

    def list(
        self,
        max=None,
    ):
        """
        Keyword arguments:
        max -- Sets the maximum number of errata to return. If not specified all the errata are returned.
        """
        query = {}
        if max is not None:
            max = Writer.render_integer(max)
            query['max'] = max
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.KatelloErratumReader.read_many(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def katello_erratum_service(self, id):
        """
        """
        return KatelloErratumService(self._connection, '%s/%s' % (self._path, id))

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        index = path.find('/')
        if index == -1:
            return self.katello_erratum_service(path)
        return self.katello_erratum_service(path[:index]).service(path[index + 1:])

    def __str__(self):
        return 'EngineKatelloErrataService:%s' % self._path


class ExternalHostProviderService(ExternalProviderService):
    """
    """

    def __init__(self, connection, path):
        super(ExternalHostProviderService, self).__init__(connection, path)
        self._certificates_service = None
        self._compute_resources_service = None
        self._discovered_hosts_service = None
        self._host_groups_service = None
        self._hosts_service = None

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.ExternalHostProviderReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def import_certificates(
        self,
        certificates=None,
    ):
        """
        Keyword arguments:
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if certificates is not None:
            writers.CertificateWriter.write_many(certificates, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'importcertificates'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def test_connectivity(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the test should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'testconnectivity'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def update(
        self,
        provider,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.ExternalHostProviderWriter.write_one(provider, writer, 'provider')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.ExternalHostProviderReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def certificates_service(self):
        """
        """
        return ExternalProviderCertificatesService(self._connection, '%s/certificates' % self._path)

    def compute_resources_service(self):
        """
        """
        return ExternalComputeResourcesService(self._connection, '%s/computeresources' % self._path)

    def discovered_hosts_service(self):
        """
        """
        return ExternalDiscoveredHostsService(self._connection, '%s/discoveredhosts' % self._path)

    def host_groups_service(self):
        """
        """
        return ExternalHostGroupsService(self._connection, '%s/hostgroups' % self._path)

    def hosts_service(self):
        """
        """
        return ExternalHostsService(self._connection, '%s/hosts' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'certificates':
            return self.certificates_service()
        if path.startswith('certificates/'):
            return self.certificates_service().service(path[13:])
        if path == 'computeresources':
            return self.compute_resources_service()
        if path.startswith('computeresources/'):
            return self.compute_resources_service().service(path[17:])
        if path == 'discoveredhosts':
            return self.discovered_hosts_service()
        if path.startswith('discoveredhosts/'):
            return self.discovered_hosts_service().service(path[16:])
        if path == 'hostgroups':
            return self.host_groups_service()
        if path.startswith('hostgroups/'):
            return self.host_groups_service().service(path[11:])
        if path == 'hosts':
            return self.hosts_service()
        if path.startswith('hosts/'):
            return self.hosts_service().service(path[6:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'ExternalHostProviderService:%s' % self._path


class GlusterBrickService(MeasurableService):
    """
    """

    def __init__(self, connection, path):
        super(GlusterBrickService, self).__init__(connection, path)
        self._statistics_service = None

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.GlusterBrickReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Removes this brick from the volume and deletes it from the database.

        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def replace(
        self,
        async=None,
        force=None,
    ):
        """
        Replaces this brick with a new one. The property `brick` is required.

        Keyword arguments:
        async -- Indicates if the replacement should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if force is not None:
            writer.write_boolean('force', force)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'replace'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def statistics_service(self):
        """
        """
        return StatisticsService(self._connection, '%s/statistics' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'statistics':
            return self.statistics_service()
        if path.startswith('statistics/'):
            return self.statistics_service().service(path[11:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'GlusterBrickService:%s' % self._path


class GlusterVolumeService(MeasurableService):
    """
    """

    def __init__(self, connection, path):
        super(GlusterVolumeService, self).__init__(connection, path)
        self._gluster_bricks_service = None
        self._statistics_service = None

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.GlusterVolumeReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def get_profile_statistics(
        self,
    ):
        """
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'getprofilestatistics'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            action = self._check_action(response)
            return action.details
        else:
            self._check_fault(response)

    def rebalance(
        self,
        async=None,
        fix_layout=None,
        force=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the rebalance should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if fix_layout is not None:
            writer.write_boolean('fix_layout', fix_layout)
        if force is not None:
            writer.write_boolean('force', force)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'rebalance'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def reset_all_options(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the reset should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'resetalloptions'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def reset_option(
        self,
        async=None,
        force=None,
        option=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the reset should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if force is not None:
            writer.write_boolean('force', force)
        if option is not None:
            writers.OptionWriter.write_one(option, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'resetoption'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def set_option(
        self,
        async=None,
        option=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the action should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if option is not None:
            writers.OptionWriter.write_one(option, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'setoption'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def start(
        self,
        async=None,
        force=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the action should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if force is not None:
            writer.write_boolean('force', force)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'start'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def start_profile(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the action should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'startprofile'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def stop(
        self,
        async=None,
        force=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the action should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if force is not None:
            writer.write_boolean('force', force)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'stop'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def stop_profile(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the action should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'stopprofile'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def stop_rebalance(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the action should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'stoprebalance'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def gluster_bricks_service(self):
        """
        """
        return GlusterBricksService(self._connection, '%s/glusterbricks' % self._path)

    def statistics_service(self):
        """
        """
        return StatisticsService(self._connection, '%s/statistics' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'glusterbricks':
            return self.gluster_bricks_service()
        if path.startswith('glusterbricks/'):
            return self.gluster_bricks_service().service(path[14:])
        if path == 'statistics':
            return self.statistics_service()
        if path.startswith('statistics/'):
            return self.statistics_service().service(path[11:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'GlusterVolumeService:%s' % self._path


class HostService(MeasurableService):
    """
    """

    def __init__(self, connection, path):
        super(HostService, self).__init__(connection, path)
        self._affinity_labels_service = None
        self._devices_service = None
        self._fence_agents_service = None
        self._hooks_service = None
        self._katello_errata_service = None
        self._network_attachments_service = None
        self._nics_service = None
        self._numa_nodes_service = None
        self._permissions_service = None
        self._statistics_service = None
        self._storage_service = None
        self._storage_connection_extensions_service = None
        self._tags_service = None
        self._unmanaged_networks_service = None

    def activate(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the activation should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'activate'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def approve(
        self,
        async=None,
        cluster=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the approval should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if cluster is not None:
            writers.ClusterWriter.write_one(cluster, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'approve'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def commit_net_config(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the action should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'commitnetconfig'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def deactivate(
        self,
        async=None,
        reason=None,
        stop_gluster_service=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the deactivation should be performed asynchronously.
        stop_gluster_service -- Indicates if the gluster service should be stopped as part of deactivating the host. It can be used while
        performing maintenance operations on the gluster host. Default value for this variable is `false`.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if reason is not None:
            writer.write_string('reason', reason)
        if stop_gluster_service is not None:
            writer.write_boolean('stop_gluster_service', stop_gluster_service)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'deactivate'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def enroll_certificate(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the enrollment should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'enrollcertificate'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def fence(
        self,
        async=None,
        fence_type=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the fencing should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if fence_type is not None:
            writer.write_string('fence_type', fence_type)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'fence'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            action = self._check_action(response)
            return action.power_management
        else:
            self._check_fault(response)

    def force_select_spm(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the action should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'forceselectspm'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def get(
        self,
        filter=None,
    ):
        """
        Keyword arguments:
        filter -- Indicates if the results should be filtered according to the permissions of the user.
        """
        query = {}
        if filter is not None:
            filter = Writer.render_boolean(filter)
            query['filter'] = filter
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.HostReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def install(
        self,
        async=None,
        deploy_hosted_engine=None,
        host=None,
        image=None,
        root_password=None,
        ssh=None,
        undeploy_hosted_engine=None,
    ):
        """
        Keyword arguments:
        root_password -- The password of of the `root` user, used to connect to the host via SSH.
        ssh -- The SSH details used to connect to the host.
        host -- This `override_iptables` property is used to indicate if the firewall configuration should be
        replaced by the default one.
        image -- When installing an oVirt node a image ISO file is needed.
        async -- Indicates if the installation should be performed asynchronously.
        deploy_hosted_engine -- When set to `true` it means this host should deploy also hosted
        engine components. Missing value is treated as `true` i.e deploy.
        Omitting this parameter means `false` and will perform no operation
        in hosted engine area.
        undeploy_hosted_engine -- When set to `true` it means this host should un-deploy hosted engine
        components and this host will not function as part of the High
        Availability cluster. Missing value is treated as `true` i.e un-deploy
        Omitting this parameter means `false` and will perform no operation
        in hosted engine area.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if deploy_hosted_engine is not None:
            writer.write_boolean('deploy_hosted_engine', deploy_hosted_engine)
        if host is not None:
            writers.HostWriter.write_one(host, writer)
        if image is not None:
            writer.write_string('image', image)
        if root_password is not None:
            writer.write_string('root_password', root_password)
        if ssh is not None:
            writers.SshWriter.write_one(ssh, writer)
        if undeploy_hosted_engine is not None:
            writer.write_boolean('undeploy_hosted_engine', undeploy_hosted_engine)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'install'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def iscsi_discover(
        self,
        async=None,
        iscsi=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the discovery should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if iscsi is not None:
            writers.IscsiDetailsWriter.write_one(iscsi, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'iscsidiscover'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            action = self._check_action(response)
            return action.iscsi_targets
        else:
            self._check_fault(response)

    def iscsi_login(
        self,
        async=None,
        iscsi=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the login should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if iscsi is not None:
            writers.IscsiDetailsWriter.write_one(iscsi, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'iscsilogin'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def refresh(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the refresh should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'refresh'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def remove(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the remove should be performed asynchronously.
        """
        query = {}
        if async is not None:
            async = Writer.render_boolean(async)
            query['async'] = async
        request = http.Request(method='DELETE', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code not in [200]:
            self._check_fault(response)

    def setup_networks(
        self,
        async=None,
        check_connectivity=None,
        connectivity_timeout=None,
        modified_bonds=None,
        modified_labels=None,
        modified_network_attachments=None,
        removed_bonds=None,
        removed_labels=None,
        removed_network_attachments=None,
        synchronized_network_attachments=None,
    ):
        """
        This method is used to change the configuration of the network interfaces of a host.
        For example, lets assume that you have a host with three network interfaces `eth0`, `eth1` and `eth2` and that
        you want to configure a new bond using `eth0` and `eth1`, and put a VLAN on top of it. Using a simple shell
        script and the `curl` command line HTTP client that can be done as follows:
        [source]
        ----
        #!/bin/sh -ex
        url="https://engine.example.com/ovirt-engine/api"
        user="admin@internal"
        password="..."
        curl \
        --verbose \
        --cacert /etc/pki/ovirt-engine/ca.pem \
        --user "${user}:${password}" \
        --request POST \
        --header "Content-Type: application/xml" \
        --header "Accept: application/xml" \
        --data '
        <action>
          <modified_bonds>
            <host_nic>
              <name>bond0</name>
              <bonding>
                <options>
                  <option>
                    <name>mode</name>
                    <value>4</value>
                  </option>
                  <option>
                    <name>miimon</name>
                    <value>100</value>
                  </option>
                </options>
                <slaves>
                  <host_nic>
                    <name>eth1</name>
                  </host_nic>
                  <host_nic>
                    <name>eth2</name>
                  </host_nic>
                </slaves>
              </bonding>
            </host_nic>
          </modified_bonds>
          <modified_network_attachments>
            <network_attachment>
              <network>
                <name>myvlan</name>
              </network>
              <host_nic>
                <name>bond0</name>
              </host_nic>
              <ip_address_assignments>
                <assignment_method>static</assignment_method>
                <ip_address_assignment>
                  <ip>
                    <address>192.168.122.10</address>
                    <netmask>255.255.255.0</netmask>
                  </ip>
                </ip_address_assignment>
              </ip_address_assignments>
            </network_attachment>
          </modified_network_attachments>
         </action>
        ' \
        "${url}/hosts/1ff7a191-2f3b-4eff-812b-9f91a30c3acc/setupnetworks"
        ----
        Note that this is valid for version 4 of the API. In previous versions some elements were represented as XML
        attributes instead of XML elements. In particular the `options` and `ip` elements were represented as follows:
        [source,xml]
        ----
        <options name="mode" value="4"/>
        <options name="miimon" value="100"/>
        <ip address="192.168.122.10" netmask="255.255.255.0"/>
        ----
        Using the Python SDK the same can be done with the following code:
        [source,python]
        ----
        host.setupnetworks(
          params.Action(
            modified_bonds=params.HostNics(
              host_nic=[
                params.HostNIC(
                  name="bond0",
                  bonding=params.Bonding(
                    options=params.Options(
                      option=[
                        params.Option(name="mode", value="4"),
                        params.Option(name="miimon", value="100"),
                      ],
                    ),
                    slaves=params.Slaves(
                      host_nic=[
                        params.HostNIC(name="eth1"),
                        params.HostNIC(name="eth2"),
                      ],
                    ),
                  ),
                ),
              ],
            ),
            modified_network_attachments=params.NetworkAttachments(
              network_attachment=[
                params.NetworkAttachment(
                  network=params.Network(name="myvlan"),
                  host_nic=params.HostNIC(name="bond0"),
                  ip_address_assignments=params.IpAddressAssignments(
                    ip_address_assignment=[
                      params.IpAddressAssignment(
                        assignment_method="static",
                        ip=params.IP(
                          address="192.168.122.10",
                          netmask="255.255.255.0",
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        )
        ----

        Keyword arguments:
        async -- Indicates if the action should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if check_connectivity is not None:
            writer.write_boolean('check_connectivity', check_connectivity)
        if connectivity_timeout is not None:
            writer.write_integer('connectivity_timeout', connectivity_timeout)
        if modified_bonds is not None:
            writers.HostNicWriter.write_many(modified_bonds, writer)
        if modified_labels is not None:
            writers.NetworkLabelWriter.write_many(modified_labels, writer)
        if modified_network_attachments is not None:
            writers.NetworkAttachmentWriter.write_many(modified_network_attachments, writer)
        if removed_bonds is not None:
            writers.HostNicWriter.write_many(removed_bonds, writer)
        if removed_labels is not None:
            writers.NetworkLabelWriter.write_many(removed_labels, writer)
        if removed_network_attachments is not None:
            writers.NetworkAttachmentWriter.write_many(removed_network_attachments, writer)
        if synchronized_network_attachments is not None:
            writers.NetworkAttachmentWriter.write_many(synchronized_network_attachments, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'setupnetworks'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def unregistered_storage_domains_discover(
        self,
        async=None,
        iscsi=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the discovery should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if iscsi is not None:
            writers.IscsiDetailsWriter.write_one(iscsi, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'unregisteredstoragedomainsdiscover'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            action = self._check_action(response)
            return action.storage_domains
        else:
            self._check_fault(response)

    def update(
        self,
        host,
    ):
        """
        Keyword arguments:
        """
        request = http.Request(method='PUT', path=self._path)
        buf = None
        writer = None
        try:
            buf = io.BytesIO()
            writer = xml.XmlWriter(buf, indent=True)
            writers.HostWriter.write_one(host, writer, 'host')
            writer.flush()
            request.body = buf.getvalue()
        finally:
            if writer is not None:
                writer.close()
            if buf is not None:
                buf.close()
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.HostReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def upgrade(
        self,
        async=None,
    ):
        """
        Keyword arguments:
        async -- Indicates if the upgrade should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'upgrade'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def affinity_labels_service(self):
        """
        List of scheduling labels assigned to this host.
        """
        return AssignedAffinityLabelsService(self._connection, '%s/affinitylabels' % self._path)

    def devices_service(self):
        """
        """
        return HostDevicesService(self._connection, '%s/devices' % self._path)

    def fence_agents_service(self):
        """
        """
        return FenceAgentsService(self._connection, '%s/fenceagents' % self._path)

    def hooks_service(self):
        """
        """
        return HostHooksService(self._connection, '%s/hooks' % self._path)

    def katello_errata_service(self):
        """
        """
        return KatelloErrataService(self._connection, '%s/katelloerrata' % self._path)

    def network_attachments_service(self):
        """
        """
        return NetworkAttachmentsService(self._connection, '%s/networkattachments' % self._path)

    def nics_service(self):
        """
        """
        return HostNicsService(self._connection, '%s/nics' % self._path)

    def numa_nodes_service(self):
        """
        """
        return HostNumaNodesService(self._connection, '%s/numanodes' % self._path)

    def permissions_service(self):
        """
        """
        return AssignedPermissionsService(self._connection, '%s/permissions' % self._path)

    def statistics_service(self):
        """
        """
        return StatisticsService(self._connection, '%s/statistics' % self._path)

    def storage_service(self):
        """
        """
        return HostStorageService(self._connection, '%s/storage' % self._path)

    def storage_connection_extensions_service(self):
        """
        """
        return StorageServerConnectionExtensionsService(self._connection, '%s/storageconnectionextensions' % self._path)

    def tags_service(self):
        """
        """
        return AssignedTagsService(self._connection, '%s/tags' % self._path)

    def unmanaged_networks_service(self):
        """
        """
        return UnmanagedNetworksService(self._connection, '%s/unmanagednetworks' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'affinitylabels':
            return self.affinity_labels_service()
        if path.startswith('affinitylabels/'):
            return self.affinity_labels_service().service(path[15:])
        if path == 'devices':
            return self.devices_service()
        if path.startswith('devices/'):
            return self.devices_service().service(path[8:])
        if path == 'fenceagents':
            return self.fence_agents_service()
        if path.startswith('fenceagents/'):
            return self.fence_agents_service().service(path[12:])
        if path == 'hooks':
            return self.hooks_service()
        if path.startswith('hooks/'):
            return self.hooks_service().service(path[6:])
        if path == 'katelloerrata':
            return self.katello_errata_service()
        if path.startswith('katelloerrata/'):
            return self.katello_errata_service().service(path[14:])
        if path == 'networkattachments':
            return self.network_attachments_service()
        if path.startswith('networkattachments/'):
            return self.network_attachments_service().service(path[19:])
        if path == 'nics':
            return self.nics_service()
        if path.startswith('nics/'):
            return self.nics_service().service(path[5:])
        if path == 'numanodes':
            return self.numa_nodes_service()
        if path.startswith('numanodes/'):
            return self.numa_nodes_service().service(path[10:])
        if path == 'permissions':
            return self.permissions_service()
        if path.startswith('permissions/'):
            return self.permissions_service().service(path[12:])
        if path == 'statistics':
            return self.statistics_service()
        if path.startswith('statistics/'):
            return self.statistics_service().service(path[11:])
        if path == 'storage':
            return self.storage_service()
        if path.startswith('storage/'):
            return self.storage_service().service(path[8:])
        if path == 'storageconnectionextensions':
            return self.storage_connection_extensions_service()
        if path.startswith('storageconnectionextensions/'):
            return self.storage_connection_extensions_service().service(path[28:])
        if path == 'tags':
            return self.tags_service()
        if path.startswith('tags/'):
            return self.tags_service().service(path[5:])
        if path == 'unmanagednetworks':
            return self.unmanaged_networks_service()
        if path.startswith('unmanagednetworks/'):
            return self.unmanaged_networks_service().service(path[18:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'HostService:%s' % self._path


class HostNicService(MeasurableService):
    """
    """

    def __init__(self, connection, path):
        super(HostNicService, self).__init__(connection, path)
        self._network_attachments_service = None
        self._network_labels_service = None
        self._statistics_service = None
        self._virtual_function_allowed_labels_service = None
        self._virtual_function_allowed_networks_service = None

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.HostNicReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def update_virtual_functions_configuration(
        self,
        async=None,
        virtual_functions_configuration=None,
    ):
        """
        The action updates virtual function configuration in case the current resource represents an SR-IOV enabled NIC.
        The input should be consisted of at least one of the following properties:
        - `allNetworksAllowed`
        - `numberOfVirtualFunctions`
        Please see the `HostNicVirtualFunctionsConfiguration` type for the meaning of the properties.

        Keyword arguments:
        async -- Indicates if the update should be performed asynchronously.
        """
        buf = io.BytesIO()
        writer = xml.XmlWriter(buf, indent=True)
        writer.write_start('action')
        if async is not None:
            writer.write_boolean('async', async)
        if virtual_functions_configuration is not None:
            writers.HostNicVirtualFunctionsConfigurationWriter.write_one(virtual_functions_configuration, writer)
        writer.write_end()
        writer.flush()
        body = buf.getvalue()
        writer.close()
        buf.close()
        request = http.Request(
            method='POST',
            path='%s/%s' % (self._path, 'updatevirtualfunctionsconfiguration'),
            body=body,
        )
        response = self._connection.send(request)
        if response.code in [200]:
            self._check_action(response)
        else:
            self._check_fault(response)

    def network_attachments_service(self):
        """
        """
        return NetworkAttachmentsService(self._connection, '%s/networkattachments' % self._path)

    def network_labels_service(self):
        """
        """
        return NetworkLabelsService(self._connection, '%s/networklabels' % self._path)

    def statistics_service(self):
        """
        """
        return StatisticsService(self._connection, '%s/statistics' % self._path)

    def virtual_function_allowed_labels_service(self):
        """
        Retrieves sub-collection resource of network labels that are allowed on an the virtual functions
        in case that the current resource represents an SR-IOV physical function NIC.
        """
        return NetworkLabelsService(self._connection, '%s/virtualfunctionallowedlabels' % self._path)

    def virtual_function_allowed_networks_service(self):
        """
        Retrieves sub-collection resource of networks that are allowed on an the virtual functions
        in case that the current resource represents an SR-IOV physical function NIC.
        """
        return VirtualFunctionAllowedNetworksService(self._connection, '%s/virtualfunctionallowednetworks' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'networkattachments':
            return self.network_attachments_service()
        if path.startswith('networkattachments/'):
            return self.network_attachments_service().service(path[19:])
        if path == 'networklabels':
            return self.network_labels_service()
        if path.startswith('networklabels/'):
            return self.network_labels_service().service(path[14:])
        if path == 'statistics':
            return self.statistics_service()
        if path.startswith('statistics/'):
            return self.statistics_service().service(path[11:])
        if path == 'virtualfunctionallowedlabels':
            return self.virtual_function_allowed_labels_service()
        if path.startswith('virtualfunctionallowedlabels/'):
            return self.virtual_function_allowed_labels_service().service(path[29:])
        if path == 'virtualfunctionallowednetworks':
            return self.virtual_function_allowed_networks_service()
        if path.startswith('virtualfunctionallowednetworks/'):
            return self.virtual_function_allowed_networks_service().service(path[31:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'HostNicService:%s' % self._path


class HostNumaNodeService(MeasurableService):
    """
    """

    def __init__(self, connection, path):
        super(HostNumaNodeService, self).__init__(connection, path)
        self._statistics_service = None

    def get(
        self,
    ):
        """
        """
        query = {}
        request = http.Request(method='GET', path=self._path, query=query)
        response = self._connection.send(request)
        if response.code in [200]:
            buf = None
            reader = None
            try:
                buf = io.BytesIO(response.body)
                reader = xml.XmlReader(buf)
                return readers.NumaNodeReader.read_one(reader)
            finally:
                if buf is not None:
                    buf.close()
                if reader is not None:
                    reader.close()
        else:
            self._check_fault(response)

    def statistics_service(self):
        """
        """
        return StatisticsService(self._connection, '%s/statistics' % self._path)

    def service(self, path):
        """
        Service locator method, returns individual service on which the URI is dispatched.
        """
        if not path:
            return self
        if path == 'statistics':
            return self.statistics_service()
        if path.startswith('statistics/'):
            return self.statistics_service().service(path[11:])
        raise Error('The path \"%s\" doesn\'t correspond to any service' % path)

    def __str__(self):
        return 'HostNumaNodeService:%s' % self._path
