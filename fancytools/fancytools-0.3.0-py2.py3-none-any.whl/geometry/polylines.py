'''
general functions for polylines =
    [ [ [x0,y0],[x1,y1], ... ], #first polyline
      [ [x0,y0],[x1,y1], ... ], #second
      ...
    ]
'''

import numpy as np
from numpy.linalg import norm

from scipy.interpolate import UnivariateSpline
from scipy.stats import linregress

from fancytools.math import line
from fancytools.math.angleDiff import angleDiff


def lengths(polyline):
    '''
    returns the length of all polylines
    '''
    return norm(np.diff(polyline, axis=0), axis=1)


def _sort(c, firstI, lastI):
    # sort given polyline giving
    # indices of first and last point
    l = len(c)
    indices = np.zeros(l, dtype=np.uint16)
    remaining = np.ones(l, dtype=bool)
    remaining[firstI] = False
    remaining[lastI] = False
    indices[0] = firstI
    indices[-1] = lastI

    nextI = firstI
    for m in xrange(1, l-1):
        p = c[nextI]
        min_dist = 1e6
        for j, other in enumerate(c):
            if remaining[j]:
                dist = norm(p[0]-other[0])
                if dist < min_dist:
                    nextI = j
                    min_dist = dist

        indices[m] = nextI
        remaining[nextI] = False
    return indices


def sort(polylines):
    '''
    sort points within polyline
    p0-p1-p2...
    '''
    for n, c in enumerate(polylines):
        l = len(c)
        if l > 2:
            # DEFINE FIRST AND LAST INDEX A THOSE TWO POINTS THAT
            # HAVE THE BIGGEST DIFFERENCE FROM A MIDDLE:
            mid = c.mean(axis=0)

            distV = (c-mid)
            dists = norm(distV, axis=-1)

            firstI = np.argmax(dists)
            sign = np.sign(distV[firstI])

            dd = np.logical_or(np.sign(distV[:,0]) != sign[0],
                               np.sign(distV[:, 1]) != sign[1] )

            dists[~dd] = 0
            lastI = np.argmax(dists)

            ind = _sort(c, firstI, lastI)
            c = c[ind]
            polylines[n] = c


def filter(polylines, min_len=20):
    '''
    filter polylines shorter than given min length
    '''
    filtered = []
    for n in xrange(len(polylines)-1,-1,-1): 
        if lengths(polylines[n]).sum() < min_len:
            filtered.append(polylines.pop(n))
    return filtered


def separate(polylines, f_mx_dist=2, mn_group_len=4): 
    '''
    split polylines wherever crinkles are found
    '''
    s = []

    for n in xrange(len(polylines)-1, -1, -1):
        c = polylines[n]
        separated = False
        start = 0

        for m in xrange(mn_group_len, len(c)-1):
            if m-start < mn_group_len:
                continue
            m+=1
            group = c[m-mn_group_len:m]

            x,y = group[:,0], group[:,1]
            asc, offs, _, _, _ = linregress(x,y)
            yfit = asc*x+offs

            #check whether next point would fit in:
            p1 = c[m]
            l = (x[0], yfit[0], p1[-1], asc*p1[-1]+offs)
            std = np.mean([line.distance(l,g) for g in group])
            dist = line.distance(l, p1)

            if dist > 2 and dist > f_mx_dist*std:
                separated = True
                s.append(c[start:m-1])
                start = m-1

        if separated:
            if len(c)-start >= 2:
                s.append(c[start:])
            polylines.pop(n)

    polylines.extend(s)

    return polylines


