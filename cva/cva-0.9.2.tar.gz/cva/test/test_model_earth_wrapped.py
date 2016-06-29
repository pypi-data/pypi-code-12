import py.test

import cva
import numpy as np

cva.solve.select(cva.model.earth,cva.metric.distance)

ngrid = 31
limit = 3e-7

# longitudes wrap directly
for u in np.linspace(0.0,1.0,ngrid):
    for v in np.linspace(0.0,1.0,ngrid):
        x_center = np.asarray(cva.model.earth((u,v)))
        x_above  = np.asarray(cva.model.earth((u,v+1.0)))
        x_below  = np.asarray(cva.model.earth((u,v-1.0)))
        try: 
            dist = cva.metric.distance(x_center,x_below)
            assert dist < limit
        except:
            print "b: ",dist,u,v,x_center,x_below
        try:       
            dist = cva.metric.distance(x_center,x_above)
            assert dist < limit
        except:
            print "a: ",dist,u,v,x_center,x_above

# negative u is a latitude wrap around the north pole
# we reverse the sign of u, and take v + 0.5
for u in np.linspace(0.0,1.0,ngrid):
    for v in np.linspace(0.0,1.0,ngrid):
        x_center = np.asarray(cva.model.earth((u,v)))
        x_left  = np.asarray(cva.model.earth((-u,v+0.5)))
        try:       
            dist = cva.metric.distance(x_center,x_left)
            assert dist < limit
        except:
            print "a: ",dist,u,v,x_center,x_left

# u > 1.0 is a wrap around the south pole
# we set u = 2.0 - u and take v+0.5
for u in np.linspace(0.0,1.0,ngrid):
    for v in np.linspace(0.0,1.0,ngrid):
        x_center = np.asarray(cva.model.earth((u,v)))
        x_right  = np.asarray(cva.model.earth((2.0-u,v+0.5)))
        try:       
            dist = cva.metric.distance(x_center,x_right)
            assert dist < limit
        except:
            print "a: ",dist,u,v,x_center,x_right
