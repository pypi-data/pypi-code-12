"""Integration tests configuration file."""
import pytest
from cf_predict.test.conftest import pytest_configure  # pylint: disable=unused-import
from cf_predict import create_app


@pytest.fixture
def app():
    """Create a Flask test client."""
    app = create_app("integration_testing")
    return app
