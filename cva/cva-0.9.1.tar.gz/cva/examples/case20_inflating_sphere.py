# -*- coding: utf-8 -*-
"""
Case 20: inflating sphere using the Minkowski metric
"""

import numpy as np
import cva

def case20_inflating_sphere():
    cva.solve.select(cva.model.inflating_sphere,cva.metric.minkowski)
    
    # We define a geodesic by fixing its two endpoints in the phase space:
    sa = (0.0,0.5,0.0)   # (u,v,w) an event on the equator at ct=0.0
    sb = (1.0,1.0,0.6)   # (u,v,w) an event at the south pole at ct=1.0
    
    steps = 5
    path = cva.solve.run(sa,sb,steps)
    cva.view.draw(path,title="Case 20: Sphere inflating at 50\% light speed")

if __name__ == '__main__':
    case20_inflating_sphere()
    

#step 1:  path_integral = 0.908899 after 2.506 seconds
#step 2:  path_integral = 0.650995 after 9.964 seconds
#step 3:  path_integral = 0.693488 after 27.106 seconds
#step 4:  path_integral = 0.790692 after 63.731 seconds
#step 5:  path_integral = 0.758812 after 142.090 seconds
#step 6:  path_integral = 0.691824 after 298.410 seconds
#step 7:  path_integral = 0.677787 after 616.618 seconds
#step 8:  path_integral = 0.679627 after 1263.531 seconds
#step 9:  path_integral = 0.677407 after 2546.428 seconds
#step 10: path_integral = 0.676588 after 5139.246 seconds
