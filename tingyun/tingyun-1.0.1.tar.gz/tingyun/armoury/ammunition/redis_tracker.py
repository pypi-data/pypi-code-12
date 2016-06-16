"""this module used to wrap the specify method to RedisTrace

"""

from tingyun.armoury.ammunition.timer import Timer
from tingyun.armoury.ammunition.tracker import current_tracker
from tingyun.logistics.warehouse.redis_node import RedisNode
from tingyun.logistics.basic_wrapper import wrap_object, FunctionWrapper


class RedisTrace(Timer):
    """
    """
    def __init__(self, tracker, command):
        """
        :return:
        """
        super(RedisTrace, self).__init__(tracker)
        self.command = command

    def create_node(self):
        """
        :return:
        """
        tracker = current_tracker()
        if tracker:
            tracker.redis_time = self.duration

        return RedisNode(command=self.command, children=self.children, start_time=self.start_time,
                         end_time=self.end_time, duration=self.duration, exclusive=self.exclusive)

    def terminal_node(self):
        return True


def redis_trace_wrapper(wrapped, command):
    """
    :return:
    """
    def dynamic_wrapper(wrapped, instance, args, kwargs):
        tracker = current_tracker()
        if tracker is None:
            return wrapped(*args, **kwargs)

        if instance is not None:
            _command = command(instance, *args, **kwargs)
        else:
            _command = command(*args, **kwargs)

        with RedisTrace(tracker, _command):
            return wrapped(*args, **kwargs)

    def literal_wrapper(wrapped, instance, args, kwargs):
        tracker = current_tracker()
        if tracker is None:
            return wrapped(*args, **kwargs)

        with RedisTrace(tracker, command):
            return wrapped(*args, **kwargs)

    if callable(command):
        return FunctionWrapper(wrapped, dynamic_wrapper)

    return FunctionWrapper(wrapped, literal_wrapper)


def wrap_redis_trace(module, object_path, command):
    wrap_object(module, object_path, redis_trace_wrapper, (command,))
