__version__ = "1.1.0"

try:
    from tornado.options import define
    from . import cli

    define('debug', default=False, help='Enable debug output')
    define('offline', default=False, help='Run in offline mode')
    define('config', default='~/.brush.conf', help='Path to configuration file',
           callback=lambda path: cli.read_config_file(path))
    define('save-when-unlocked', default=False,
           help='Write data to database when comb is unlocked')

    define('xmlrpc-host', type=str, help='XMLRPC server hostname')
    define('xmlrpc-port', type=int, default=8123, help='XMLRPC server port')
    define('xmlrpc-user', default=None, help='XMLRPC server user')
    define('xmlrpc-password', default=None, help='XMLRPC server password')

    define('sql-url', default='sqlite:///brush.sqlite', help='SQL database URL')
    define('sql-table', default='brush', help='SQL table name')

    define('redis-host', default='localhost', help='Redis hostname')
    define('redis-port', default=6379, help='Redis port')
    define('redis-password', default=None, help='Redis password')

    define('server-port', default=8090, help='Port to serve on')
    define('server-url-prefix', default='', help='URL prefix')
except ImportError:
    pass
