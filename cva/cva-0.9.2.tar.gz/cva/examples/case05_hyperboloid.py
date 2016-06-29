# -*- coding: utf-8 -*-
"""
Case 5: compute a geodesic along the surface of a hyperboloid in one sheet
"""

import cva

def case05_hyperboloid():
    cva.solve.select(cva.model.hyperboloid,cva.metric.distance)
    
    # We define a geodesic by fixing its two endpoints in the (u,v) plane:
    sa = (0.9,0.0)   # (u,v)
    sb = (0.1,0.3)   # (u,v)
    
    steps = 5
    path = cva.solve.run(sa,sb,steps)
    cva.view.set_parm('xyzlim',[-2.2,2.2])

    cva.view.draw(path,title="Case 5: Hyperboloid in One Sheet")

if __name__ == '__main__':
    case05_hyperboloid()
    
