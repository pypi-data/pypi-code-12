import numpy as np

def kfunc(kpts):
	E= 200.0+np.exp(-sum(kpts))
	return E