"""Binding for the pledge(2) system call on OpenBSD. Allows restricting
   process functionality for correctness and security."""
import ctypes
import os
from typing import Iterable, List


def pledge(promises: Iterable[str], paths: List[bytes]=None) -> None:
    """Restrict the current process to the functionality defined in a
       list of promises, as defined by pledge(2)."""
    if isinstance(promises, str):
        promises = promises.split()

    try:
        libc = ctypes.CDLL('libc.so', use_errno=True)
        _pledge = libc.pledge
        _pledge.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_char_p)]
        _pledge.restype = ctypes.c_int
    except (OSError, AttributeError) as err:
        raise OSError('pledge() not supported') from err

    paths_buf = None
    if paths is not None:
        if not all(isinstance(path, bytes) for path in paths):
            raise TypeError('Path whitelist must be list of bytes')

        PathsArray = ctypes.c_char_p * (len(paths) + 1)
        paths_buf = PathsArray(*(paths + [None]))

    result = _pledge(bytes(' '.join(promises), 'ascii'), paths_buf)
    if result < 0:
        errno = ctypes.get_errno()
        raise OSError(errno, os.strerror(errno))
