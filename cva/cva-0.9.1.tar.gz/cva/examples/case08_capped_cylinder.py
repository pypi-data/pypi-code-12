# -*- coding: utf-8 -*-
"""
Case 8: compute a geodesic along the surface of a sphere
"""

import cva

def case08_capped_cylinder():
    cva.solve.select(cva.model.capped_cylinder,cva.metric.distance)
    
    # We define a geodesic by fixing its two endpoints in the (u,v) plane:
#    sa = (0.0,0.1)   # (u,v) a point on the equator
#    sb = (0.4,0.9)   # (u,v) a point at the south pole
    sa = (0.1,0.2)   # (u,v) 
    sb = (0.9,0.6)   # (u,v) 
    
    steps = 5
    path = cva.solve.run(sa,sb,steps)
    cva.view.set_parm('xlim',[-1.0,1.0])
    cva.view.set_parm('ylim',[-1.0,1.0])
    cva.view.set_parm('zlim',[0.0,1.0])
    cva.view.draw(path,title="Case 8: Capped Cylinder")

if __name__ == '__main__':
    case08_capped_cylinder()
    
