import numpy as np
import scipy.ndimage as nd
def new_points(map, method='coco', npoints=1):
    """
    The CoCo (Complementary Coordinates) methods. The input is an
    MDPlus Map object defining the sampling so far of the conformational space.
    Various CoCo methods will identify 'interesting' regions to
    be sampled next.
    """
    if method == 'coco':
        """
        returns new points, generated using the COCO procedure,
        in the form of an (npoints,D) numpy array, where D is the number of
        dimensions in the map.
        """
        cp = np.zeros((npoints,map.ndim))
        # make a temporary binary image, and invert
        tmpimg = np.where(map._H > 0, 0, 1)
        for i in range(npoints):
            dis = nd.morphology.distance_transform_edt(tmpimg)
            indMax = np.unravel_index(dis.argmax(),dis.shape)
            for j in range(map.ndim):
                cp[i,j]=map._edges[j][0]+indMax[j]*map.cellsize[j]
            
            tmpimg[indMax] = 0
        return cp

    elif method == 'hpoints':
        """
        hpoints returns new points that form a halo of unsampled space
        just beyond the sampled region.
        """
        # This is the halo filter:
        def f(arr):
            cval = arr[len(arr)/2]
            if cval == 0 and np.max(arr) > 0:
                return 1
            else:
                return 0

        halo = nd.filters.generic_filter(map._H,f,size=3,mode='constant')
        npoints = int(np.sum(halo))
        hp = np.zeros((npoints,map.ndim))
        for i in range(npoints):
            indMax = np.unravel_index(halo.argmax(),map.shape)
            for j in range(map.ndim):
                hp[i,j]=map.edges[j][0]+indMax[j]*map.cellsize[j]
            
            halo[indMax] = 0
        return hp

    elif method == 'fpoints':
        """
        fpoints returns new points at the frontier of sampled space
        """
        # This is the frontier filter:
        def f(arr):
            cval = arr[len(arr)/2]
            if cval > 0 and np.min(arr) == 0:
                return 1
            else:
                return 0

        front = nd.filters.generic_filter(map._H,f,size=3,mode='constant')
        npoints = int(np.sum(front))
        fp = np.zeros((npoints,map.ndim))
        for i in range(npoints):
            indMax = np.unravel_index(front.argmax(),map.shape)
            for j in range(map.ndim):
                fp[i,j]=map._edges[j][0]+indMax[j]*map.cellsize[j]
            
            front[indMax] = 0
        return fp

    elif method == 'bpoints':
        """
        bpoints() returns new points not at the frontier of sampled space
        """
        # This is the buried filter:
        def f(arr):
            cval = arr[len(arr)/2]
            if cval > 0 and np.min(arr) > 0:
                return 1
            else:
                return 0

        bur = nd.filters.generic_filter(map._H,f,size=3,mode='constant')
        npoints = int(np.sum(bur))
        bp = np.zeros((npoints,map.ndim))
        for i in range(npoints):
            indMax = np.unravel_index(bur.argmax(),map.shape)
            for j in range(map.ndim):
                bp[i,j]=map._edges[j][0]+indMax[j]*map.cellsize[j]
            
            bur[indMax] = 0
        return bp

    elif method == 'rpoints':
        """
        rpoints() returns one point per bin of sampled space, and its weight
        """

        tmpimg = map._H.copy()
        hsum = np.sum(map._H)
        npoints = tmpimg[np.where(tmpimg > 0)].size
        wt = np.zeros((npoints))
        rp = np.zeros((npoints,map.ndim))
        for i in range(npoints):
            indMax = np.unravel_index(tmpimg.argmax(),map.shape)
            for j in range(map.ndim):
                rp[i,j]=map._edges[j][0]+indMax[j]*map.cellsize[j]
            
            tmpimg[indMax] = 0
            wt[i] = map._H[indMax]/hsum
        return rp,wt

    else:
        raise ValueError('Unknown method: {}'.format(method))

