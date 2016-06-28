# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
"""
Pre-processing operations based on NDVars
"""


def threshold_envelope(x):
    z = x - x.mean(('case', 'time'))
    z /= z.std(('case', 'time'))
    z = z.mean('sensor')
