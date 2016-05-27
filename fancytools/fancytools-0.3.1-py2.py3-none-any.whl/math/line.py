'''
Collection of line-based functions
line given as: 
    x0,y0,x1,y1 = line
'''
from numpy import pi, array, empty
from math import sin, cos, atan2, hypot, acos, copysign
from fancytools.math.rotatePolygon import rotatePolygon
from numba import jit
from numpy import argmax


@jit(nopython=True)   
def sort(line):
    '''
    change point position  if x1,y0 < x0,y0
    '''
    x0,y0,x1,y1 = line
    turn = False
    if abs(x1-x0) > abs(y1-y0):
        if x1 < x0:
            turn = True
    elif y1 < y0:
        turn = True
             
    if turn:
        line[0] = x1
        line[1] = y1
        line[2] = x0
        line[3] = y0
  

@jit(nopython=True)   
def length(line):
    x0,y0,x1,y1 = line
    dx = x1-x0
    dy = y1-y0
    return hypot(dx,dy) 


def isEven(angle):
    '''
    return whether lines is either horizontal or vertical
    '''
    return angle<0.1 or angle>1.4


def dxdy(line):
    '''
    return normalised ascent vector
    '''
    x0,y0,x1,y1 = line
    dx = float(x1-x0)
    dy = float(y1-y0)
    f = hypot(dx,dy)
    return dx/f, dy/f

def ascent(line):
    x0,y0,x1,y1 = line
    try:
        return min(float(y1-y0) / (x1-x0),1e10)
    except ZeroDivisionError:
        return 1e10


def angle(line):
    x0,y0,x1,y1 = line
    try:
        return atan2(float(y1)-y0, float(x1)-x0)
    except ZeroDivisionError:
        if y1 > y0:
            return - pi
        return pi

@jit(nopython=True)   
def angle2(line1, line2):
    #return angle between two lines
    #from http://stackoverflow.com/questions/13226038/calculating-angle-between-two-lines-in-python
    x0,y0,x1,y1 = line1
    x1-=x0
    y1-=y0
    x0,y0,x2,y2 = line2
    x2-=x0
    y2-=y0    
    inner_product = x1*x2 + y1*y2
    len1 = hypot(x1, y1)
    len2 = hypot(x2, y2)
    a = inner_product/(len1*len2)
    return copysign(acos(min(1,max(a,-1))), y2)


def fromAttr(mid, ang, dist):
    '''
    create from middle, angle and distance
    '''
    mx,my = mid
    dx = cos(ang)*dist*0.5
    dy = sin(ang)*dist*0.5
    return mx-dx,my-dy,mx+dx,my+dy


def fromAttr2(start, ang, dist):
    '''
    create from start, angle and distance
    '''
    sx,sy = start
    dx = cos(ang)*dist
    dy = sin(ang)*dist
    return sx,sy,sx+dx,sy+dy
    
    
def fromFn(ascent,offs, length=1, px=0):
    py = px*ascent + offs
    dx = length
    dy = ascent*length
    if length != 1:
        #normalize
        l = length / (dx**2 + dy**2)**0.5
        dx*=l
        dy*=l
    return px,py,px+dx,py+dy


def toFn(line):
    x0,y0,x1,y1 = line
    m = ascent(line)
    offs = y0-m*x0
    return m,offs, length(line)
    

def merge(l1, l2):
    '''
    merge 2 lines together
    '''
    x1,y1,x2,y2 = l1
    xx1,yy1,xx2,yy2 = l2
    
    comb = ( (x1,y1,xx1,yy1),
             (x1,y1,xx2,yy2),
             (x2,y2,xx1,yy1),
             (x2,y2,xx2,yy2) )
    
    d = [length(c) for c in comb]
    i = argmax(d)
    
    dist = d[i]
    mid = middle(comb[i])

    a = (angle(l1) + angle(l2)) * 0.5
    return fromAttr(mid, a, dist)


def resize(line, factor):
    '''
    factor: relative length (1->no change, 2-> double, 0.5:half)
    '''
    a = angle(line)
    mx,my = middle(line)
    d = length(line)*factor*0.5
    dx = cos(a)*d
    dy = sin(a)*d
    return mx-dx,my-dy,mx+dx,my+dy
    
    
@jit(nopython=True)   
def middle(line):    
    x0,y0,x1,y1 = line
    return (x0+x1)/2, (y0+y1)/2

 
def rotate(line, angle):
    x0,y0,x1,y1 = line
    p = rotatePolygon(array(((x0,y0),(x1,y1))),angle)
    return [p[0,0], p[0,1],p[1,0],p[1,1]]


def distance(line, point):
    '''
    infinite line to point or line to line distance
    is point is given as line - use middle point of that liune
    '''
    x0,y0,x1,y1 = line
    try:
        p1,p2 = point
    except ValueError:
        #line is given instead of point
        p1,p2 = middle(point)
    n1 = ascent(line)
    n2 = -1
    n0 = y0 - n1*x0
    return abs(n1*p1 + n2*p2 + n0 ) / (n1**2 + n2**2)**0.5


def segmentDistance(line,point):
    dx,dy = distanceVector(line, point, ignoreEndpoints=False)
    return (dx**2+dy**2)**0.5


