# -*- coding: utf-8 -*-
"""
Case 21: compute a geodesic along the surface of a sphere in R^3
"""

import cva

def case21_sphere_in_r3():
    cva.solve.select(cva.model.sphere,cva.metric.distance)
    
    sa = (0.5,0.5)   # (u,v) a point on the equator
    sb = (1.0,0.5)   # (u,v) a point at the south pole    
    steps = 5
    path = cva.solve.run(sa,sb,steps)
    cva.view.draw(path, title="Case 21: Sphere in $R^3$")

if __name__ == '__main__':
    case21_sphere_in_r3()
