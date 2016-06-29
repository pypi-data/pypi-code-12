# -*- coding: utf-8 -*-
"""
Case 14: compute the brachistochrone on a hyperboloid
"""

import cva

def case14_brachistochrone_hyperboloid():
    cva.solve.select(cva.model.hyperboloid,cva.metric.brachistochrone_earth)
    
    # We define a geodesic by fixing its two endpoints in the (u,v) plane:
#    sa = (0.0,1.0)   # (u,v)
#    sb = (0.4,0.0)   # (u,v)
    sa = (0.0,0.0)   # (u,v)
    sb = (1.0,0.4)   # (u,v)
    
    steps = 5
    path = cva.solve.run(sa,sb,steps)
    cva.view.set_parm('xyzlim',[-2.2,2.2])
    cva.view.draw(path,title="Case 14: Brachistochrone on a Hyperboloid")

if __name__ == '__main__':
    case14_brachistochrone_hyperboloid()
