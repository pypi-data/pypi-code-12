
# 
#     @staticmethod     
#     @jit(nopython=True)
#     def _closestConnectedDistance(bbdists, busbars, ksize=50):
#         #fill bbdists array with closest direct distance to next busbar
#         #within a given kernel size
#         s0,s1 = busbars.shape
#         min_dist0 = 2*ksize
#         for i in xrange(s0):
#             for j in xrange(s1): 
#                 min_dist = min_dist0



import numpy as np
from numba import jit


def closestConnectedDistance(target,walls=None, ksize=30):
    '''
    return an array with contains the closest distance to the next positive
    value given in arr  within a given kernel size
    '''
    if walls is None:
        walls = np.zeros_like(target, dtype=bool)
    dists = np.zeros_like(target, dtype=np.uint16)
    growth = np.zeros_like(target, dtype=np.uint16)
    _calc(growth, dists, walls, target,ksize)
    return dists
    

@jit(nopython=True)
def _calc(growth, dists, walls, target, ksize):
    s0,s1 = walls.shape
    mi,mj = growth.shape[0]/2, growth.shape[1]/2
    max_steps = 3*ksize

    #TODO: ensure even ksize

    for i in xrange(s0):
        for j in xrange(s1): 
            
            if walls[i,j]:
                continue
            
            growth[:]=0
            growth[i,j]=1
            
            for step in xrange(1,max_steps):
                found = _grow(growth, walls,#[i-mi:i+mi, j-mj:j+mj], 
                              target,step)#[i-mi:i+mi, j-mj:j+mj], step)
                if found:
                    break
            
            dists[i,j] =   step
                
@jit(nopython=True)
def _grow(growth, walls, target, step, i,j):
    s0,s1 = growth.shape
    while True:

        #start in middle
        #and move around every point 
        #much faster in iteration

        if growth[i,j] == step:
            for ii in xrange(-1,2):
                for jj in xrange(-1,2):
                    if ii==0 and jj==0:
                        continue
                    pi = i+ii
                    pj = j+jj
                    if growth[pi,pj] == 0 and not walls[pi,pj]:
                        growth[pi,pj] = step+1
                        if target[pi,pj]:
                            #found destination
                            return True
    return False         

# #BACKUP
# @jit(nopython=True)
# def _grow(growth, walls, target, step):
#     s0,s1 = growth.shape
#     for i in xrange(1,s0-1):
#         for j in xrange(1,s1-1):   
#             if growth[i,j] == step:
#                 for ii in xrange(-1,2):
#                     for jj in xrange(-1,2):
#                         if ii==0 and jj==0:
#                             continue
#                         pi = i+ii
#                         pj = j+jj
#                         if growth[pi,pj] == 0 and not walls[pi,pj]:
#                             growth[pi,pj] = step+1
#                             if target[pi,pj]:
#                                 #found destination
#                                 return True
#     return False




        
if __name__ == '__main__':

    import pylab as plt
    
    size = (50,50)
    walls =np.zeros(size, dtype=bool)
    walls[10:30,20]=1
    walls[25:40,40]=1
    
    target = np.zeros(size, dtype=bool)
    target[10:30,40]=1
    

    dists = closestConnectedDistance(walls, target)
    plt.figure('dists')
    plt.imshow(dists)
    plt.colorbar()
    plt.figure('walls')
    plt.imshow(walls)
    plt.figure('target')
    plt.imshow(target)    
    
    plt.show()
    

