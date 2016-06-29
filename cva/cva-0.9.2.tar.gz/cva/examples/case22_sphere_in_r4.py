# -*- coding: utf-8 -*-
"""
Case 22: compute a geodesic along the surface of a sphere in R^4
"""

import numpy as np
import cva

def case22_sphere_in_r4():
    cva.solve.select(cva.model.sphere,cva.metric.distance)
    
    ndim = 4
    sa = np.linspace(0.1,0.3,ndim-1)
    sb = np.linspace(0.5,0.7,ndim-1)
    
    steps = 5
    path = cva.solve.run(sa,sb,steps)
    cva.view.set_parm('xyzlim',[-1.0,1.0])
    cva.view.draw(path, title="Case 22: Hypersphere in $R^4$")

if __name__ == '__main__':
    case22_sphere_in_r4()


#after step 1:  path_integral = 1.696701 after 3.31 seconds
#after step 2:  path_integral = 1.763354 after 10.3 seconds
#after step 3:  path_integral = 1.782555 after 26.6 seconds
#after step 4:  path_integral = 1.787777 after 61.5 seconds
#after step 5:  path_integral = 1.789106 after 134  seconds
#after step 6:  path_integral = 1.789440 after 280  seconds
#after step 7:  path_integral = 1.789523 after 575  seconds
#after step 8:  path_integral = 1.789544 after 1165 seconds
#after step 9:  path_integral = 1.789549 after 2348 seconds
#after step 10: path_integral = 1.789550 after 4714 seconds