@jit(nopython=True)   
def distanceVector(line, point, ignoreEndpoints=True):
    x0,y0,x1,y1 = line
    px,py = point
    line_magnitude =  length(line)
    if line_magnitude == 0:
        return px-x0,py-y0
    u = ((px - x0) * (x1 - x0) +
         (py - y0) * (y1 - y0)) \
         / (line_magnitude ** 2)
    # closest point does not fall within the line segment, 
    # take the shorter distance to an endpoint
    if u < 0.00001 or u > 1:
        if ignoreEndpoints:
            return 0,0
        ix = length((px,py,x0,y0))
        iy = length((px,py,x1,y1))
        if ix > iy:
            
            ix, iy = x1,y1
        else:
            ix,iy = x0,y0
    else:
        ix = x0 + u * (x1 - x0)
        iy = y0 + u * (y1 - y0)
          
    return ix-px, iy-py


def segmentIntersection(line1, line2):
    i = intersection(line1, line2)
    if i is None:
        return None

    if (pointIsBetween(line1[0:2],line1[2:],i) 
        and pointIsBetween(line2[0:2],line2[2:],i) ):
        return i
    return None




def pointIsBetween(startP,endP,p):
    return distancePoint(startP,p) + distancePoint(p,endP) - distancePoint(startP,endP) <1e-6

def distancePoint(p1,p2):
    return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5
    

@jit(nopython=True)   
def intersection(line1, line2):
    """
    Return the coordinates of a point of intersection given two lines.
    Return None if the lines are parallel, but non-colli_near.
    Return an arbitrary point of intersection if the lines are colli_near.

    Parameters:
    line1 and line2: lines given by 4 points (x0,y0,x1,y1).
    """
    x1,y1, x2,y2 = line1
    u1,v1, u2,v2 = line2
    (a,b), (c,d) = (x2-x1, u1-u2), (y2-y1, v1-v2)
    e, f = u1-x1, v1-y1
    # Solve ((a,b), (c,d)) * (t,s) = (e,f)
    denom = float(a*d - b*c)
    if _near(denom, 0):
        # parallel
        # If colli_near, the equation is solvable with t = 0.
        # When t=0, s would have to equal e/b and f/d
        if b == 0 or d == 0:
            return None
        if _near(float(e)/b, float(f)/d):
            # colli_near
            px = x1
            py = y1
        else:
            return None
    else:
        t = (e*d - b*f)/denom
        # s = (a*f - e*c)/denom
        px = x1 + t*(x2-x1)
        py = y1 + t*(y2-y1)
    return px, py

@jit(nopython=True)   
def _near(a, b, rtol=1e-5, atol=1e-8):
    return abs(a - b) < (atol + rtol * abs(b))









def translate(line, ascent, offs=0):
    '''
    offs -> shifts parallel to line
    ascent -> rotate line
    '''
    #TODO: why do I have thuis factor here?
    ascent*=-2
    offs*=-2
     
    l0 = length(line)

    #change relative to line:         
    t0 = offs#-h+offs
    t1 = l0*ascent+offs
    return translate2P(line,t0,t1)


def translate2P(line,t0,t1):
    a = angle(line)

    #change in x and y:
    dx0 = sin(a)*t0
    dx1 = sin(a)*t1
    dy0 = cos(a)*t0
    dy1 = cos(a)*t1
    return line[0]+dx0, line[1]+dy0, line[2]+dx1, line[3]+dy1
   

#REMOVE?
def split(line, lines):
    '''
    split <line> into multiple sublines
    using intersection with <lines> 
    '''
    out = empty((len(lines)+1,4))

    p1 = line[:2]
    for n, l2 in enumerate(lines):
        p2 = intersection(line,l2)
        out[n][:2]=p1
        out[n][2:]=p2
        p1 = p2
    out[n+1][:2]=p2
    out[n+1][2:]=line[2:]
    return out
        

def splitN(line,n):
    '''
    split a line n times
    returns n sublines
    '''
    x0,y0,x1,y1 = line

    out = empty((n,4), dtype=type(line[0]))
    px,py = x0,y0
    dx = (float(x1)-x0) / n
    dy = (float(y1)-y0) / n
    #print dx,dy,777777777777777
    
    for i in xrange(n):
        o = out[i]
        o[0] = px
        o[1] = py
        px += dx
        py +=dy
        o[2] = px
        o[3] = py        
    return out


if __name__ == '__main__':
    import pylab as plt


#     l0 = [2625,  526, 2625, 1441]
#     l1 = [2178 , 288 ,2178 ,3021]
#     print middle(l1)
#     print 666, distanceVector(l0, middle(l1), ignoreEndpoints=False)

    l0 = [0.,0.5,0.,1.]
     
    l1 = [0.5,0.,1.5,0.]
    

    
    
    print angle2(l0,l1),888
    print intersection(l0,l1)


    plt.plot((l0[0],l0[2]),(l0[1],l0[3]),'r')                 
    plt.plot((l1[0],l1[2]),(l1[1],l1[3]),'g')
    plt.show() 

    
    ll = [[0.1,1,0.1,0],[0.3,1,0.3,0]]
    print splitN(l0,3)



#     
    l0 = [4674 , 233 ,4651, 2892]
    a = -0.00284855546826 
    o = 5.5832401565
#     
    l1= translate(l0, a, o)
    plt.plot((l0[0],l0[2]),(l0[1],l0[3]),'r')                 
    plt.plot((l1[0],l1[2]),(l1[1],l1[3]),'g')
    plt.show()  
#(4650.9517093206787, 540593.62650955946, 4673.952276003728, 537934.62651446124) 
    p0 = [0.5,0.5]
    print length(l0)
    print distanceVector(l0, p0, ignoreEndpoints=True)