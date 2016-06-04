import numpy as np
from numba import jit
from scipy.misc import imresize
from interpolate.interpolate2dStructuredIDW import interpolate2dStructuredIDW



DIRECT_NEIGHBOURS = (-1,0),(1,0), (0,1), (0,-1)
OPPOSITE_DIR = (1,0,3,2,4)#index of opposite neighbour + plus 1 extra number for initial val


def closestConnectedDistance(target, walls=None, fast=False, 
                             max_len_border_line=500,
                             max_n_path=100,
                             concentrate_every_n_pixel=1):
    '''
    returns an array with contains the closest distance from every pixel
    the next position where target == 1

    [walls] binary 2darray - e.g. walls in a labyrinth that have to be surrounded in order to get to the target
     
    [target] binary 2darray - positions given by 1
    
    [fast] is true travelled distance = number of step of region growth method
    
    [concentrate_every_n_pixel] often the distance of neighbour pixels is similar
            to speed up calculation set this value to e.g. 3 to calculate only 
            the distance for every 3. pixel and interpolate in between
    
        recommended are values up to 3-5
    
    [max_len_border_line]
    this function calculates distances travelled using region growth
    e.g.
    
    0123
    1123
    2223
    3333
    
    the last steps (e.g. for all steps 3 border_line=7) are stored in an array of limited
    length defined in 'max_len_border_line'
    
    [max_n_path]
    how many paths are possible between every pixel and the target
    only needed if fast==False
    '''
    c = concentrate_every_n_pixel    
    assert c >=1
    if walls is None:
        walls = np.zeros_like(target, dtype=bool)
    s = target.shape
    out = np.full( (s[0]/c,s[1]/c), -1, dtype=np.int16)
    #temporary arrays:
    growth = np.zeros_like(target, dtype=np.uint16)
    res = np.empty(shape=3,dtype=np.uint16)

    steps = np.empty(shape=(max_len_border_line,2),dtype=np.uint16)
    new_steps = np.empty(shape=(max_len_border_line,2),dtype=np.uint16)

    if fast:
        max_n_path = 0
    #in order to find shortest path between every pixel...
        #which path works
    last_n = np.zeros(max_n_path, dtype=np.uint8)
        #for every path how often the direction was changed 
    n_dir_changes = np.zeros(max_n_path, dtype=np.uint16)
        #x,y value of the position of the current path
    cur_position = np.empty((max_n_path,2), dtype=np.uint16)
    active_paths = np.zeros(max_n_path, dtype=bool)

    #run calculation:
    _calc(growth, out, walls, target, fast, steps, new_steps, 
          res, concentrate_every_n_pixel, last_n, n_dir_changes, cur_position,
          active_paths)
    
    if c > 1:
        #if concentrate_every_n_pixel > 1
        #the resized output array
        #will have wrong values close to the wall
        #therefore substitute all wall value (-1)
        #with an average of their closest neighbours
        interpolate2dStructuredIDW(out, out==-1)
        out = imresize(out, s, interp='bilinear')
        #set wall:
        out[walls]=-1
        #out[target]=-1
    return out
    
  

@jit(nopython=True)
def _calc(growth, dists, walls, target, fast, steps, new_steps, res, 
          concentrate_every_n_pixel, last_n, n_dir_changes, cur_position,
          active_paths):
    s0,s1 = walls.shape

    #for every pixel:
    for ii,i in enumerate(xrange(0,s0,concentrate_every_n_pixel)):
        for jj,j in enumerate(xrange(0,s1,concentrate_every_n_pixel)): 
            if walls[i,j]:
                continue

            #get the number of steps needed:
            _grow(growth, walls, target, i,j, steps, new_steps, res)
            
            if res[0]:
                #only of path to target could be found:
                #dists[ii,jj] = -1
                if fast:
                    #approximate travelled distance as number of growth steps taken
                    #this is fast but will return a too short path
                    dists[ii,jj] = growth[res[1],res[2]]
                else:
                    #calculate actual distance travelled and update dists:
                    dists[ii,jj] = _findPath(growth, res, last_n, n_dir_changes, 
                                             cur_position, active_paths)

     
 
