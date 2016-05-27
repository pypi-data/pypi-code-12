import numpy as np


def rotatePolygon(polygon, theta, origin=None):
    """Rotates the given polygon around the origin or if not given it's center of mass
    
    polygon: np.array( (x1,y1), (...))
    theta: rotation clockwise in RADIAN
    origin = [x,y] - if not given set to center of gravity
    
    returns: None
    """
    if origin is None:
        origin = np.mean(polygon,axis=0, dtype=polygon.dtype)
    #polygon = polygon.copy()
    polygon -= origin
    for n,corner in enumerate(polygon):
        polygon[n] = corner[0]*np.cos(theta)-corner[1]*np.sin(theta) , corner[0]*np.sin(theta)+corner[1]*np.cos(theta)
    polygon += origin
    return polygon