import numpy as np

from .cgp_config import coordinate_type

class CartesianPointSet():
    def __init__(self, topological_points, shape=None):
        topological_points = np.array(topological_points, coordinate_type)
        self.cartesian_points = np.concatenate(
            (topological_points/2, (topological_points+1)/2), 0)
