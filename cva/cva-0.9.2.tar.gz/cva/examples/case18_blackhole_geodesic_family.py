# -*- coding: utf-8 -*-
"""
Case 18: compute geodesic family near Sgr A* using rectangular coordinates
"""

import numpy as np
import cva

def case18_blackhole_geodesic_family():
    cva.solve.select(cva.model.blackhole,cva.metric.schwarzschild)
    
    steps = 4
    for delta in np.arange(0.05,0.5,0.1):
        sa = (0.0+delta,1.0)        # (u,v)
        sb = (0.0+delta,0.0)        # (u,v)
        path = cva.solve.run(sa,sb,steps) # left vertical
        cva.view.draw_hold(path,title="Case18: Geodesics near Sgr A*")
        sa = (0.0,0.0+delta)
        sb = (1.0,0.0+delta)
        path = cva.solve.run(sa,sb,steps,silent=True) # bottom horizontal
        cva.view.draw_hold(path)
        sa = (0.5+delta,0.0)
        sb = (0.5+delta,1.0)
        path = cva.solve.run(sa,sb,steps,silent=True) # right vertical
        cva.view.draw_hold(path)
        sa = (1.0,0.5+delta)
        sb = (0.0,0.5+delta)
        path = cva.solve.run(sa,sb,steps,silent=True)  # top horizontal
        cva.view.draw_hold(path)
    cva.view.draw_show()

if __name__ == '__main__':
    case18_blackhole_geodesic_family()
    
