import numpy as np
from scipy.ndimage.filters import median_filter
from scipy.ndimage.measurements import label

from imgProcessor.cameraCalibration.NoiseLevelFunction import oneImageNLF


def removeSingleTimeEvents(images, noise_level_function=None, 
                           processAll=True, return_ste_indices=False, 
                           count=False, copy=True, n_stdDev=1.5):
    '''
    need at least 2 images as np.ndarray or list of 2d-np.arrays
    showing the same motif taken under identical conditions
    
    processAll = [False, True] -> False: remove only STE from first image
    count =      [False, True] -> whether to count all found STE
    copy  =      [False, True] -> True: create a new array, False: modify existing
    
    returns: cleaned images and indices of changed positions
    '''
    l = len(images)
    if noise_level_function is None:
        img2 = None
        if l>1:
            img2=images[1]
        noise_level_function,blurred = oneImageNLF(images[0], img2)
    if l == 1:
        clean = blurred
    else:
        clean = np.min(images,axis=0)

    #STE if difference to averaged image > 1.5 * noise level:
    threshold = noise_level_function(clean) * n_stdDev
    ste_indices = []
    number_of_STE = []
    
    if copy:
        images = [i.copy() for i in images]
    
    for im in images:
        i = abs(im - clean) > threshold
        #clean:
        im[i] = clean[i]
        if return_ste_indices or count:
            #filter noise:
            i = median_filter(i, size=3)
            ste_indices.append(i)
            if count:
                number_of_STE.append(label(i)[1])
        #STOP AFTER FIRST IMAGE?
        if not processAll:
            break
    ste_indices = np.array(ste_indices)
    return images, ste_indices, number_of_STE