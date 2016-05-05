# -*- coding: utf-8 -*-

import logging
import pytest
from logging.handlers import SocketHandler, DEFAULT_TCP_LOGGING_PORT
from multiprocessing import Process
from log_server import start_server, configure_client_logger, stop_server


def pytest_addoption(parser):
    group = parser.getgroup('pytest-single_file_logging')
    group.addoption(
        '--logconfig',
        action='store',
        dest='log_config',
        default='log.config',
        help='Set the logging as specified for dictconfig.'
             ' See https://docs.python.org/3.5/library/logging.config.html#logging-config-dictschema for details'
    )
    group.addoption(
        '--serverip',
        action='store',
        dest='server_ip',
        default='127.0.0.1',
        help='Set the ip of the log server.'
    )


@pytest.mark.tryfirst
def pytest_configure(config):
    from time import sleep
    if hasattr(config, 'slaveinput'):
        ip = config.getoption('server_ip')
        node_id = config.slaveinput['slaveid']
        l = configure_client_logger(ip, '')
        l.info('Finished configuring logger for {}'.format(node_id))
    else:
        # need xdist for this to work, but not sure if I need this line since I don't want to defer any hooks
        # config.pluginmanager.getplugin('xdist')
        file_name = config.getoption('log_config')
        p = Process(target=start_server, args=(file_name,))
        p.start()
        # TODO: may need to wait until sever is confirmed to be listening
        # socket_logger = logging.getLogger(__name__)
        # socket_handler = SocketHandler('localhost', DEFAULT_TCP_LOGGING_PORT)
        # socket_logger.addHandler(socket_handler)
        # socket_logger.info('Finished configuring logger')


def pytest_unconfigure(config):
    if not hasattr(config, 'slaveinput'):
        # send signal to server saying it's time to stop
        stop_server()


# def pytest_report_teststatus(report):
#     l = logging.getLogger(__name__)
#     l.info('Test ')
#     pass


@pytest.fixture
def logger(request):
    """
    Lets each test have access to a logger with the name of the worker
    """
    si = getattr(request.config, "slaveinput", None)
    if si:
        log = logging.getLogger(si['slaveid'])
    else:
        log = logging.getLogger()
    return log
