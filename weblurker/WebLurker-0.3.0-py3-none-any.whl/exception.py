"""
Here goes all exceptions
Most of them are only informative, so no extensive code is added

"""


class NoBrowserError(Exception):
    """
    Thrown when an unitialized browser is being called
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class CacheError(Exception):
    """
    Thrown when an error in the cache system is found
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
