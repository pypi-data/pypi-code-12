# -*- coding: utf-8 -*-
"""
Case 26: compute a geodesic along the surface of a sphere in R^8
"""

import numpy as np
import cva

def case26_sphere_in_r8():
    cva.solve.select(cva.model.sphere,cva.metric.distance)
    
    ndim = 8
    sa = np.linspace(0.1,0.3,ndim-1)
    sb = np.linspace(0.5,0.7,ndim-1)
    
    steps = 5
    path = cva.solve.run(sa,sb,steps)

if __name__ == '__main__':
    case26_sphere_in_r8()
    

#after step 1:  path_integral = 1.488223 after 2301.990542 seconds
#after step 2:  path_integral = 1.931927 after 9226.857173 seconds
#after step 3:  path_integral = 2.333551 after 25961.989080 seconds
#after step 4:  path_integral = 2.105507 after 62067.506190 seconds
#after step 5:  path_integral = 2.686958 after 139553.422914 seconds
