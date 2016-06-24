# -*- coding: utf-8 -*-
"""
Case 24: compute a geodesic along the surface of a sphere in R^6
"""

import numpy as np
import cva

def case24_sphere_in_r6():
    cva.solve.select(cva.model.sphere,cva.metric.distance)
    
    ndim = 6
    sa = np.linspace(0.1,0.3,ndim-1)
    sb = np.linspace(0.5,0.7,ndim-1)
    
    steps = 1
    path = cva.solve.run(sa,sb,steps)
    cva.view.set_parm('xyzlim',[-1.0,1.0])

    cva.view.draw(path, title="Case 24: Hypersphere in $R^6$")

if __name__ == '__main__':
    case24_sphere_in_r6()
    
#after step 1:  path_integral = 1.572299 after 238  seconds
#after step 2:  path_integral = 1.669267 after 482  seconds
#after step 3:  path_integral = 1.700871 after 1103 seconds
#after step 4:  path_integral = 1.710147 after 2383 seconds
#after step 5:  path_integral = 1.712541 after 4969 seconds
