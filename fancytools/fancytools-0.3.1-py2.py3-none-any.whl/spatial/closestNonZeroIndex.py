
import numpy as np
from numpy.linalg import norm



def closestNonZeroIndex(pt, arr, kSize=21):
    '''
    return the index closest to point [pt] in an array [arr]
    within a given kernel size [kSize] that is not zero
    '''
    assert kSize%2 ==1, 'need odd kernel size'

    hk = int(kSize/2)
    ipt = np.asarray(pt, dtype=int)
    #array slice of shape kSize around ipt:
    r = [slice(max(0,p-hk), 
                     min(s,p+hk+1)) for p,s in zip(ipt, arr.shape)]
    
    #sliced array:
    arrr = arr[tuple(r)]
    #all indices that are non zero:
    ind = np.transpose(np.nonzero(arrr))
    if not len(ind):
        #nothing found
        return None
    #pos of ipt within array slice:
    center = [p-s.start for p,s in zip(ipt, r)]
    ind -= center
    #index of minimum distance:
    m = np.argmin(norm(ind, axis=-1))
    return ipt + ind[m]



if __name__ == '__main__':
    from matplotlib import pyplot as plt
    import sys
    
    SIZE = 100
    NSEEDS = 100
    KERNELSIZE = 5

    #distance between pt and closest non-zero index must be smaller than...
    max_distance = 2**0.5 * (KERNELSIZE/2+1)

    #np.random.seed(1)
 
    arr = np.random.randint(0,100,(SIZE,SIZE))
    arr = (arr>95)#.astype(int)

    #[NSEEDS] random positions within the array:
    pos = np.transpose((np.random.rand(NSEEDS)*SIZE,
                        np.random.rand(NSEEDS)*SIZE))

    #FIND CLOSEST INDEX:
    closest = []    
    
    for p in pos:
        c = closestNonZeroIndex(p,arr, kSize=KERNELSIZE)
        if c is  None:
            c = [np.nan, np.nan]
        else:
            #TEST 1: closest index is not at a zero value
            assert arr[tuple(c)] != 0
            #TEST 2: distance between pt and closest is smaller than max_distance:
            assert norm(p-c) <= max_distance
        closest.append(c)
    closest = np.array(closest)


    if 'no_window' not in sys.argv:
        #PLOT:
        plt.figure('green: rand. seeds, yellow: vector to closest red')
        plt.imshow(arr.T, interpolation='nearest')
        plt.scatter(pos[:,0], pos[:,1], color='g')
        for p,c in zip(pos,closest):
            plt.plot((p[0],c[0]),(p[1],c[1]), color='y') 
        plt.show()
