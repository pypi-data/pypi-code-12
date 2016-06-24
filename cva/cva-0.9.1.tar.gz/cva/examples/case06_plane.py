# -*- coding: utf-8 -*-
"""
Case 6: compute a geodesic along the surface of a plane
"""

import cva

def case06_plane():
    cva.solve.select(cva.model.tilted_plane,cva.metric.distance)
    
    # We define a geodesic by fixing its two endpoints in the (u,v) plane:
    sa = (0.1,0.2)   # (u,v) a point on the equator
    sb = (0.9,0.7)   # (u,v) a point at the south pole
    
    steps = 5
    path = cva.solve.run(sa,sb,steps)
    cva.view.set_parm('xyzlim',[0.0,1.0])
    cva.view.draw(path,title="Case 6: Tilted Plane")

if __name__ == '__main__':
    case06_plane()
    
