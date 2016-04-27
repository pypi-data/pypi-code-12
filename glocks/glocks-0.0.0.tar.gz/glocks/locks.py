from .base import LockBase
from .exceptions import ClientError

from redis.exceptions import RedisError
from twisted.internet import task, reactor

import time


class LoopingCall(task.LoopingCall):

    def __init__(self, func, interval, now, *args, **kwargs):
        self.interval = interval
        self.now = now
        task.LoopingCall.__init__(self, func, *args, **kwargs)

    def start(self):
        return task.LoopingCall.start(
            self, self.interval, self.now
        )


class Lock(LockBase):
    """
    """
    # KEYS[1] - lock name
    # ARGV[1] - token
    # ARGV[2] - timeout in milliseconds
    # return 1 if lock was acquired, otherwise 0
    LUA_ACQUIRE_LOCK = """
        if redis.call('setnx', KEYS[1], ARGV[1]) == 1 then
            redis.call('pexpire', KEYS[1], ARGV[2])
            return 1
        end
        return 0
    """

    # KEYS[1] - lock name
    # ARGS[1] - token
    # return 1 if the lock was released, otherwise 0
    LUA_RELEASE_LOCK = """
        local token = redis.call('get', KEYS[1])
        if not token then
            return 1
        end
        if token ~= ARGV[1] then
            return 0
        end
        redis.call('del', KEYS[1])
        return 1
    """

    def setup(self):
        try:
            self.client = self.setup_client(self.host_info)
        except RedisError as err:
            raise ClientError(err.message)

        self.acquire_script = self.client.register_script(
            self.LUA_ACQUIRE_LOCK
        )
        self.release_script = self.client.register_script(
            self.LUA_RELEASE_LOCK
        )

    def run_script(self, script, keys, args):
        return script(keys=keys, args=args, client=self.client)


class RLock(Lock):
    """
        Re-entrant global lock
    """

    # KEYS[1] - lock name
    # ARGV[1] - token
    # ARGV[2] - timeout in milliseconds
    # return 1 if lock was acquired, otherwise 0
    LUA_ACQUIRE_LOCK = """
        if redis.call('setnx', KEYS[1], ARGV[1]) == 1 then
            redis.call('pexpire', KEYS[1], ARGV[2])
            return 1
        end
        local token = redis.call('get', KEYS[1])
        if token == ARGV[1] then
            redis.call('pexpire', KEYS[1], ARGV[2])
            return 1
        end
        return 0
    """

    KEEP_ALIVE_FREQUENCY = 2

    def __init__(self,  host_info, name, ttl, keep_alive=True, now=True, reactor=reactor):
        super(RLock, self).__init__(host_info, name, ttl)

        self.reactor = reactor
        self.keep_alive = keep_alive
        self.now = now
        self.keep_alive_task = None
        self.trigger_keep_alive()

    def acquire(self):
        output = super(RLock, self).acquire()
        return output

    def trigger_keep_alive(self):
        if self.keep_alive and not self.keep_alive_task:
            interval = (float(self.ttl) / float(self.KEEP_ALIVE_FREQUENCY)) - 1.
            self.keep_alive_task = self.setup_loopingcall(interval / 1000.)
            self.keep_alive_task.clock = self.reactor
            self.keep_alive_task.start()

    def setup_loopingcall(self, interval):
        """
            Override this method to control the behaviour of the
            keep_alive_task. It must return n instance of a
            twisted.internet.task.LoopingCall subclass.

            interval in seconds
        """
        return LoopingCall(self.acquire, interval, self.now)

    def release(self):
        if self.keep_alive_task and self.keep_alive_task.running:
            self.keep_alive_task.stop()
        return super(RLock, self).release()


class DLock(Lock):
    """
        Distributed global lock
    """

    quorum = None
    TIMEOUT_FACTOR = 0.8

    def setup(self):
        clients = []
        errors = []
        for info in self.host_info:
            try:
                clients.append(
                    self.setup_client(info)
                )
            except RedisError as err:
                errors.append(err)
                continue

        self.quorum = (len(self.host_info) / 2) + 1

        if len(clients) < self.quorum:
            errmsg = 'Could not connect to a majority of the clients. {}'.format(
                '::'.join([error.message for error in errors])
            )
            raise ClientError(errmsg)

        self.clients = clients

        client = clients[0]
        self.acquire_script = client.register_script(
            self.LUA_ACQUIRE_LOCK
        )
        self.release_script = client.register_script(
            self.LUA_RELEASE_LOCK
        )

    @property
    def timeout(self):
        # the maximum allowed time that is allowed to elapse when
        # trying to acquire the locks
        return int(self.ttl * self.TIMEOUT_FACTOR) - 2

    def run_script(self, script, keys, args):
        count = 0
        errors = []
        start_time = time.time()
        for client in self.clients:
            try:
                count += script(keys=keys, args=args, client=client)
            except RedisError as err:
                errors.append(err)
                continue

        elapsed_time = (time.time() - start_time) * 1000
        success = 0
        if count < self.quorum:
            self.failure('Quorum Error', errors)
        elif elapsed_time >= self.timeout:
            self.failure('Timeout Error', errors)
        else:
            success = 1
        return success

    def failure(self, base_message, errors):
        """
            Override this method so to alter the behaviour of the lock
            when failures occur e.g. track failures and raise after some limit.
        """
        pass

    def acquire(self):
        success = super(DLock, self).acquire()
        if not success:
            self.release()
        return success


class RDLock(DLock, RLock):
    """
        Re-entrant distributed global lock
    """
