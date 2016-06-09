environ = {
    'APPD_APP_NAME': 'hello-app',
    'APPD_TIER_NAME': 'hello-web-tier',
    'APPD_NODE_NAME': 'hello-web-node1',

    'APPD_WSGI_SCRIPT_ALIAS': 'abc.py',
    'APPD_WSGI_CALLABLE_OBJECT': 'foobar',

    'APPD_LOGS_DIR': '/tmp/fixtures/logs',
    'APPD_LOGGING_LEVEL': 'info',
    'APPD_DEBUG_LOG': 'on',

    'APPD_CONTROLLER_HOST': 'controller.example.org',
    'APPD_CONTROLLER_PORT': '1234',
    'APPD_SSL_ENABLED': 'on',
    'APPD_ACCOUNT_NAME': 'someaccount',
    'APPD_ACCOUNT_ACCESS_KEY': 'supersecretkey',

    'APPD_HTTP_PROXY_HOST': 'http-proxy.example.org',
    'APPD_HTTP_PROXY_PORT': '8080',
    'APPD_HTTP_PROXY_USER': 'proxyuser',
    'APPD_HTTP_PROXY_PASSWORD_FILE': '/tmp/fixtures/proxy/passwd',

    'APPD_PROXY_CONTROL_PATH': '/tmp/fixtures/proxycontrol',
    'APPD_PROXY_STARTUP_READ_TIMEOUT_MS': '234',
    'APPD_PROXY_STARTUP_INITIAL_RETRY_DELAY_MS': '345',
    'APPD_PROXY_STARTUP_MAX_RETRY_DELAY_MS': '456',

    'APPD_PROXY_CONFIG_SOCKET_NAME': 'hello',
    'APPD_CONFIG_SERVICE_RELOAD_INTERVAL_MS': '567',
    'APPD_CONFIG_SERVICE_MAX_RETRIES': '678',

    'APPD_INCLUDE_AGENT_FRAMES': 'on',
}

environ_expect = dict((k[5:], v) for k, v in environ.items())
environ_expect.update(
    DEBUG_LOG=True,
    CONTROLLER_PORT=1234,
    SSL_ENABLED=True,
    HTTP_PROXY_PORT=8080,
    PROXY_STARTUP_READ_TIMEOUT_MS=234,
    PROXY_STARTUP_INITIAL_RETRY_DELAY_MS=345,
    PROXY_STARTUP_MAX_RETRY_DELAY_MS=456,
    CONFIG_SERVICE_RELOAD_INTERVAL_MS=567,
    CONFIG_SERVICE_MAX_RETRIES=678,
    INCLUDE_AGENT_FRAMES=True,
)
