# Copyright 2016 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Define Logging API Sinks."""

import re

from gcloud._helpers import _name_from_project_path
from gcloud.exceptions import NotFound


_SINK_TEMPLATE = re.compile(r"""
    projects/            # static prefix
    (?P<project>[^/]+)   # initial letter, wordchars + hyphen
    /sinks/              # static midfix
    (?P<name>[^/]+)      # initial letter, wordchars + allowed punc
""", re.VERBOSE)


def _sink_name_from_path(path, project):
    """Validate a sink URI path and get the sink name.
    :type path: string
    :param path: URI path for a sink API request.
    :type project: string
    :param project: The project associated with the request. It is
                    included for validation purposes.
    :rtype: string
    :returns: Metric name parsed from ``path``.
    :raises: :class:`ValueError` if the ``path`` is ill-formed or if
             the project from the ``path`` does not agree with the
             ``project`` passed in.
    """
    return _name_from_project_path(path, project, _SINK_TEMPLATE)


class Sink(object):
    """Sinks represent filtered exports for log entries.

    See:
    https://cloud.google.com/logging/docs/api/ref_v2beta1/rest/v2beta1/projects.sinks

    :type name: string
    :param name: the name of the sink

    :type filter_: string
    :param filter_: the advanced logs filter expression defining the entries
                    exported by the sink.

    :type destination: string
    :param destination: destination URI for the entries exported by the sink.

    :type client: :class:`gcloud.logging.client.Client`
    :param client: A client which holds credentials and project configuration
                   for the sink (which requires a project).
    """
    def __init__(self, name, filter_, destination, client):
        self.name = name
        self.filter_ = filter_
        self.destination = destination
        self._client = client

    @property
    def client(self):
        """Clent bound to the sink."""
        return self._client

    @property
    def project(self):
        """Project bound to the sink."""
        return self._client.project

    @property
    def full_name(self):
        """Fully-qualified name used in sink APIs"""
        return 'projects/%s/sinks/%s' % (self.project, self.name)

    @property
    def path(self):
        """URL path for the sink's APIs"""
        return '/%s' % (self.full_name)

    @classmethod
    def from_api_repr(cls, resource, client):
        """Factory:  construct a sink given its API representation

        :type resource: dict
        :param resource: sink resource representation returned from the API

        :type client: :class:`gcloud.logging.client.Client`
        :param client: Client which holds credentials and project
                       configuration for the sink.

        :rtype: :class:`gcloud.logging.sink.Sink`
        :returns: Sink parsed from ``resource``.
        :raises: :class:`ValueError` if ``client`` is not ``None`` and the
                 project from the resource does not agree with the project
                 from the client.
        """
        sink_name = _sink_name_from_path(resource['name'], client.project)
        filter_ = resource['filter']
        destination = resource['destination']
        return cls(sink_name, filter_, destination, client=client)

    def _require_client(self, client):
        """Check client or verify over-ride.

        :type client: :class:`gcloud.logging.client.Client` or ``NoneType``
        :param client: the client to use.  If not passed, falls back to the
                       ``client`` stored on the current sink.

        :rtype: :class:`gcloud.logging.client.Client`
        :returns: The client passed in or the currently bound client.
        """
        if client is None:
            client = self._client
        return client

    def create(self, client=None):
        """API call:  create the sink via a PUT request

        See:
        https://cloud.google.com/logging/docs/api/ref_v2beta1/rest/v2beta1/projects.sinks/create

        :type client: :class:`gcloud.logging.client.Client` or ``NoneType``
        :param client: the client to use.  If not passed, falls back to the
                       ``client`` stored on the current sink.
        """
        client = self._require_client(client)
        target = '/projects/%s/sinks' % (self.project,)
        data = {
            'name': self.name,
            'filter': self.filter_,
            'destination': self.destination,
        }
        client.connection.api_request(method='POST', path=target, data=data)

    def exists(self, client=None):
        """API call:  test for the existence of the sink via a GET request

        See
        https://cloud.google.com/logging/docs/api/ref_v2beta1/rest/v2beta1/projects.sinks/get

        :type client: :class:`gcloud.logging.client.Client` or ``NoneType``
        :param client: the client to use.  If not passed, falls back to the
                       ``client`` stored on the current sink.
        """
        client = self._require_client(client)

        try:
            client.connection.api_request(method='GET', path=self.path)
        except NotFound:
            return False
        else:
            return True

    def reload(self, client=None):
        """API call:  sync local sink configuration via a GET request

        See
        https://cloud.google.com/logging/docs/api/ref_v2beta1/rest/v2beta1/projects.sinks/get

        :type client: :class:`gcloud.logging.client.Client` or ``NoneType``
        :param client: the client to use.  If not passed, falls back to the
                       ``client`` stored on the current sink.
        """
        client = self._require_client(client)
        data = client.connection.api_request(method='GET', path=self.path)
        self.filter_ = data['filter']
        self.destination = data['destination']

    def update(self, client=None):
        """API call:  update sink configuration via a PUT request

        See
        https://cloud.google.com/logging/docs/api/ref_v2beta1/rest/v2beta1/projects.sinks/update

        :type client: :class:`gcloud.logging.client.Client` or ``NoneType``
        :param client: the client to use.  If not passed, falls back to the
                       ``client`` stored on the current sink.
        """
        client = self._require_client(client)
        data = {
            'name': self.name,
            'filter': self.filter_,
            'destination': self.destination,
        }
        client.connection.api_request(method='PUT', path=self.path, data=data)

    def delete(self, client=None):
        """API call:  delete a sink via a DELETE request

        See
        https://cloud.google.com/logging/docs/api/ref_v2beta1/rest/v2beta1/projects.sinks/delete

        :type client: :class:`gcloud.logging.client.Client` or ``NoneType``
        :param client: the client to use.  If not passed, falls back to the
                       ``client`` stored on the current sink.
        """
        client = self._require_client(client)
        client.connection.api_request(method='DELETE', path=self.path)
