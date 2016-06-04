import numpy as np
from fancytools.math.MaskedMovingAverage import MaskedMovingAverage

from imgProcessor.imgIO import imread

from imgProcessor.FitHistogramPeaks import FitHistogramPeaks
from imgProcessor.scaleSignal import getSignalPeak
from scipy.ndimage.filters import gaussian_filter
from fancytools.fit.fit2dArrayToFn import fit2dArrayToFn
from imgProcessor.equations.vignetting import vignetting



def flatFieldFromImgFit(images, nstd=3, ksize=15, scale_factor=0.7):
    '''
    calculate flat field from multiple non-calibration images
    through ....
    * blur each image
    * masked moving average all images to even out individual deviations
    * fit vignetting function of average
    
    return: flatfield, bglevel, fitimg, mask 
    '''
    
    #average background level
    bglevel = 0
    ll = 0
    for n,i in enumerate(images):
        print '%s/%s' %(n+1,len(images))
        try:
            img = imread(i, 'gray', dtype=float)
            
            if n == 0:        
                m = MaskedMovingAverage(shape=img.shape)
        
            f = FitHistogramPeaks(img)
            sp  = getSignalPeak(f.fitParams)
            
            #non-backround indices:
            i = img > sp[1]-nstd*sp[2]
            #blur:
            blurred = gaussian_filter(img, ksize)
            
            #scale [0-1]:
            mn = img[~i].mean()
            if np.isnan(mn):
                mn = 0
            mx = blurred.max()
            blurred-=mn
            blurred/=(mx-mn)
            
            m.update(blurred, i)
            
            bglevel += mn
            
            ll +=1
        except IOError, err:
            print err
            pass
        
    bglevel /= ll


    s0,s1 = img.shape
    s0*=scale_factor
    s1*=scale_factor
            #f-value, alpha, fx, cx,     cy
    guess = (s1*0.7,  0,     1 , s0/2.0, s1/2.0)
    
    #set assume normal plane - no tilt and rotation:
    fn = lambda (x,y),f,alpha, fx,cx,cy:  vignetting((x*fx,y),  f, alpha, 
            Xi=0, tau=0, cx=cx,cy=cy)

    fitimg = m.avg
    mask = fitimg>0.5
    
    flatfield = fit2dArrayToFn(fitimg, fn, mask=mask, 
                    guess=guess, scale_factor=scale_factor)[0]
    
    
    return flatfield, bglevel, fitimg, mask
    