def merge(polylines, mx_dist=4):
    '''
    point by line segment comparison
    merge polylines if points are close
    '''
    l = len(polylines)
    to_remove = set()
    for n in xrange(l-1, -1, -1):
        if n not in to_remove:
            c = polylines[n]
            for p0, p1 in zip(c[:-1], c[1:]):
                #create a line from any subsegment:
                l0 = p0[0], p0[1], p1[0], p1[1]

                #for every other polyline:
                for m in xrange(l-1, -1, -1):
                    if m not in to_remove:
                        if n == m:
                            continue
                        remove = False
                        cc = polylines[m]
                        ind = np.zeros(shape=cc.shape[0], dtype=bool)

                        #for every point p in this polyline:
                        for o in xrange(len(cc)-1, -1, -1):
                            p = cc[o]

                            if line.segmentDistance(l0, p) < mx_dist:
                                remove = True
                                ind[o] = True

                        if remove:
                            polylines[n] = np.append(c, cc[ind], axis=0)
                            ind= ~ind
                            s = ind.sum()
                            if s < 2:
                                to_remove.add(m)
                            else:
                                polylines[m] = cc[ind]

    to_remove = list(to_remove)
    to_remove.sort()
    to_remove.reverse()
    for i in to_remove:
        polylines.pop(i)

              
#TODO: get direction d0,d1 by meas dists
def _connect(c0,c1, d0,d1): 
    #connect both polylines is they have a similar orientation
    #d0, d1: which position if connected
    #0-> start pos
    #1-> end position
    
    #sort positions as follows:
    #  c0        c1
    #p0---p1   p2--p3
    if d0 == 0:
        p0 = c0[-1]
        p1 = c0[0]
    else:
        p0 = c0[0]
        p1 = c0[-1]
    if d1 == 0:
        p2 = c1[0]
        p3 = c1[-1]
    else:
        p2 = c1[-1]
        p3 = c1[0]        

    a0 = line.angle((p0[0],p0[1],p1[0],p1[1]))
    a1 = line.angle((p2[0],p2[1],p3[0],p3[1]))
    diff =  angleDiff(a0,a1)

    is_same = False
    #CRITERION 1: similar angle
    if abs(diff) < 0.3:
        #CRITERION 2: all points in a row
        if norm(p0-p2)<norm(p0-p3):
            is_same = True
            #create connected polyline:
            if d0==0:
                if d1==0:
                    c0 = np.insert(c0,0,c1[::-1],axis=0)
                else:
                    c0 = np.insert(c0,0,c1,axis=0)
            else:
                if d1==0:
                    c0 = np.append(c0,c1,axis=0)
                else:
                    c0 = np.append(c0,c1[::-1],axis=0)
            
    return is_same, c0



def connect(polylines, max_dist=10):
    '''
    connect polylines that are close and have a similar orientation
     o---o  <->  o---o  ==> o----o--o----o
    TODO: max_dist as faction of cell size
    '''
    ll = len(polylines)
    remove = []
    for n in xrange(ll-1,-1,-1):
        c = polylines[n]
        if len(c)>1:
            for d0,p0 in enumerate((c[0,0],c[-1,0])):            
                for m in xrange(len(polylines)-1,-1,-1):
                    #combine all x all polylines
                    if n==m:
                        continue
                    cc = polylines[m]

                    for d1,p1 in enumerate((cc[0,0],cc[-1,0])):
                        # for end points of other polylines:
                        # measure closest distance for current polyline
                        ndist = norm(p0-p1)
                        if ndist < max_dist:
                            is_same, c =  _connect(c,cc, d0,d1)
                            if is_same:
                                if m not in remove:
                                    remove.append(m)
                                polylines[n] = c
                                break
    # remove those which are already in connected to other polyline:
    remove.sort()
    remove.reverse()
    for r in remove:
        polylines.pop(r)


def smooth(polylines):
    '''
    smooth every polyline using spline interpolation
    '''
    for c in polylines:
        if len(c)<9:
            # smoothing wouldn't make sense here
            continue
        x = c[:, 0]
        y = c[:, 1]

        t = np.arange(x.shape[0], dtype=float)
        t /= t[-1]
        x = UnivariateSpline(t, x)(t)
        y = UnivariateSpline(t, y)(t)
        c[:, 0] = x
        c[:, 1] = y


def plot(polylines, img=None):
    import pylab as plt
    plt.figure(1)

    for n, c in enumerate(polylines):
        x = c[:, 0]
        y = c[:, 1]
        plt.plot(x, y, linewidth=3)
        plt.text(x[-1], y[-1], str(n+1))
    if not img is None:
        plt.imshow(img, interpolation='none')
        plt.set_cmap('gray')
    plt.show()



if __name__ == '__main__':
    #TODO
    pass