@jit(nopython=True)
def _findPath(growth, res, last_n, n_dir_changes, cur_position, active_paths):
    #the number of steps (horizontal, vertical, diagonal)
    #is not necessarily == travelled distance
    #a good approximation is to count all diagonal moves
    #and add those to the distance as *sqrt(2)

    i = res[1]
    j = res[2]
    max_n_path = len(active_paths)

    step0 = growth[i,j]

    #prepare first step:
    n_paths = 1
    cur_position[0,0]=i
    cur_position[0,1]=j
    last_n[0] = 4 
    n_dir_changes[0]=0
    active_paths[0] = True

    s0,s1 = growth.shape
    for s in xrange(step0-1,0,-1):
        p = 0    
        while p < n_paths:
        #for p in xrange(n_paths):
            #try out all different possibilities from 
            #a pixel to the target, taking only
            #direct neighbours 
            
            if active_paths[p]:
                i,j = cur_position[p]
                
                continue_path = True
                for n,(ii,jj) in enumerate(DIRECT_NEIGHBOURS): 
                    #don't go back
                    ln = last_n[p]
                    #print ln, (1,0,3,2,4)[ln]
                    #if  ln == OPPOSITE_DIR[ln]:
                   #     continue
                        
                    #check out all neighbours
                    pi = i+ii
                    pj = j+jj
                    #if in image:
                    if 0<=pi<s0 and 0<=pj<s1:
                        #print growth[pi,pj], s,999
                        if growth[pi,pj] == s: 
                            #print 66666
                             
                            #growth[pi,pj] = -1 # don't go somewhere twice
                            
                            if continue_path:
                                #print 77777
                                cur_position[p,0] = pi
                                cur_position[p,1] = pj
                                
                                if n != ln:
                                    #direction changed
                                    n_dir_changes[p] += 1
                                    
                                    last_n[p] = n
                                continue_path = False
                        
                            elif n_paths < max_n_path:
                                #print 888
                                #prepare new path:
                                #print n_dir_changes[p]
                                if  n_dir_changes[p] == 1:
                                    #print 222222222
                                #if n != ln:

                                    n_dir_changes[n_paths] = n_dir_changes[p] + 1
                                else:
                                    n_dir_changes[n_paths] = n_dir_changes[p]
                                last_n[n_paths] = n
                                cur_position[n_paths,0] = pi
                                cur_position[n_paths,1] = pj 
                                active_paths[n_paths] = True
#                                 if n_paths >= max_n_path-1:
#                                     #array is full - have to stop
#                                     stop = True
#                                     break
                                n_paths += 1
                    #print n           

                    
                if continue_path:  
                    #no new step found: 
                    #print 999999999 
                    active_paths[p] = False
            p += 1
            #print p, n_paths

    #get shortest path:
    ndirchanges = n_dir_changes[0]
    #print 7777777777777777777
    for n in xrange(1,n_paths):
        #print active_paths[n]
        if active_paths[n]:
            
            print n_dir_changes[n],n,888
            val = n_dir_changes[n]
            if val < ndirchanges:
                ndirchanges = val
    if n_paths > 1:
        #print ndirchanges
    #ndirchanges = n_dir_changes[:n_paths].min()#[active_paths[:n_paths]]
        print ndirchanges, n_paths
#     if n_paths > 1:
#         print 66666666666, ndirchanges
#         for nn in n_dir_changes[:n_paths]:
#             print nn
        #print ndirchanges, n_paths
    ndiags = 0.5*(ndirchanges-1)

    return 1 + step0 +  2**0.5*(ndiags)
    
    
@jit(nopython=True)
def _grow(growth, walls, target, i,j, steps, new_steps, res):
    #fills [res] with [distance to next position where target == 1, 
    #                  x coord.,
    #                  y coord. of that position in target]
    # using region growth
    
    #i,j -> pixel position
    # growth -> a work array, needed to measure the distance
    # steps, new_steps -> current and last positions of the region growth steps
        #using this instead of looking for the right step position in [growth]
        #should speed up the process

    #clean array:
    growth[:] = 0

    if target[i,j]:
        #pixel is in target
        res[0]=1
        res[1]=i
        res[2]=j
        return
    
    step = 1
    s0,s1 = growth.shape
    step_len = 1
    new_step_ind = 0
    
    steps[new_step_ind,0] = i
    steps[new_step_ind,1] = j
    growth[i,j]=1

    while True:
        for n in xrange(step_len):
            i,j = steps[n]
            for ii,jj in  DIRECT_NEIGHBOURS:
                    pi = i+ii
                    pj = j+jj
                    
                    #if in image:
                    if 0<=pi<s0 and 0<=pj<s1:
                        #is growth array is empty and there are no walls:
                            #fill growth with current step
                        if growth[pi,pj] == 0 and not walls[pi,pj]:
                            growth[pi,pj] = step
                            if target[pi,pj]:
                                #found destination
                                res[0]=1
                                res[1]=pi
                                res[2]=pj
                                return
                            
                            new_steps[new_step_ind,0]=pi
                            new_steps[new_step_ind,1]=pj                            
                            new_step_ind += 1

        if new_step_ind == 0:
            #couldn't populate any more because growth is full
                #and all possible steps are gone
            res[0]=0
            return
        
        step += 1
        steps,new_steps  = new_steps, steps
        step_len = new_step_ind
        new_step_ind = 0
      

  
if __name__ == '__main__':
    import pylab as plt

    
    size = (50,60)
#     walls =np.zeros(size, dtype=bool)
#     walls[10:30,20]=1
#     walls[40, 25:40]=1
#     walls[35, 5:45]=1
#     
#     target = np.zeros(size, dtype=bool)
#     target[10:30,40]=1

    walls =np.zeros(size, dtype=bool)


    walls[5:-5, 35]=1
    walls[35:-5, 20]=1
    walls[-5, 20:34]=1
    walls[35, 20:35]=1

    #draw diag:
    for i in xrange(10,20):
        walls[i,i]=1

    #walls[35, 5:45]=1
    
    target = np.zeros(size, dtype=bool)
    target[:,2]=1
    target[:,-2]=1

    dists = closestConnectedDistance(target, walls, 
                                     concentrate_every_n_pixel=1,fast=True)

    dists[target] = dists.max()
    plt.figure('Walls=Blue, Target=Red')
    
    plt.imshow(dists, interpolation='none')
    plt.colorbar()
  
    
    plt.show()
    

