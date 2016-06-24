# -*- coding: utf-8 -*-
"""
Case 13: compute the brachistochrone on a unit sphere
"""

import cva

def case13_brachistochrone_unit_sphere():
    cva.solve.select(cva.model.sphere,cva.metric.brachistochrone_earth)
    
    # We define a geodesic by fixing its two endpoints in the (u,v) plane:
#    sa = (0.2,0.6)   # (u,v)
#    sb = (0.4,1.0)   # (u,v)   
    sa = (0.3,0.2)   # (u,v)
    sb = (0.5,0.5)   # (u,v)
    
    steps = 5
    path = cva.solve.run(sa,sb,steps)
    cva.view.set_parm('xyzlim',[-1.0,1.0])
    cva.view.draw(path,title="Case 13: Brachistochrone on a Unit Sphere")

if __name__ == '__main__':
    case13_brachistochrone_unit_sphere()
    
