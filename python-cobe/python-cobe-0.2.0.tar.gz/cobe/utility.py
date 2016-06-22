"""Utilities to help identify the current host and process."""


def identify_host():  # pragma: no cover
    """Identify the host the current process is running on.

    This creates an entity identifier that identifies the host the
    current process is running on. This is useful for relating custom
    entities to the host.

    :returns: A :class:`cobe.Identifier` object for the host.
    """
    raise NotImplementedError  # TODO: Everything


def identify_process():  # pragma: no cover
    """Identify the process.

    This creaets an entity identifier that identifies the process
    Python is currently running in. This is useful for relating custom
    entities to the interpreter's process.

    :returns: A :class:`cobe.Identifier` object for the current process.
    """
    raise NotImplementedError  # TODO: Everything
