import logging
from mock import patch, MagicMock as Mock
import sys

from appdynamics import config
from appdynamics.agent import services
from appdynamics.agent.core import registries
from appdynamics.agent.core.agent import Agent
from appdynamics.agent.core.timer import Timer
from appdynamics.agent.models import exitcalls
from appdynamics.agent.models import transactions


class Patchable(object):
    def __init__(self, *args, **kwargs):
        self.mocks = []

    def patch_method(self, method):
        """Replace method with a mock, but run the real method as a side effect.

        This is minimally intrusive, but allows use to check call_count etc.

        """
        mock = patch.object(self, method, side_effect=getattr(self, method)).start()
        self.mocks.append(mock)

    def reset_mocks(self):
        """Reset all patched methods.

        """
        for mock in self.mocks:
            mock.reset_mock()


class TestBackendRegistry(registries.BackendRegistry, Patchable):
    def __init__(self, *args, **kwargs):
        super(TestBackendRegistry, self).__init__(*args, **kwargs)
        self.patch_method('get_backend')

    def get_backend(self, *args, **kwargs):
        # Give the backend a registered ID so it can generate correlation
        # headers.
        return exitcalls.Backend(0, 0, {}, 'test_backend', registered_id=123)


class TestAgent(Agent, Patchable):
    def __init__(self, started=True):
        super(TestAgent, self).__init__()

        if started:
            self.start_mocks()
            self.started = True

    def start_mocks(self):
        # All this code seems pretty brittle.  How can I refactor the agent so that these
        # things don't need to be done manually here?  Like if the services aren't defined, then it will work.
        # Don't have things like 'enabled' be checking a service is started!
        # Have a 'start_service' function which sets a flag!

        # this is basically 'on_start_node_response'.
        # why don't I just mock all the services and registries and allow on_start_response to run?
        # here I would add a side_effect to start the proxy control svc instead.

        self.app_id = config.APP_NAME
        self.tier_id = config.TIER_NAME
        self.node_id = config.NODE_NAME
        self.controller_guid = 'controller_guid'
        self.account_guid = 'account_guid'

        self.patch_method('start_transaction')
        self.patch_method('end_transaction')
        self.patch_method('start_exit_call')
        self.patch_method('end_exit_call')
        self.patch_method('start')

        self.bt_registry = registries.TransactionRegistry()
        self.backend_registry = TestBackendRegistry()
        self.error_config_registry = registries.ErrorConfigRegistry()
        self.data_gatherer_registry = registries.DataGathererRegistry()
        self.naming_registry = registries.NamingSchemeRegistry()
        patch.object(self.naming_registry, 'match',
                     return_value=registries.TransactionNamingMatch(name='bt_name', naming_scheme='scheme')).start()

        # Mock agent services.
        self.proxy_control_svc = Mock(services.proxycontrol.ProxyControlService)
        self.config_svc = Mock(services.config.ConfigService('socket_name', 'update_agent_config', 'reconnect_proxy',
                                                             None))
        self.tx_svc = Mock(services.transaction.TransactionService)
        self.tx_monitor_svc = Mock(services.transaction_monitor.TransactionMonitorService)

        self._tx_factory = transactions.make_transaction_factory(self, lambda: Mock(Timer),
                                                                 self.error_config_registry.is_bt_error)

    def reset_mocks(self):
        super(TestAgent, self).reset_mocks()
        self.backend_registry.reset_mocks()
        self.proxy_control_svc.reset_mock()
        self.config_svc.reset_mock()
        self.tx_svc.reset_mock()
        self.tx_monitor_svc.reset_mock()


class NullHandler(logging.Handler):
    def emit(self, record):
        pass


def verify_bt(agent):
    """Verify that the agent started and ended a BT.

    """
    assert agent.start_transaction.call_count == 1
    assert agent.end_transaction.call_count == 1


def verify_bt_exception(exceptions, exception_name):
    """Verify that the exception is in the exceptions list.

    `exceptions` is a list returned from the `bt_exceptions` fixture.

    """
    assert len(exceptions) == 1
    assert exceptions[0].klass == exception_name


def verify_exit_call(agent, exit_type, exit_subtype, properties, operation='', call_count=1,
                     get_backend_call_count=None):
    """Verify the agent started an exit call with the supplied arguments.

    """
    assert agent.start_exit_call.call_count == call_count
    assert agent.end_exit_call.call_count == call_count

    # this check is kind of dodgey, it's like this so I can check things like:
    # 'SET' in "['*3\r\n$3\r\nSET\r\n$9\r\nsomething\r\n$1\r\n0\r\n']"
    assert operation in agent.start_exit_call.call_args[1]['operation']

    assert agent.backend_registry.get_backend.call_count == (get_backend_call_count or call_count)
    backend_args = agent.backend_registry.get_backend.call_args

    assert backend_args[0][0:2] == (exit_type, exit_subtype)

    backend_properties = backend_args[0][2]
    assert backend_properties == properties


def verify_exit_call_exception(agent, exception):
    """Verify the agent ended an exit call with the supplied exception.

    """
    exc_info = agent.end_exit_call.call_args[1]['exc_info']
    assert exc_info[1] is exception


def wsgi_request(application, url, environ, start_response):
    environ['PATH_INFO'] = url
    return application(environ, start_response)


def import_or_reload_module(name):
    module = sys.modules.get(name)
    if module:
        reload(module)
    else:
        __import__(name)
