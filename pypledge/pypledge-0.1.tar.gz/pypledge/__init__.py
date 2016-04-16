"""Binding for the pledge(2) system call on OpenBSD. Allows restricting
   process functionality for correctness and security."""
import ctypes
from typing import Iterable


def pledge(promises: Iterable[str]) -> None:
    """Restrict the current process to the functionality defined in a
       list of promises, as defined by pledge(2)."""
    try:
        _pledge = ctypes.cdll['libc.so'].pledge
    except (OSError, AttributeError) as err:
        raise OSError('pledge() not supported') from err

    result = _pledge(bytes(' '.join(promises), 'ascii'), None)
    if result < 0:
        raise PermissionError('Failed to pledge: {}'.format(promises))
