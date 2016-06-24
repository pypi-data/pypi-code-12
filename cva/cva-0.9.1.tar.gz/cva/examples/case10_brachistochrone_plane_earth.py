# -*- coding: utf-8 -*-
"""
Case 10: compute the brachistochrone on a vertical plane
"""

import cva

def case10_brachistochrone_plane_earth():
    cva.solve.select(cva.model.vertical_plane,cva.metric.brachistochrone_earth)
    
    # We define a geodesic by fixing its two endpoints in the (u,v) plane:
    sa = (0.0,0.62)   # (u,v)
    sb = (1.0,0.0)    # (u,v)
    
    steps = 5
    path = cva.solve.run(sa,sb,steps)
    cva.view.set_parm('xlim',[0.0,1.0])
    cva.view.set_parm('ylim',[-0.5,0.5])
    cva.view.set_parm('zlim',[0.0,1.0])
    cva.view.draw(path,title="Case 10: Brachistochrone in Earth Gravity")

if __name__ == '__main__':
    case10_brachistochrone_plane_earth()
    
