from numba import jit


def similarity1DdiffShapedArrays(arr1, arr2, normalize=False):
    '''
    compare two strictly monotonous increasing 1d arrays 
    of same or different size 
    return a similarity index-> 0=identical
    '''
    #assign longer and shorter here, because jit cannot do it
    if len(arr1) < len(arr2):
        arr1,arr2 = arr2,arr1
    if not len(arr2):
        out = sum(arr1)
    else:
        out = _calc(arr1, arr2)

    if normalize:
        if not len(arr2):
            mn = arr1[0]
            mx = arr1[-1]
        else:
            mn = min(arr1[0],arr2[0])        
            mx = max(arr1[-1],arr2[-1])
        out = float(out) / (mx-mn)
        
    return out
   
    
@jit(nopython=True)
def _calc(l,s):
    #l...longer array, s... shorter array
    i = 0 #index of l
    j = 0 #index of s
    v = s[0]
    sim = 0
    ls = len(s)-1
    ll = len(l)-1
    #ll = len(l)-1
    #walk through both arrays adding the minimum difference to 'sim'
    while True:
        d0 = abs(l[i]- v)
        d1 = abs(l[i+1] -v)
        sim += min(d0,d1)
        if d1<d0:
            i += 1
            if i == ll:
                break
        else:
            j += 1
            if j == ls:
                break            
            v = s[j]
    return sim




if __name__ == '__main__':
    import numpy as np

    arr1 = np.array([1.06257158,   2.03065364,   3.00055033,   4.02509933,
         5.04263119,   6.02609311,   7.0613511 ,   8.01943069,
         9.0996045 ,  10.07413368 ])
    arr2 = np.array([  2.03140113,   3.0375256 ,   4.04365008,   5.04977456,
         6.05589903,   7.06202351,   8.06814798,   9.07427246,
        10.08039693,  11.08652141])
    print similarity1DdiffShapedArrays(arr1, arr2)
    arr2 = np.array([  1.98539463,   3.00056414,   4.01573365,   5.03090316,
         6.04607267,   7.06124218,   8.07641169,   9.0915812 ,
        10.10675071,  11.12192022])
    print similarity1DdiffShapedArrays(arr1, arr2)
    print 555


    arr1 = np.array([ 1.54661319,  3.83296723,  6.11932126,  8.40567529])
    print similarity1DdiffShapedArrays(arr1, arr2)





#     #case 1: identical arrays
#     arr1 = np.array([1,2,3,4,5,5.1,6,7,8,9,10])
#     arr2 = arr1
#     assert np.isclose(similarity1DdiffShapedArrays(arr1, arr2), 0)
# 
#     #case 1: smaller array is just missing values: 
#     arr1 = np.array([1,2,3,4,5,6,7,8,9,10])
#     arr2 = np.array([    3,4,5,6,7,8,9])
#     assert np.isclose(similarity1DdiffShapedArrays(arr1, arr2), 1)
#         
#     #case 2: case 1 + smaller array has one slightly diff. one: 
#     arr1 = np.array([1,2,3,4,5,6,     7,8,9,10])
#     arr2 = np.array([    3,4,5,6,6.1, 7,8,9])
#     assert np.isclose(similarity1DdiffShapedArrays(arr1, arr2),1.1)
# 
#     #case 2: case 2 + longer array has extra values in between: 
#     arr1 = np.array([1,2,3,4,5,  5.5,  6,  7,7.7, 8,9,10])
#     arr2 = np.array([    3,4,5,6,      6.1,7,     8,9])
#     assert np.isclose(similarity1DdiffShapedArrays(arr1, arr2), 1.6)
# 
#     #case 4: 2 random arrays or different size
#     arr1 = np.sort(np.random.rand(1000))
#     arr2 = np.sort(np.random.rand(800))
#     print similarity1DdiffShapedArrays(arr1, arr2)
# 
#     #case 4: case 3 bit higher values - return similar result
#         #through normalize=True
#     arr1 = np.sort(np.random.rand(1000)*1000)
#     arr2 = np.sort(np.random.rand(800)*1000)
#     print similarity1DdiffShapedArrays(arr1, arr2, normalize=True)
