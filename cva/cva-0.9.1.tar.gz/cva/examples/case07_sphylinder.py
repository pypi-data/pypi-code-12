# -*- coding: utf-8 -*-
"""
Case 7: compute a geodesic along the surface of a sphylinder
"""

import cva

def case07_sphylinder():
    cva.solve.select(cva.model.sphylinder,cva.metric.distance)
    
    # We define a geodesic by fixing its two endpoints in the (u,v) plane:
#    sa = (0.0,0.1)   # (u,v) a point on the equator
#    sb = (0.25,0.8)   # (u,v) a point at the south pole    
    sa = (0.1,0.15)   # (u,v)
    sb = (0.9,0.45)   # (u,v)
    
    steps = 5
    path = cva.solve.run(sa,sb,steps)
    cva.view.set_parm('xyzlim',[-1.0,1.0])
    cva.view.draw(path,title="Case 7: Sphylinder")

if __name__ == '__main__':
    case07_sphylinder()
    
