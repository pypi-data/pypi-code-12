# -*- coding: utf-8 -*-
"""
Case 25: compute a geodesic along the surface of a sphere in R^7
"""

import numpy as np
import cva

def case25_sphere_in_r7():
    cva.solve.select(cva.model.sphere,cva.metric.distance)
    
    ndim = 7
    sa = np.linspace(0.1,0.3,ndim-1)
    sb = np.linspace(0.5,0.7,ndim-1)
    
    steps = 5
    path = cva.solve.run(sa,sb,steps)
    
if __name__ == '__main__':
    case25_sphere_in_r7()
    

#after step 1:  path_integral = 1.497589 after 447   seconds
#after step 2:  path_integral = 1.630233 after 1780  seconds
#after step 3:  path_integral = 1.670822 after 4877  seconds
#after step 4:  path_integral = 1.682637 after 11348 seconds
#after step 5:  path_integral = 1.685694 after 24773 seconds
