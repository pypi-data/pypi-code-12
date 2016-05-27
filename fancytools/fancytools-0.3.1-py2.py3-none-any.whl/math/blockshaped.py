
#code taken from 
#http://stackoverflow.com/questions/16873441/form-a-big-2d-array-from-multiple-smaller-2d-arrays/16873755#16873755

import numpy as np


def blockshaped(arr, nrows, ncols):
    """
    Return an new array of shape (n, nrows, ncols) where
    n * nrows * ncols = arr.size

    If arr is a 2D array, the returned array looks like n subblocks with
    each subblock preserving the "physical" layout of arr.
    """
    h, w = arr.shape
    return (arr.reshape(h//nrows, nrows, -1, ncols)
               .swapaxes(1,2)
               .reshape(-1, nrows, ncols))


def unblockshaped(arr, h, w):
    """
    Return an new array of shape (h, w) where
    h * w = arr.size

    If arr is of shape (n, nrows, ncols), n sublocks of shape (nrows, ncols),
    then the returned array preserves the "physical" layout of the sublocks.
    """
    n, nrows, ncols = arr.shape
    return (arr.reshape(h//nrows, -1, nrows, ncols)
               .swapaxes(1,2)
               .reshape(h, w))


#TODO: better reimplement both methods above
# to avoid all these reshaping
def into2dBlocks(arr, n0, n1):
    '''
    similar to blockshaped
    but splits an array into n0*n1 blocks
    '''
    s0,s1 = arr.shape
    b = blockshaped(arr, s0/n0, s1/n1)
    return b.reshape(n0,n1,*b.shape[1:] )


def from2dBlocks(arr):
    '''
    input needs to be 4d array (2d array of 2d arrays)
    '''
    s = arr.shape
    s0,s1 = s[0]*s[2],s[1]*s[3]
    return unblockshaped(arr.reshape(s[0]*s[1], s[2], s[3]), s0,s1)

if __name__ == '__main__':
    

    c = np.arange(24).reshape((4,6))
    print(c)
    # [[ 0  1  2  3  4  5]
    #  [ 6  7  8  9 10 11]
    #  [12 13 14 15 16 17]
    #  [18 19 20 21 22 23]]
    
    bl = into2dBlocks(c,2,3)
    print(bl.shape)
    bl[0,0]=0
    c = from2dBlocks(bl)
    print c
    # (2L, 3L, 2L, 2L)
    bl = blockshaped(c, 2, 3)
    bl[0]=0
    print (bl)
    print 22, c
    
    # [[[ 0  1  2]
    #   [ 6  7  8]]
    
    #  [[ 3  4  5]
    #   [ 9 10 11]]
    
    #  [[12 13 14]
    #   [18 19 20]]
    
    #  [[15 16 17]
    #   [21 22 23]]]
    
    print(unblockshaped(blockshaped(c, 2, 3), 4, 6))
    # [[ 0  1  2  3  4  5]
    #  [ 6  7  8  9 10 11]
    #  [12 13 14 15 16 17]
    #  [18 19 20 21 22 23]]