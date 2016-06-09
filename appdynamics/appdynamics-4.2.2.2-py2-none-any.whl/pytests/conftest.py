import logging
import mock
import pytest
import sys
from wsgiref.util import setup_testing_defaults

from pytests.helpers import TestAgent, NullHandler

from appdynamics import config
from appdynamics.lib import LazyWsgiRequest
from appdynamics.agent import api
from appdynamics.agent import bootstrap
from appdynamics.agent import pb
from appdynamics.agent.models import transactions

# another note:  all the class scope fixtures are not really class scope when
# the tests are run randomly.  should I change them to session scope?

# here is how to run the tests
# py.test --random --cov -rx --quiet

# finish snapshot service test?
# sql tests? think they are done...

# coverage fail_under is not working....


@pytest.fixture
def exception_logger(_test_logger, _remove_side_effect):
    """Return a Mock which tracks logged exceptions during the test.

    When using this fixture, the normal behaviour of the logging mechanism can
    be observed, as opposed to the test logger used by default, which raises
    logged exceptions.

    """
    _test_logger.exception.reset_mock()
    _remove_side_effect(_test_logger.exception)
    return _test_logger.exception


@pytest.fixture(autouse=True)
def agent(_test_agent):
    """Return the global agent instance used for testing.

    The following methods are patched for convenience::
        start
        start_transaction
        end_transaction
        start_exit_call
        end_exit_call

    For the most part, this agent behaves just like a real Agent instance, so
    be careful not to alter its state during tests.

    """
    _test_agent.reset_mocks()
    _test_agent.active_bts = {}
    return _test_agent


@pytest.fixture
def active_bt(request, agent, mocker, environ):
    """Return a BT which is active for the duration of the test.

    If many tests in the same class require an active BT, it is easist to
    invoke this fixture with a `pytest.mark.usefixtures('active_bt')` decorator
    on the test class.

    """
    bt = agent.start_transaction(transactions.ENTRY_PYTHON_WEB, request=LazyWsgiRequest(environ))
    mocker.patch.object(bt, 'wait_for_bt_info_response', return_value=True)
    bt.bt_info_response = pb.BTInfoResponse()
    request.addfinalizer(agent.end_transaction)
    return bt


@pytest.fixture
def backend(agent):
    """Return an HTTP backend with empty properties called 'test_backend'.

    """
    return agent.backend_registry.get_backend()


@pytest.fixture
def exit_call(request, agent, active_bt, backend):
    """Return an exit call which is active for the duration of the test.

    """
    exit_call = agent.start_exit_call(active_bt, sys._getframe(), backend)

    def end_exit_call():
        if active_bt._active_exit_call:
            agent.end_exit_call(active_bt, exit_call)

    request.addfinalizer(end_exit_call)
    return exit_call


@pytest.fixture
def bt_exceptions(mocker):
    """Return a list of exceptions which were added to BTs during this test.

    This fixture enables the test to inspect exceptions which were added to BTs
    even after they have ended.

    """

    exceptions = []
    add_exception = transactions.Transaction.add_exception

    def _add_exception(transaction, *args):
        add_exception(transaction, *args)

        # If a new exception was added, add it to our local version of the list.
        if len(transaction.exceptions) != len(exceptions):
            exceptions.append(transaction.exceptions[-1])

    mocker.patch.object(transactions.Transaction, 'add_exception', new=_add_exception)
    return exceptions


@pytest.fixture
def environ():
    """Return an environ for passing to WSGI applications.

    """
    environ = {}
    setup_testing_defaults(environ)
    return environ


@pytest.fixture
def start_response(mocker):
    """Return a start_response callable for passing to WSGI applications.

    """
    start_response = mocker.MagicMock()
    start_response.__name__ = 'start_response'
    return start_response


@pytest.fixture(scope='session')
def _test_logger():
    # Do not try to create real log files.
    mock.patch('logging.handlers.RotatingFileHandler').start()
    appd_logger = logging.getLogger('appdynamics')
    agent_logger = logging.getLogger('appdynamics.agent')
    api_logger = logging.getLogger('appdynamics.agent.api')
    # Don't allow any handlers to be added, but provide a NullHandler to
    # suppress 'no handlers could be found' warnings.
    appd_logger.handlers = [NullHandler()]
    agent_logger.handlers = [NullHandler()]
    mock.patch.object(appd_logger, 'addHandler').start()
    mock.patch.object(agent_logger, 'addHandler').start()

    # Re-raise logged agent exceptions to try to catch hidden errors during
    # testing.  If you want to specifically test that some code does not
    # propagate exceptions, use the `exception_logger` fixture, which restores
    # normal behaviour and allows you to check that the exception was logged.
    def reraise(msg, *args, **kwargs):
        print(msg)
        raise
    mock.patch.object(agent_logger, 'exception', side_effect=reraise).start()
    mock.patch.object(api_logger, 'exception', side_effect=reraise).start()
    return agent_logger


@pytest.fixture(scope='session')
def _test_agent(_test_logger):
    # Note that we depend on _test_logger here to ensure that the logger is
    # patched before the module hooks are run.
    config.merge({
        'APP_NAME': 'app_id',
        'TIER_NAME': 'tier_id',
        'NODE_NAME': 'node_id',
    })

    agent = TestAgent()
    bootstrap(agent)
    api.api._agent = agent
    return agent


@pytest.fixture
def _remove_side_effect(request):
    def remove_side_effect(mock):
        side_effect = mock.side_effect
        mock.side_effect = None

        def restore():
            mock.side_effect = side_effect
        request.addfinalizer(restore)
    return remove_side_effect
