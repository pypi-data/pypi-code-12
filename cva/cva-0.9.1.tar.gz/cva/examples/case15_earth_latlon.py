# -*- coding: utf-8 -*-
"""
Case 15: compute a geodesic along the surface of the Earth using lat/lon
"""

import cva

def case15_earth_latlon():
    cva.solve.select(cva.model.earth,cva.metric.distance)
    
    # ETSU University, Johnson City, TN USA
    lat = 36.303181
    lon = -82.368280
    sa = cva.model.latlon(lat, lon)
    # University of Sidney, Sydney, New South Wales, Australia
    lat = -33.889272
    lon = 151.194132
    sb = cva.model.latlon(lat, lon)
    
    # find a minimum path
    steps = 5
    path = cva.solve.run(sa,sb,steps)
    cva.view.set_parm('xyzlim',[-6400,6400])
    cva.view.draw(path, title="Case15: Path connecting two universities")

if __name__ == '__main__':
    case15_earth_latlon()
