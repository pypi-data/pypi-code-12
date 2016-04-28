import pytest


def pytest_addoption(parser):
    parser.addoption('--port', action='store', default='8080',
                     help='port where fakeserver is running, default 8080')


@pytest.fixture
def port(request):
    return request.config.getoption("--port")
