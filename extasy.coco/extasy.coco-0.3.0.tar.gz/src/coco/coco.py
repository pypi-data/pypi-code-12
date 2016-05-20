# Python program that implements coco in Python.
#
# @Copyright
# Dr. Ardita Shkurti
# Dr. Charles Laughton
# The University of Nottingham
# Contact: ardita.shkurti@gmail.com

import numpy as np
import scipy.ndimage as nd

class Coco():
    
    def __init__(self, projs, resolution=10, limits=None):
        '''
        Initialise a COCO map. This is essentially a multidimensional histogram
        produced from a set of coordinate data, projs(N,D) where N is the
        number of points and D is the number of dimensions. "resolution" 
        specifies the number of bins in each dimension, and may be a single 
        number or a list of length D. The optional limits parameter sets the
        histogram boundaries, which are otherwise set automatically to include
        all the data.
        '''
        self.ndim = projs.shape[1]
        # resolution may be a single value or a list of values, 1 per dimension
        self.resolution = np.zeros(self.ndim)
        self.resolution[:] = resolution
        self.range = []
        if limits is None:
            self.limits = []
            min = projs.min(axis=0)
            max = projs.max(axis=0)
            # set a buffer, so that there is a clear 1-bin boundary around the map.
            # This is for future "halo" and "frontier" point-choosing methods.
            for i in range(self.ndim):
                buff = (max[i]-min[i])/(self.resolution[i]-2)*1.01
                self.limits.append((min[i]-buff,max[i]+buff))
        else:
            self.limits=limits
        # Create the histogram
        self.H, self.edges = np.histogramdd(projs, bins=self.resolution, range=self.limits)
        # find the bin dimensions (this should be buff, but don't assume)
        self.ginc = []
        for i in range(self.ndim):
            self.ginc.append(self.edges[i][1]-self.edges[i][0])
            
        # calculate the bin volume, and number of sampled bins
        self.cellvol = self.ginc[0]
        for l in self.ginc[1:]:			
            self.cellvol = self.cellvol*l
        self.coverage = self.H[np.where(self.H > 0)].size
        
    def cpoints(self,npoints):
        '''
        cpoints(np) returns new points, generated using the COCO procedure,
        in the form of an (npoints,D) numpy array, where D is the number of
        dimensions in the map.
        '''
        cp = np.zeros((npoints,self.ndim))
        # make a temporary binary image, and invert
        tmpimg = np.where(self.H > 0, 0, 1)
        for i in range(npoints):
            self.dis = nd.morphology.distance_transform_edt(tmpimg)
            indMax = np.unravel_index(self.dis.argmax(),self.dis.shape)
            for j in range(self.ndim):
                cp[i,j]=self.edges[j][0]+indMax[j]*self.ginc[j]
            
            tmpimg[indMax] = 0
        return cp
        

    def hpoints(self):
        '''
        hpoints() returns new points that form a halo of unsampled space
        just beyond the sampled region.
        '''
        # This is the halo filter:
        def f(arr):
            cval = arr[len(arr)/2]
            if cval == 0 and np.max(arr) > 0:
                return 1
            else:
                return 0

        halo = nd.filters.generic_filter(self.H,f,size=3,mode='constant')
        npoints = int(np.sum(halo))
        hp = np.zeros((npoints,self.ndim))
        for i in range(npoints):
            indMax = np.unravel_index(halo.argmax(),self.H.shape)
            for j in range(self.ndim):
                hp[i,j]=self.edges[j][0]+indMax[j]*self.ginc[j]
            
            halo[indMax] = 0
        return hp

    def fpoints(self):
        '''
        fpoints() returns new points at the frontier of sampled space
        '''
        # This is the frontier filter:
        def f(arr):
            cval = arr[len(arr)/2]
            if cval > 0 and np.min(arr) == 0:
                return 1
            else:
                return 0

        front = nd.filters.generic_filter(self.H,f,size=3,mode='constant')
        npoints = int(np.sum(front))
        fp = np.zeros((npoints,self.ndim))
        for i in range(npoints):
            indMax = np.unravel_index(front.argmax(),self.H.shape)
            for j in range(self.ndim):
                fp[i,j]=self.edges[j][0]+indMax[j]*self.ginc[j]
            
            front[indMax] = 0
        return fp

    def bpoints(self):
        '''
        bpoints() returns new points not at the frontier of sampled space
        '''
        # This is the buried filter:
        def f(arr):
            cval = arr[len(arr)/2]
            if cval > 0 and np.min(arr) > 0:
                return 1
            else:
                return 0

        bur = nd.filters.generic_filter(self.H,f,size=3,mode='constant')
        npoints = int(np.sum(bur))
        bp = np.zeros((npoints,self.ndim))
        for i in range(npoints):
            indMax = np.unravel_index(bur.argmax(),self.H.shape)
            for j in range(self.ndim):
                bp[i,j]=self.edges[j][0]+indMax[j]*self.ginc[j]
            
            bur[indMax] = 0
        return bp

    def rpoints(self):
        '''
        rpoints() returns one point per bin of sampled space, and its weight
        '''

#        tmpimg = np.where(self.H > 0, 1, 0)
        tmpimg = self.H.copy()
        hsum = np.sum(self.H)
        npoints = tmpimg[np.where(tmpimg > 0)].size
        wt = np.zeros((npoints))
        rp = np.zeros((npoints,self.ndim))
        for i in range(npoints):
            indMax = np.unravel_index(tmpimg.argmax(),self.H.shape)
            for j in range(self.ndim):
                rp[i,j]=self.edges[j][0]+indMax[j]*self.ginc[j]
            
            tmpimg[indMax] = 0
            wt[i] = self.H[indMax]/hsum
        return rp,wt
