# -*- coding: utf-8 -*-
"""
Case 2: compute a geodesic along the surface of a sphere
"""

import cva

def case02_sphere():
    cva.solve.select(cva.model.sphere,cva.metric.distance)
    
    # We define a geodesic by fixing its two endpoints in the (u,v) plane:
    sa = (0.5,0.5)   # (u,v) a point on the equator
    sb = (1.0,0.5)   # (u,v) a point at the south pole

    steps = 5
    path = cva.solve.run(sa,sb,steps)
    cva.view.set_parm('xyzlim',[-1.0,1.0])
    cva.view.draw(path,title="Case 2: Unit Sphere")

if __name__ == '__main__':
    case02_sphere()
    
