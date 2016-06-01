from pycam02ucs.cm.viscm import viscm
from colorspacious import cspace_convert
# from pycam02ucs import cspace_convert

from parula import parula_map
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

import numpy as np

from scipy import interpolate

x = np.linspace(0, 1, 100)
parula_rgb = parula_map(x)[:, :3]
parula_samples_Jpapbp = cspace_convert(parula_rgb, "sRGB1", "CAM02-UCS")

distances = np.cumsum(np.sqrt(np.sum((parula_samples_Jpapbp[:-1, ...] - parula_samples_Jpapbp[1:, ...]) ** 2, axis=-1)))
distances = np.concatenate(([0], distances))

newparula_samples_Jpapbp = interpolate.interp1d(distances, parula_samples_Jpapbp, axis=0, kind='quadratic')(
    np.linspace(0, distances.max(), 100))
newparula_samples_sRGB = cspace_convert(newparula_samples_Jpapbp, "CAM02-UCS", "sRGB1")

smooth_parula = LinearSegmentedColormap.from_list('smooth_parula', np.clip(newparula_samples_sRGB, 0, 1))

viscm(smooth_parula)
plt.show()
