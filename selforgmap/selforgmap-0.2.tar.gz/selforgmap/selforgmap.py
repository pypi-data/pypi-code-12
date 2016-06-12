import math
from random import random as rnd

from nodes import Nodes
from decay import Decay
from distances import Distances
from neighborhoods import square_


class SOMSupervised(object):
    """the standard supervised version of som operating on voting principles"""

    def __init__(self, n, m, lr=False):
        self.n = n
        self.m = m
        self.lr = 0.5 if not lr else lr
        self.nodes, self.pad = Nodes(n, m).create_nodes()
        self.decay = Decay(self.n, self.lr)
        self.metric = Distances().euclidian
        self.smp_count = 1
        self.bmus = {}

    def pick_(self, pcount):
        """picks a random sample from dataset"""

        return [int(rnd() * pcount) for _ in xrange(self.smp_count)]

    def bmu(self, item):
        """gets the best bmu (based on metric)"""

        min_d = float('infinity')
        candidate = None
        for node in self.nodes:
            if self.metric(item, node.w) < min_d:
                min_d = self.metric(item, node.w)
                candidate = node
        return candidate

    def get_neighbors(self, bmu, n_nghbs):
        """returns immediate neighbors of bmu under n_nhgbs distance"""

        n_items = range(1, n_nghbs + 1)
        p_obj = {
            'p_i': bmu.i,
            'p_x': bmu.x,
            'p_y': bmu.y,
            'min_x': bmu.x,
            'min_y': bmu.y,
            'max_x': bmu.x,
            'max_y': bmu.y
        }

        for i in n_items:
            k = i
            nxmin = math.floor(p_obj['p_x'] - (self.pad * k))
            nxmax = math.ceil(p_obj['p_x'] + (self.pad * k))
            nymin = math.floor(p_obj['p_y'] - (self.pad * k))
            nymax = math.ceil(p_obj['p_y'] + (self.pad * k))
            if nxmin < p_obj['p_x']:
                p_obj['min_x'] = nxmin
            if nxmax > p_obj['max_x']:
                p_obj['max_x'] = nxmax
            if nymin < p_obj['p_y']:
                p_obj['min_y'] = nymin
            if nymax > p_obj['p_y']:
                p_obj['max_y'] = nymax
        neighbors = square_(p_obj, self.nodes)
        return neighbors

    def update_nodes(self, neighbors, item, label, bmu):
        """updates neighbors of bmu"""

        for node in neighbors:
            distance = float(abs(bmu.x - node.x) + abs(bmu.y - node.y)) / 2
            force = 1 / max([distance, 1])
            for i, j in enumerate(node.w):
                node.w[i] = node.w[i] + force * (item[i] - node.w[i])
            node.fcount[label] = force
        return

    def predict(self, x):
        """predicts based on the voting method"""

        f = {}
        bmu = self.bmu(x)
        neighbors = self.get_neighbors(bmu, 2)
        for each in neighbors:
            winner = max(each.fcount, key=lambda n: each.fcount[n])
            f[winner] = f.get(winner, 0) + 1
        return max(f, key=lambda n: f[n])

    def train(self, data, labels):
        """main training method to build clusters in som grid"""

        n_nghbs = self.n
        pcount = len(data)
        t = 0
        while n_nghbs > 1:
            samples = self.pick_(pcount)
            for sample in samples:
                item = data[sample]
                label = labels[sample]
                bmu = self.bmu(item)
                bmu.bmu_count += 1
                self.bmus[bmu.i] = 1
                n_nghbs = int(self.decay.exp(t) / 2)
                neighbors = self.get_neighbors(bmu, n_nghbs)
                self.update_nodes(neighbors, item, label, bmu)
                t += 1
        return
