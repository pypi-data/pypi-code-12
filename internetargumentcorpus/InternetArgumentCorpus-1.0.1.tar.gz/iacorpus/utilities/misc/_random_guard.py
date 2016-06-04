import random


class random_guard:
    """with random_guard(1) do"""
    def __init__(self, random_seed=None):
        self.random_seed = random_seed
    def __enter__(self):
        if self.random_seed is not None:
            self.original_random_state = random.getstate()
            random.seed(self.random_seed)
        return
    def __exit__(self, type, value, traceback):
        if self.random_seed is not None:
            random.setstate(self.original_random_state)
