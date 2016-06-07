"""
Implementation of the CloudHub API functionality related to notifications.
"""
import json

from bigpy import DotDict

from cloudhub.common import CloudHubApi


class CloudHubNotification(CloudHubApi):

    INFO = 'INFO'
    WARN = 'WARN'
    ERROR = 'ERROR'

    @property
    def _base_url(self):
        return '{0}/notifications'.format(self.api_base_url)

    def create_notification(self, application_name, message, transaction_id, priority=INFO, custom_properties=None):
        data = DotDict()
        data.domain = application_name
        data.message = message
        data.transactionId = transaction_id
        data.priority = priority

        if custom_properties:
            data.customProperties = custom_properties

        response = self._post(data=json.dumps(data))

        # expecting 201 Created
        if response.status_code != 201:
            self._handle_standard_errors(response, 'Failed to create notification')
