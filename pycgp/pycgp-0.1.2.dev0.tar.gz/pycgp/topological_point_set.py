import numpy as np
from itertools import product

from .cgp_config import coordinate_type


class TopologicalPointSet():
    def __init__(self, cell_order, points=np.zeros((0,3))):
        self.cell_order = cell_order
        self.points = np.abs(points)
        self.sign = 1 - 2 * np.any(np.asarray(points) < 0, axis=1).astype(np.int8)

    def extend(self, tps):
        """
        Merges another TopologicalPointSet into this TopologicalPointSet
        :param tps: another TopologicalPointSet
        """
        assert(self.cell_order == tps.cell_order)
        self.points = np.vstack((self.points, tps.points))
        self.sign = np.hstack((self.sign, tps.sign))

    def adjacent_voxels(self):
        arr = np.zeros((2*len(self.points),3), dtype=coordinate_type)
        arr[::2,:] = self.points / 2
        arr[1::2,:] = (self.points + 1) / 2
        return arr

    def size(self):
        return len(self.points)

    def point_to_voxel(self, point):
        c = [None]*3
        for i in range(3):
            if point[i] % 2 == 0:
                c[i] = int(point[i]/2),
            else:
                c[i] = (int(point[i]/2), int((point[i]+1)/2))

        return list(product(c[0], c[1], c[2]))
