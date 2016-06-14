# -*- coding: utf-8 -*-

import pytest
import requests_mock

from rio_client import Client

@pytest.fixture
def client():
    return Client(dsn='http://sender:password@domain:8080/1/project')

def test_set_transport(client):
    with requests_mock.Mocker() as m:
        url = 'http://sender:password@domain:8080/event/project/emit/action'
        m.post(url, json={
            'message': 'ok',
            'event': {'uuid': 'uuid'},
            'task': {'id': 1},
        })
        data = client.emit('action', {'key': 'value'})
        assert data['is_success']
