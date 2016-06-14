import math


class Distances(object):
    """distance metrics container"""

    def __init__(self):
        pass

    def euclidian(self, x, y):
        """euclidian distance"""

        return math.sqrt(sum(math.pow(i - j, 2) for i, j in zip(x, y)))

    def manhattan(self, x, y):
        """manhattan distance"""

        return sum(abs(i - j) for i, j in zip(x, y))

    def chebychev(self, x, y):
        """chebychev distance"""

        return max([abs(i - j) for i, j in zip(x, y)])
