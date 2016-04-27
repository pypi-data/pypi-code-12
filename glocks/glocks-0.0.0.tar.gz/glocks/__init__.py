try:
    from .locks import Lock, RLock, DLock, RDLock  # NOQA
except ImportError:
    pass

__version__ = '0.0.0'
