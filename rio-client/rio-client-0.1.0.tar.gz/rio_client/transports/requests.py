# -*- coding: utf-8 -*-
"""
rio_client.transports.requests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from __future__ import absolute_import

import requests

from ..retry import Retry
from .base import Transport

class RequestsTransport(Transport):
    """Requests Transport.

    Emit actions via awesome `requests`.
    """

    def emit(self, action, payload):
        """Emit action with payload via `requests.post`."""
        url = self.get_emit_api(action)
        headers = {'User-Agent': 'rio/0.1.0', 'X-Rio-Protocol': '1'}
        resp = requests.post(url, json=payload, headers=headers)
        data = resp.json()
        is_success = resp.status_code == 200
        result = dict(
            is_success=is_success,
            message=data['message'],
        )
        if result['is_success']:
            result.update(
                event_uuid=data['event']['uuid'],
                task_id=data['task']['id'],
            )
        return result

    def retry(self, times):
        """Retry on request connection error."""
        return Retry((requests.ConnectionError, ), times)
