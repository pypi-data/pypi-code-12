"""
Mysql databse backend via ssh_tunnel
@author: drwrong<yuhangchaney@gmail.com>
"""

from django.db.backends.mysql.base import DatabaseWrapper as MysqlDatabaseWrapper
from sshtunnel import SSHTunnelForwarder


class DatabaseWrapper(MysqlDatabaseWrapper):

    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        self.tunnel = None

    def get_connection_params(self):
        kwargs = super(DatabaseWrapper, self).get_connection_params()
        host = kwargs['host']
        port = kwargs['port']
        config = self.settings_dict["TUNNEL_CONFIG"]
        config['remote_bind_address'] = (host, port)
        self.tunnel = SSHTunnelForwarder(**config)
        self.tunnel.start()
        kwargs["host"] = '127.0.0.1'
        kwargs['port'] = self.tunnel.local_bind_port
        return kwargs

    def _close(self):
        super(DatabaseWrapper, self)._close()
        if self.tunnel is not None:
            self.tunnel.stop()
