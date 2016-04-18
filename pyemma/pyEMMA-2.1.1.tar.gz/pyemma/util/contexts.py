'''
Created on 04.01.2016

@author: marscher
'''
from contextlib import contextmanager
import random

import numpy as np


class conditional(object):
    """Wrap another context manager and enter it only if condition is true.
    """

    def __init__(self, condition, contextmanager):
        self.condition = condition
        self.contextmanager = contextmanager

    def __enter__(self):
        if self.condition:
            return self.contextmanager.__enter__()

    def __exit__(self, *args):
        if self.condition:
            return self.contextmanager.__exit__(*args)


@contextmanager
def numpy_random_seed(seed=42):
    """ sets the random seed of numpy within the context.

    Example
    -------
    >>> import numpy as np
    >>> with numpy_random_seed(seed=0):
    ...    np.random.randint(1000)
    684
    """
    old_state = np.random.get_state()
    np.random.seed(seed)
    try:
        yield
    finally:
        np.random.set_state(old_state)


@contextmanager
def random_seed(seed=42):
    """ sets the random seed of Python within the context.

    Example
    -------
    >>> import random
    >>> with random_seed(seed=0):
    ...    random.randint(0, 1000) # doctest: +SKIP
    864
    """
    old_state = random.getstate()
    random.seed(seed)
    try:
        yield
    finally:
        random.setstate(old_state)
