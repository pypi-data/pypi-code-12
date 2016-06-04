#!/usr/local/bin/python2.7
# encoding: utf-8
import numpy as np

from imgProcessor.imgIO import imread
from imgProcessor.transformations import transpose
from imgProcessor.cameraCalibration.NoiseLevelFunction import oneImageNLF
from imgProcessor.SingleTimeEffectDetection import SingleTimeEffectDetection






#TODO: substitute STE removal code with right STE removal class

def zDenoise(images, STEremoval=True, copy=True, 
             noise_level_function=None,nStd=2.5):
    '''
    Remove single time effects and average in z-direction
    Take at least 2 image
    ----
    only grayscale images at the moment
    ----
    returns z_denoised, removed_indices

    '''
    l = float(len(images))
    if not STEremoval:
        #NP.MEAN WITHOUT REEDING ONLY ONE IMAGE AT THE TIME
        #if source_was_str:
        i0 = imread(images[0])
        out = i0 / l
        for i in images[1:]:
            out += imread(i) / l
        return out, None
    
    #STE REMOVAL#
    ste = SingleTimeEffectDetection(images, nStd=4, 
                            noise_level_function=self.noise_level_function)
    
    
        #READ FIRST 3 IMAGES
    for n,i in enumerate(images[:2]):
        if isinstance(i, basestring):
            images[n] = transpose(imread(i))
    
    noSTE = np.min(images[:2], axis=0)
    if noise_level_function is None:
        noise_level_function,blurred = oneImageNLF(images[0], images[1])
    print noSTE, noise_level_function(10), noise_level_function(1000), noise_level_function(10000)
    threshold = noise_level_function(noSTE)*nStd
    print threshold,88888
    out = np.zeros_like(images[0])
    removed = np.zeros(shape=i.shape,dtype=int)
    with np.errstate(invalid='ignore'):
        for i1, i2 in zip(images[:-1],images[1:]):
            i1 = imread(i1)
            i2 = imread(i2)
            diff = i1-i2
            
            
            diff = i-noSTE
            ind = diff > threshold
            out[~ind]+=i[~ind]/l
            out[ind] += noSTE[ind]
            print diff
            diff[ind]=0
            removed[ind]+=1
            out += diff/l
    return out, removed
