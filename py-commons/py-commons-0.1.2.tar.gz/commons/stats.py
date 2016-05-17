from __future__ import print_function
import functools

from six.moves._thread import start_new_thread
from time import sleep
import timeit


__all__ = ['DecoratorStatsManager']


class Stats(object):
    """
    Base class for stats collectors
    """

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return self.__class__.__name__ + str(self.dict)

    @property
    def dict(self):
        return self.__dict__

    def merge_to_lifetime(self, lifetime):
        raise NotImplementedError()


class InvocationStats(Stats):

    def __init__(self):
        super(InvocationStats, self).__init__()
        self.invocations = 0
        self.errors = 0
        self.successes = 0

    def merge_to_lifetime(self, lifetime):
        assert isinstance(lifetime, InvocationStats)
        lifetime.invocations += self.invocations
        lifetime.errors += self.errors
        lifetime.successes += self.successes


class LatencyStats(Stats):
    def __init__(self):
        super(LatencyStats, self).__init__()
        self.total_time = 0.0
        self.total_calls = 0
        self.max_time = 0.0
        self.min_time = None

    class meter(object):
        __slots__ = ['time_start', 'stats']

        def __init__(self, stats):
            self.stats = stats

        def __enter__(self):
            self.time_start = timeit.default_timer()

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.stats.total_calls += 1
            exec_time = timeit.default_timer() - self.time_start
            self.stats.total_time += exec_time
            self.stats.max_time = max((exec_time, self.stats.max_time))
            self.stats.min_time = min((exec_time, self.stats.min_time)) if self.stats.min_time else exec_time

    def measure(self):
        return LatencyStats.meter(self)

    @property
    def avg(self):
        return self.total_time / self.total_calls if self.total_calls else 0

    @property
    def dict(self):
        return {
            'avg': self.avg,
            'max': self.max_time,
            'min': self.min_time if self.min_time else 0
        }

    def merge_to_lifetime(self, lifetime):
        assert isinstance(lifetime, LatencyStats)
        lifetime.total_time += self.total_time
        lifetime.total_calls += self.total_calls
        lifetime.max_time = max((lifetime.max_time, self.max_time))
        if self.min_time:
            lifetime.min_time = min((lifetime.min_time, self.min_time))


class StatGroup(object):
    def __init__(self):
        self.data = {}

    def get(self, key, default):
        return self.data.get(key, default)

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    @property
    def dict(self):
        return dict((name, value.dict) for name, value in self.data.items())


class HistoryGroup(object):
    def __init__(self):
        self.data = {}

    def merge(self, stat_group):
        assert isinstance(stat_group, StatGroup)
        for k, v in stat_group.dict.items():
            hist = self.data.get(k, [])
            hist.append(v)

    @property
    def dict(self):
        return self.__dict__


class StatsManager(object):
    """
    Main class that keeps track of stats, history and lifetime aggregates
    """
    def __init__(self, period=1, history=20):
        self.current_stats = {}
        self.history = []
        self.total_stats = {}
        self.max_history = history
        self.stats_builders = {}
        if period > 0:
            self.timer = timer(period, self.tick)
        self.tick()

    def tick(self):
        """
        Push current stats to history and reset them.
        """
        current_stats, self.current_stats = self.current_stats, dict((k, v()) for k, v in self.stats_builders.items())
        self.history = ([self.current_stats] + self.history)[:self.max_history]
        for k, v in current_stats.items():
            assert isinstance(v, Stats)
            v.merge_to_lifetime(self.total_stats[k])

    def __str__(self):
        return self.__class__.__name__ + str(self.current_stats)

    def __repr__(self):
        return self.__class__.__name__ + str(self.__dict__)

    @property
    def dict(self):
        return {
            'current': self.to_dict(self.current_stats),
            'history': [self.to_dict(_) for _ in self.history],
            'lifetime': self.to_dict(self.total_stats)
        }

    @staticmethod
    def to_dict(stats):
        return dict((name, value.dict) for name, value in stats.items())


class DecoratorStatsManager(StatsManager):
    """
    This class provides decorator-based interface for stats collection
    """
    def invocation_counter(self, stats_name):
        self.total_stats[stats_name] = InvocationStats()
        self.stats_builders[stats_name] = InvocationStats

        def decorator(f):
            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                stats = self.current_stats.get(stats_name, InvocationStats())
                try:
                    stats.invocations += 1
                    res = f(*args, **kwargs)
                    stats.successes += 1
                    return res
                except:
                    stats.errors += 1
                    raise
                finally:
                    self.current_stats[stats_name] = stats

            return wrapper
        return decorator

    def latency_meter(self, stats_name):
        self.total_stats[stats_name] = LatencyStats()
        self.stats_builders[stats_name] = LatencyStats

        def decorator(f):
            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                stats = self.current_stats.get(stats_name, LatencyStats())
                try:
                    with stats.measure():
                        return f(*args, **kwargs)
                finally:
                    self.current_stats[stats_name] = stats
            return wrapper
        return decorator


def timer(interval, function, iterations=0, *args, **kwargs):
    """Repeating timer. Returns a thread id."""

    def __repeat_timer(interval, function, iterations, args, kwargs):
        """Inner function, run in background thread."""
        count = 0
        while iterations <= 0 or count < iterations:
            sleep(interval)
            function(*args, **kwargs)
            count += 1

    return start_new_thread(__repeat_timer, (interval, function, iterations, args, kwargs))


if __name__ == '__main__':
    """
    A very simple usage example:
    """
    stats = DecoratorStatsManager(0)

    @stats.latency_meter('groupname.latency')
    @stats.invocation_counter('groupname.statsname')
    def foo(a):
        """
        Some doc for foo
        """
        return a

    print('foo: ', foo)
    print('foo(123): ', foo(123))
    print('stats: ', stats)