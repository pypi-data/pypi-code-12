from numba import jit

#REMOVE? not needed. - can be replaced with something like that:
#bg = maximum_filter(img,max(img.shape)/100)<sm
#binImg[bg]=0


@jit(nopython=True)
def filterIfNeighboursTooLow(img, img2, thresh, ksizeX=10, ksizeY=None):
    '''
    Filter values in [img] if local values in [img2] are not higher than 
    [thresh].
    
    img - 2d array, e.g. binary image
    img2 - 2d array of same size
    thresh - minimum value, if cannot be e exceeded within a kernel in img2 
             local img value set to false
    ksizeX, ksizeY - kernel size in x,y 
    '''
    if ksizeY is None:
        ksizeY = ksizeX

    gx = img.shape[0]
    gy = img.shape[1]

    
    hkx = ksizeX//2
    hky = ksizeY//2

    for i in xrange(gx):
        for j in xrange(gy):
            
            if img[i,j]:
            
                #get kernel boundaries:
                xmn = i-hkx
                if xmn < 0:
                    xmn = 0
                xmx = i+hkx
                if xmx > gx:
                    xmx = gx
                    
                ymn = j-hky
                if ymn < 0:
                    ymn = 0
                ymx = j+hky
                if ymx > gy:
                    ymx = gy
                
                found = False
                for ii in xrange(xmx-xmn):
                    for jj in xrange(ymx-ymn):
                        if img2[xmn+ii,ymn+jj] > thresh:
                            found = True
                            break
                    if found == True:
                        break
                if not found:
                    img[i,j]=False
            
if __name__ == '__main__':
    import numpy as np
    import pylab as plt
    
    img = np.random.rand(500,500)> 0.8
    img2 = np.fromfunction(lambda x,y: np.sin(x/300)+np.cos(y/100), (500,500))
    img2[np.random.rand(500,500)> 0.8]=0
    
    thresh = 0.4
    
    img3 = img.copy()
    filterIfNeighboursTooLow(img3, img2, thresh)
    
    plt.figure('before')
    plt.imshow(img)
    plt.figure('img2')
    plt.imshow(img2)
    plt.figure('after')
    plt.imshow(img3)
    plt.show()
    