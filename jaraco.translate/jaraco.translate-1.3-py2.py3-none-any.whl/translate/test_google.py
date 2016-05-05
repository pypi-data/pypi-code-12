import os

import pytest

from . import google


@pytest.fixture
def google_api_key(monkeypatch):
	key = os.environ.get('GOOGLE_API_KEY')
	if not key:
		pytest.skip("Need GOOGLE_API_KEY environment variable")
	monkeypatch.setattr(google.translate, 'API_key', key, raising=False)


def test_translate(google_api_key):
	# Google seems to title-case Hello World. *shrug*
	expected = 'Hello World'
	assert google.translate('hola mundo') == expected
