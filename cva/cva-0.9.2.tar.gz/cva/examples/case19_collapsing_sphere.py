# -*- coding: utf-8 -*-
"""
Case 109 collapsing sphere using the Minkowski metric
"""

import numpy as np
import cva

def case19_collapsing_sphere():
    cva.solve.select(cva.model.collapsing_sphere,cva.metric.minkowski)
    
    # We define a geodesic by fixing its two endpoints in phase space:
    sa = (0.0,0.5,0.0)   # (u,v,w) an event on the equator at ct=0.0
    sb = (1.0,1.0,0.6)   # (u,v,w) an event at the south pole at ct=0.9    

    steps = 5
    path = cva.solve.run(sa,sb,steps)
    cva.view.draw(path,title="Case 19: Sphere collapsing at 50\% light speed")

if __name__ == '__main__':
    case19_collapsing_sphere()
    

#step 1:  path_integral = 0.903135 after 2.432 seconds
#step 2:  path_integral = 0.698767 after 9.669 seconds
#step 3:  path_integral = 0.729855 after 26.479 seconds
#step 4:  path_integral = 0.748744 after 62.540 seconds
#step 5:  path_integral = 0.772700 after 136.902 seconds
#step 6:  path_integral = 0.762853 after 288.724 seconds
#step 7:  path_integral = 0.753423 after 593.518 seconds
#step 8:  path_integral = 0.753451 after 1207.126 seconds
#step 9:  path_integral = 0.749706 after 2435.318 seconds
#step 10:  path_integral = 0.746652 after 4893.771 seconds
