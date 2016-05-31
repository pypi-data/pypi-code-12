"""Packet formatter functions."""


def timer_packet(name, value):
    """Return a timer formatted packet."""
    yield packet(
        name,
        int(value * 1000),
        'ms',
    )


def counter_packet(name, value):
    """Return a counter formatted packet."""
    yield packet(name, str(value), 'c')


def gauge_set_packet(name, value):
    """Return a gauge formatted packet."""
    if value < 0:
        yield packet(name, '0', 'g')

    yield packet(name, str(value), 'g')


def gauge_update_packet(name, value):
    """Return a gauge formatted packet."""
    if value >= 0:
        value = '+{}'.format(value)
    yield packet(name, str(value), 'g')


def set_packet(name, value):
    """Return a set formatted packet."""
    yield packet(name, value, 's')


def packet(name, value, suffix):
    """Return a formatted packet.

    General utility function, to build other formatters on top of.
    """
    return '{name}:{value}|{suffix}'.format(
        name=name,
        value=str(value),
        suffix=suffix,
    )
