import math


class Decay(object):
    """decaying methods container"""

    def __init__(self, n, lr):
        self.n = n
        self.lr = lr

    def exp(self, t):
        """basic exponential decay"""

        return self.n * math.exp((math.log(self.lr) / self.n * t))
