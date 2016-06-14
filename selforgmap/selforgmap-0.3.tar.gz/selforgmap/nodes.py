from random import uniform


class Node:
    """node object"""

    def __init__(self, x, y, i, m):
        self.x = x
        self.y = y
        self.i = i
        self.w = [uniform(0, 1) for _ in xrange(m)]
        self.fcount = {}
        self.bmu_count = 0


class Nodes:
    """grid constructor"""

    def __init__(self, n, m):
        self.n = n
        self.m = m
        self.nn = n * n

    def create_nodes(self):
        """builds a nxn grid where each item is a node"""

        nodes = []
        pad = 10
        x = 0
        y = 0 - pad
        for i in xrange(self.nn):
            x = pad * (i % self.n)
            if i % self.n == 0:
                y += pad
            nodes.append(Node(x, y, i, self.m))
        return nodes, pad
