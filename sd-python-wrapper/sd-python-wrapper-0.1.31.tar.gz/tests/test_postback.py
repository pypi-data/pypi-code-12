#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from hashlib import md5
import json

from mock import patch
from serverdensity.wrapper import ApiClient
from serverdensity.wrapper import Postback


class PostbackTest(unittest.TestCase):

    @patch.object(ApiClient, '_make_request')
    def setUp(self, mock_make_request):
        self.client = ApiClient('aeou')
        self.client._make_request = mock_make_request
        self.client._make_request.return_value = {'postbacks': 'result'}
        self.postbacks = Postback(api=self.client)

    def test_postback_create(self):
        payload = json.dumps({'agentkey': 'aeu'})
        data = {'payload': payload}

        hashed = md5(payload.encode('utf-8')).hexdigest()
        data.update({'hash': hashed})
        self.postbacks.create(payload={'agentkey': 'aeu'}, account_name='example')
        self.client._make_request.assert_called_with(
            data=data,
            method='POST',
            url=Postback.PATHS['create'],
            params=None,
            headers={'X-Forwarded-Host': 'example.serverdensity.io'}
        )

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
