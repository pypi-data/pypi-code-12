# -*- coding: utf-8 -*-
"""
Case 12: compute the brachistochrone in Moon gravity
"""

import cva

def case12_brachistochrone_plane_moon():
    cva.solve.select(cva.model.vertical_plane,cva.metric.brachistochrone_moon)
    
    # We define a geodesic by fixing its two endpoints in the (u,v) plane:
    sa = (0.0,0.62)   # (u,v)
    sb = (1.0,0.0)   # (u,v)
    
    steps = 5
    path = cva.solve.run(sa,sb,steps)
    cva.view.set_parm('xlim',[0.0,1.0])
    cva.view.set_parm('ylim',[-0.5,0.5])
    cva.view.set_parm('zlim',[0.0,1.0])
    cva.view.draw(path,title="Case 12: Brachistochrone in Moon Gravity")

if __name__ == '__main__':
    case12_brachistochrone_plane_moon()
