# -*- coding: utf-8 -*-
"""
Case 4: compute a geodesic along the surface of a cylinder
"""

import cva

def case04_cylinder():
    cva.solve.select(cva.model.cylinder,cva.metric.distance)
    
    # We define a geodesic by fixing its two endpoints in the (u,v) plane:
    sa = (1.0,0.5)   # (u,v)
    sb = (0.1,1.0)   # (u,v)   

    steps = 5
    path = cva.solve.run(sa,sb,steps)
    cva.view.set_parm('xlim',[-1.0,1.0])
    cva.view.set_parm('ylim',[-1.0,1.0])
    cva.view.set_parm('zlim',[0.0,1.0])    
    cva.view.draw(path,title="Case 4: Cylinder")

if __name__ == '__main__':
    case04_cylinder()
    
