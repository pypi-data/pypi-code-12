# Copyright (C) 2014, Red Hat, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
External event triggering for servers, not to be used by users.
"""

from novaclient import extension
from novaclient.tests.unit import utils
from novaclient.tests.unit.v2.contrib import fakes
from novaclient.v2.contrib import server_external_events as ext_events


class ServerExternalEventsTestCase(utils.TestCase):
    def setUp(self):
        super(ServerExternalEventsTestCase, self).setUp()
        extensions = [
            extension.Extension(ext_events.__name__.split(".")[-1],
                                ext_events),
        ]
        self.cs = fakes.FakeClient(extensions=extensions)

    def test_external_event(self):
        events = [{'server_uuid': 'fake-uuid1',
                   'name': 'test-event',
                   'status': 'completed',
                   'tag': 'tag'},
                  {'server_uuid': 'fake-uuid2',
                   'name': 'test-event',
                   'status': 'completed',
                   'tag': 'tag'}]
        result = self.cs.server_external_events.create(events)
        self.assert_request_id(result, fakes.FAKE_REQUEST_ID_LIST)
        self.assertEqual(events, result)
        self.cs.assert_called('POST', '/os-server-external-events')
