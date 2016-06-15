# -*- coding: utf-8 -*-

import os
import json

import pytest

from vdirsyncer.storage.google import \
    GoogleCalendarStorage, GoogleContactsStorage

from . import StorageTests


class GoogleTests(StorageTests):
    @pytest.fixture
    def get_storage_args(self, tmpdir):
        prefix = self.storage_class.storage_name.upper()
        try:
            token = os.environ[prefix + '_TOKEN']
            client_id = os.environ['GOOGLE_CLIENT_ID']
            client_secret = os.environ['GOOGLE_CLIENT_SECRET']
        except KeyError as e:
            pytest.skip('Environment variable missing: {}'.format(e))

        token_file = tmpdir.join('google_token')
        token_file.write(token)

        def inner(collection='test'):
            rv = {
                'token_file': str(token_file),
                'client_id': client_id,
                'client_secret': client_secret
            }
            if collection is not None:
                rv = self.storage_class.create_collection(
                    collection=collection, **rv)
            return rv
        return inner


class TestContacts(GoogleTests):
    storage_class = GoogleContactsStorage


class TestCalendar(GoogleTests):
    storage_class = GoogleCalendarStorage
