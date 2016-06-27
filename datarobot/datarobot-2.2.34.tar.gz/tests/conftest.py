import pytest
from .utils import SDKTestcase
from datarobot.client import get_client


@pytest.yield_fixture(scope='module')
def client():
    """A mocked client."""
    SDKTestcase.setUpClass()
    yield get_client()
    SDKTestcase.tearDownClass()
