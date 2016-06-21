# The mapping module. Creates and does various useful things with
# multidimensional histograms.

import numpy as np
import scipy.ndimage as nd
from skimage.feature import peak_local_max
import skimage.morphology

class Map():
    """
    Create a map - an enhanced multidimensional histogram - from sample data.

    A Map is essentially a multidimensional histogram produced from an 
    array of - typically - PCA projection data. It is the start point for 
    watershed clustering.
    
    Args: 
        arr(numpy array): The data, as an [N,D] array,. where N is the
            number of points and D is the number of dimensions. 
        resolution (Optional, int or list, default=10): The number of bins 
            in each dimension, and may be a single number or a list of 
            length D. 
        limits (Optional, list of floats) sets the histogram boundaries, 
            which are otherwise set automatically to include all the data.
        boundary(Optional, int, default=0): Sets a buffer of boundary 
            unoccupied bins at the edges of the histogram.

    Once created, a map has the following attributes set:

    Attributes:
        ndim (int): number of dimensions in the histogram.
        boundary (int): buffer of guaranteed empty bins at the limits
            of each dimension of the histogram.
        shape (tuple): shape of the histogram array.
        cellsize (numpy array): the dimensions of a histogram bin.
        cellvol (float): the volume of a histogram bin.
        coverage (int): the number of sampled bins in the histogram.
        volume(float): the volume of all sampled bins.
        ID (numpy array): the cluster ID of each histogram bin. IDs are
            positive integers, except for the bin that 
            contains the maximum number of samples for that
            cluster, which is marked with a negative ID.


    Methods:

        """
    
    def __init__(self, arr, resolution=10, boundary=0, limits=None):
        
        self.ndim = arr.shape[1]
        self.boundary = boundary
        # resolution may be a single value or a list of values, 1 per dimension
        self.resolution = np.zeros(self.ndim)
        self.resolution[:] = resolution
        if limits is None:
            self.limits = []
            min = arr.min(axis=0)
            max = arr.max(axis=0)
            # set a boundary
            for i in range(self.ndim):
                buff = (max[i]-min[i])/(self.resolution[i]-2*boundary)*boundary*1.01
                self.limits.append((min[i]-buff,max[i]+buff))
        else:
            self.limits=limits

        # Create the histogram
        self._H, self._edges = np.histogramdd(arr, bins=self.resolution, range=self.limits)
        self.shape = self._H.shape
        # find the bin dimensions (this should be buff, but don't assume)
        self.cellsize = []
        for i in range(self.ndim):
            self.cellsize.append(self._edges[i][1]-self._edges[i][0])
        # calculate the bin volume, and number of sampled bins
        self.cellvol = self.cellsize[0]
        for l in self.cellsize[1:]:
            self.cellvol = self.cellvol*l
        self.coverage = self._H[np.where(self._H > 0)].size
        # correct coverage if there is a boundary:
        v0 = 1
        v1 = 1
        for d in self.resolution:
           v0 = v0*d
           v1 = v1*(d-2*self.boundary)
        self.deadspace = v0 - v1
        self.volume = v0
        # now give preliminary values to the cluster-related data.
        self.ID = self._H.copy()
        indMax = np.unravel_index(self.ID.argmax(),self.ID.shape)
        self.ID = np.where(self._H > 0, 1, 0)
        self.ID[indMax] = -1
        self.sizes = [0, arr.shape[0]]

    def map(self, vec):
        """
        Returns the index of the bin that contains coordinates vec.

        Args:
            vec (numpy array, list or tuple): N-dimensional coordinate array, 
                where N is the number of dimensions in the histogram.

        Returns:
            indx (tuple): index of the bin that would contain point vec.
        """
        if len(vec) != self.ndim:
            raise ValueError('Error - vector has wrong length.')
        indx = []
        i = 0
        for c in vec:
            indx.append(np.digitize((c,c),self._edges[i])[0]-1)
            i += 1
        return indx

    def unmap(self, indx):
        """
        Returns the coordnates corresponding to the mid point of a bin.
        bin with the given index.

        Args:
            indx (tuple, list, or array): index of the bin in the N-dimensional 
                histogram.

        Returns:
            vec (list): coordinates of the bin mid-point.
        """
        if len(indx) != self.ndim:
            raise ValueError('Error - index has wrong number of dimensions.')
        vec = []
        i = 0
        for c in indx:
            vec.append(self.limits[i][0]+c*self.cellsize[i]+ 0.5*self.cellsize[i])
            i += 1
        return vec


    def cluster_id(self, vec):
        """
        Returns the cluster ID of the point vec.

        Args:
            vec (numpy array, list or tuple): N-dimensional coordinate array, 
                where N is the number of dimensions in the histogram.

        Returns:
            cid (int): ID of the cluster.
        """
        if len(vec) != self.ndim:
            raise ValueError('Error - vector has wrong length.')
        indx = []
        i = 0
        for c in vec:
            indx.append(np.digitize((c,c),self._edges[i])[0]-1)
            i += 1
        return self.ID[tuple(indx)]

    def cluster_centre(self, id):
        """
        Returns the mid point of the most populated bin for this cluster.

        Args:
            id (int): The cluster of interest.

        Returns:
            vec (list): coordinates of the bin centre.
        """
        if id < 0:
            id = -id
        w = np.where(self.ID == -id)
        e = []
        for i in range(self.ndim):
            e.append(self._edges[i][w[i][0]]+0.5*self.cellsize[i])
        return e 

    def cluster_size(self, id):
        """
        Returns the number of samples in cluster = id
        """
        return self.sizes[id-1]

def watershed(map):
    """
    Watershed clustering. 
    
    Args:
        map (Map object): Map on which to do the clustering. The process
            resets the ID attributes of each histogram bin.
    """
    # The method requires a clear 1-bin boundary around the distribution:
    if map.boundary < 1:
        raise ValueError('The input map needs to have a boundary.')

    a = map._H.astype(int)
    local_maxi = peak_local_max(a, min_distance = 1, indices = False, threshold_rel = 0.01)
    markers = nd.label(local_maxi)[0]
    map.ID = skimage.morphology.watershed(-a, markers, mask = a > 0)

    # Flatten for now to make the next few steps a bit easier:
    map.ID = map.ID.flatten()
    # now we find out big each cluster is:
    sizes = np.zeros(1+int(np.max(map.ID)), dtype=np.int)
    for i in range(len(map.ID)):
        sizes[int(map.ID[i])] += map._H.flatten()[i]
    # now reassign labels so largest group has label=1, etc.

    newlab = np.argsort(np.argsort(sizes))
    newlab = abs(newlab-newlab.max()) + 1
    map.sizes = np.sort(sizes)[::-1]

    for i in range(len(map.ID)):
        map.ID[i] = newlab[map.ID[i]]

    # put ID back into the right shape:
    map.ID = map.ID.reshape(map._H.shape)
    # now mark "root" structures with negative indices:
    map.ID = np.where(markers>0, -map.ID, map.ID)
    # set empty bins to have label=0:
    maxval = np.max(markers)
    map.ID = np.where(map.ID==maxval+1, 0, map.ID)

