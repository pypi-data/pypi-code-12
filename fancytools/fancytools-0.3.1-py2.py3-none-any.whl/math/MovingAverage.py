class MovingAverage(object):
    '''
    calc. the mean of the last n values, see http://en.wikipedia.org/wiki/Moving_average
    :param n: number of the last values to calc the mean from
    '''
    def __init__(self, n):
        self.maxQuantity = n # middle until this quantity is reached
        self.reset()


    def reset(self):
        self.value = 0.0
        self._quantity = 0


    def update(self, signal):
        ##dependent to the size of the cluster (v = old + (new-old)/size_cluser))
        if self._quantity < self.maxQuantity:
            self._quantity += 1
        self.value += (signal - self.value) / self._quantity
        return self.value

