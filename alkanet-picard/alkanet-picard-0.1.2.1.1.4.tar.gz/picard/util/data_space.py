'''
    Map data to search spaces
'''
from picard.spaces.mlp import get_space
import numpy as np

def get_data_space(data):
    return get_space(
        np.array(data['xTrain']).shape[1],
        np.array(data['yTrain']).shape[1]
    )
