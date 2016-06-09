# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Interceptor for Redis.

"""

from appdynamics.agent.interceptor.cache import CacheInterceptor


class RedisConnectionInterceptor(CacheInterceptor):
    def __init__(self, agent, cls):
        super(RedisConnectionInterceptor, self).__init__(agent, cls, 'REDIS')

    def _send_packed_command(self, send_packed_command, connection, command):
        with self.log_exceptions():
            bt = self.bt
            if bt:
                try:
                    server_pool = ['%s:%s' % (connection.host, connection.port)]
                except AttributeError:
                    # For UnixDomainSocketConnection objects.
                    server_pool = [connection.path]
                backend = self.get_backend(server_pool)
                if backend:
                    self.start_exit_call(bt, backend, operation=str(command))

        result = send_packed_command(connection, command)
        self.end_exit_call()
        return result


def intercept_redis(agent, mod):
    RedisConnectionInterceptor(agent, mod.Connection).attach('send_packed_command')
