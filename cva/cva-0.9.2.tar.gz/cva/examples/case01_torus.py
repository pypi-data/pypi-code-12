# -*- coding: utf-8 -*-
"""
Case 1: compute a geodesic along the surface of a torus
"""

import cva

def case01_torus():
    cva.solve.select(cva.model.torus,cva.metric.distance)
    
    # We define a geodesic by fixing its two endpoints in the (u,v) plane:
    sa = (0.5,0.1)   # (u,v)
    sb = (1.0,0.5)   # (u,v)
    
    steps = 5
    path = cva.solve.run(sa,sb,steps)
    cva.view.set_parm('xyzlim',[-2.5,2.5])
    cva.view.draw(path, title="Case 1: Torus")

if __name__ == '__main__':
    case01_torus()
