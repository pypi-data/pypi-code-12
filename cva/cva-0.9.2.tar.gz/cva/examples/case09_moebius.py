# -*- coding: utf-8 -*-
"""
Case 9: compute a geodesic along the surface of a Moebius strip
"""

import cva

def case09_moebius():
    cva.solve.select(cva.model.moebius,cva.metric.distance)
    
    # We define a geodesic by fixing its two endpoints in the (u,v) plane:
    sa = (1.0,0.39)   # (u,v)
    sb = (1.0,0.0)   # (u,v)
    
    steps = 5
    cva.view.set_parm('xlim',[-1.5,1.5])
    cva.view.set_parm('ylim',[-1.5,1.5])
    cva.view.set_parm('zlim',[-4.0,4.0])
    path = cva.solve.run(sa,sb,steps)
    cva.view.draw(path,title="Case 9: Moebius Strip")

if __name__ == '__main__':
    case09_moebius()
