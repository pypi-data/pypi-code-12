# -*- coding: utf-8 -*-
"""
Case 23: compute a geodesic along the surface of a sphere in R^5
"""

import numpy as np
import cva

def case23_sphere_in_r5():
    cva.solve.select(cva.model.sphere,cva.metric.distance)
    
    ndim = 5
    sa = np.linspace(0.1,0.3,ndim-1)
    sb = np.linspace(0.5,0.7,ndim-1)
    
    steps = 5
    path = cva.solve.run(sa,sb,steps)
    cva.view.set_parm('xyzlim',[-1.0,1.0])

    cva.view.draw(path, title="Case 23: Hypersphere in $R^5$")

if __name__ == '__main__':
    case23_sphere_in_r5()
    
#after step 1:  path_integral = 1.547860 after 26.6 seconds
#after step 2:  path_integral = 1.714237 after 67.3 seconds
#after step 3:  path_integral = 1.738289 after 161  seconds
#after step 4:  path_integral = 1.745367 after 365  seconds
#after step 5:  path_integral = 1.747180 after 783  seconds
#after step 6:  path_integral = 1.747636 after 1634 seconds
#after step 7:  path_integral = 1.747750 after 3346 seconds
#after step 8:  path_integral = 1.747778 after 6785 seconds
#after step 9:  path_integral = 1.747785 after 13669 seconds
#after step 10: path_integral = 1.747787 after 27454 seconds
