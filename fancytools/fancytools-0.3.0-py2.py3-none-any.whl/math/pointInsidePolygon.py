

def pointInsidePolygon(x,y,poly):
    '''
    Determine if a point is inside a given polygon or not
    Polygon is a list of (x,y) pairs.
    
    [code taken from: http://www.ariel.com.au/a/python-point-int-poly.html]

    let's make an easy square:
    
    >>> poly = [ (0,0),\
                 (1,0),\
                 (1,1),\
                 (0,1) ]
    >>> pointInsidePolygon(0.5,0.5, poly)
    True
    >>> pointInsidePolygon(1.5,1.5, poly)
    False
    '''
    n = len(poly)
    inside =False
    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x,p1y = p2x,p2y
    return inside


if __name__ == "__main__":
    import doctest
    doctest.testmod()