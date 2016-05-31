"""The various clients that help you send stats."""
import itertools
import socket
import time

from . import packets
from .helpers import dot_join


class StatsClient:
    """Basic stats client.

    Holds some functionality, but is not recommended for direct use.
    """

    def __init__(self, prefix, host=None, port=None, disabled=None):
        """Return a new StatsClient."""
        self.prefix = prefix
        self.port = port or 8125
        self.host = host or 'localhost'
        self.disabled = disabled or False

        if not self.disabled:
            self.socket = self.connect(self.host, self.port)

    def counter(self, suffix):
        """Return a counter."""
        return Counter(self, suffix)

    def timer(self, suffix):
        """Return a timer."""
        return Timer(self, suffix)

    def gauge(self, suffix):
        """Return a gauge."""
        return Gauge(self, suffix)

    def set(self, suffix):
        """Return a set."""
        return Set(self, suffix)

    def send(self, *partials):
        """Send a packet."""
        if self.disabled:
            return

        full_packages = (
            dot_join(self.prefix, partial).encode()
            for partial in partials
        )

        self.socket.send(b'\n'.join(full_packages))

    @staticmethod
    def connect(host, port):
        """Connect to the host."""
        connection_info = (host, port)
        conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        conn.connect(connection_info)
        return conn


class Timer:
    """Timer class.

    <name>:<value>|ms
    """

    def __init__(self, client, suffix):
        """Return a new counter."""
        self.client = client
        self.suffix = suffix
        self._start = None
        self._intermediate = None

    def send(self, name, value):
        """Send a measured time off."""
        self.client.send(
            *packets.timer_packet(
                dot_join(self.suffix, name),
                value,
            )
        )

    def start(self):
        """Start the timer."""
        self._start = time.time()
        return self

    def intermediate(self, name):
        """Send an intermediate time."""
        since = self._intermediate or self._start
        self.send(name, time.time() - since)
        self._intermediate = time.time()

    def stop(self, name='total'):
        """Stop the timer."""
        self.send(name, time.time() - self._start)
        self._start = None
        self._intermediate = None


class Counter:
    """Counter class.

    <name>:<value>|c
    """

    def __init__(self, client, suffix):
        """Return a new counter."""
        self.client = client
        self.suffix = suffix

    def increment(self, name, count):
        """Increment the counter."""
        self.client.send(
            *packets.counter_packet(
                dot_join(self.suffix, name),
                count,
            )
        )

    def decrement(self, name, count):
        """Decrement the counter."""
        self.increment(name, -count)

    def from_mapping(self, mapping):
        """Send many values at once from a mapping."""
        parts = (
            packets.counter_packet(dot_join(self.suffix, name), count)
            for name, count in mapping.items()
        )

        self.client.send(*itertools.chain.from_iterable(parts))


class Gauge:
    """Gauge class.

    <name>:<value>|g
    """

    def __init__(self, client, suffix):
        """Return a new counter."""
        self.client = client
        self.suffix = suffix

    def set(self, name, value):
        """Set the current value of the gauge."""
        lines = packets.gauge_set_packet(dot_join(self.suffix, name), value)
        self.client.send(*lines)

    def update(self, name, value):
        """Update the current value with a relative change."""
        lines = packets.gauge_update_packet(dot_join(self.suffix, name), value)
        self.client.send(*lines)


class Set:
    """Set class.

    <name>:<value>|s
    """

    def __init__(self, client, suffix):
        """Return a new counter."""
        self.client = client
        self.suffix = suffix

    def add(self, name, value):
        """Add a value to the set."""
        self.client.send(
            *packets.set_packet(
                dot_join(self.suffix, name),
                value,
            )
        )
