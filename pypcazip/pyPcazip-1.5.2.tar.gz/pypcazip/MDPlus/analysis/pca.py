import numpy as np
from scipy.linalg import *
import struct
import logging as log
import sys
from time import time
import warnings
from MDPlus import fastfitting
try:
    import h5py
    h5py_available = True
except ImportError:
    h5py_available = False

class Pcz:
    """
    PCA analysis of trajectory data.

    Initialises a new pcz object with the data from the given
    cofasu object.

    Arguments:
        cofasu: An MDPlus cofasu.
        target (Optional, array): target structure used for least-squares
            fitting.
        covar (Optional, array): Pre-calculated covriance matrix.
        quality (Opt, float): Percentage of variance to be explained.
            Defaults to 90.0 (90%).
        req_evecs (Optional, int): Number of eigenvectors to calculate. If
            set, overrides quality setting.
        fastmethod (optional, bool): If True, an approximate fast matrix
            diagonalizaion method is used.

    Attributes:
        nvecs (int): Number of eigenvectors.
        avg (array): Mean structure.
        evals (array): Eigenvalues, in descending order of size.
        evecs ([nvecs, 3*natoms] array): Eigenvectors, in same order as
            eigenvectors.
        projs ([nvecs, nframes] array): Projection data.

    >>> topfile = "../../../../test/2ozq.pdb"
    >>> trjfile = "../../../../test/2ozq.dcd"
    >>> from MDPlus.core import Fasu, Cofasu
    >>> c = Cofasu(Fasu(topfile, trjfile, 
    ...    selection='name CA and resid 1 to 10'))
    >>> p = Pcz(c)

    
    target can be a precalculated global average
    structure:

    >>> target = c.avg-10.0
    >>> p = Pcz(c, target=target)

    covar can be a precalculated covariance matrix, in which case the
    corresponding target structure must also be given.

    The quality setting defaults to 90%:
    >>> p = Pcz(c, quality=95)
    >>> p = Pcz(c, quality=120)
    Traceback (most recent call last):
    ...
    ValueError: Pcz: quality must lie in the range 0:100.

    If fastmethod=True then a fast approximate diagonalisation
    method is used.

    >>> f = Fasu(topfile, trjfile, selection='resid 1 to 30')
    >>> c = Cofasu(f)
    >>> p1 = Pcz(c)
    >>> ev1 = p1.evals
    >>> p2 = Pcz(c, fastmethod=True)
    >>> ev2 = p2.evals
    >>> print(np.allclose(ev1, ev2))
    True

    """
    def __init__(self, cofasu, target=None, covar=None, quality=90.0,
                 req_evecs=None,  fastmethod=False):

        self.cofasu = cofasu
        self.comm = self.cofasu.comm
        self.quality = quality
        self.natoms = self.cofasu.shape[1]
        self.nframes = self.cofasu.shape[0]
        
        if self.comm is not None:
            self.rank = self.comm.Get_rank()
            self.size = self.comm.Get_size()
        else:
            self.rank = 0
            self.size = 1

        if quality < 0 or quality > 100:
            raise ValueError('Pcz: quality must lie in the range 0:100.')

        if self.rank == 0:
            log.info('Pcz: {0} atoms and {1} snapshots'.format(self.natoms, 
                     self.nframes))
        if covar is None:
            if self.rank == 0:
                log.info('Pcz: least-squares fitting snapshots')
            time_avg_0 = time()
            self.cofasu.align(target=target, procrustes=True)
            self.avg = self.cofasu.avg
            time_avg_1 = time()
            if self.rank == 0:
                log.info( 'Pcz: Time for trajectory fitting: '
                         + '{0:.2f} s'.format(time_avg_1 - time_avg_0))

            if self.rank == 0:
                log.info('Pcz: calculating covariance matrix')
            if fastmethod:
                # adapted from Ian Dryden's R code. If you have
                # n atoms and p snapshots, then the conventional
                # way to do the pca is to calculate the [3n,3n]
                # covariance matrix and then diagonalise that.
                # However if p < 3n, then the last 3n-p eigenvectors
                # and values are meaningless anyway, and instead
                # you can calculate the [p,p] covariance matrix,
                # diagonalise that, and then do some
                # data massaging to recover the full eigenvectors
                # and eigenvalues from that. Here we extend the
                # approach to situations where 3n is just too big
                # for diagonalisation in a reasonable amount of
                # time, by just taking a selection of snapshots
                # from the full set (<< 3n) and applying this
                # approach. Obviously this is an approximate
                # method, but it may be good enough.
                if self.rank == 0:
                    log.info("Using fast approximate diagonalisation method")
                nsamples = min(100,self.nframes)
                stepsize = self.nframes/nsamples
                tmptrj = self.cofasu[::stepsize]
                tmptrj = tmptrj - self.avg
                tmptrj = tmptrj.reshape((-1, 3 * self.natoms))

                cv = np.dot(tmptrj.conj(), tmptrj.T)/nsamples
            else:
                n3 = self.natoms * 3
                lcv = np.zeros((n3, n3))
                nlocal = 0
                for f in self.cofasu.fasulist:
                    if f.owner ==  self.rank:
                        dx = (f.x - self.avg).reshape((-1, n3))
                        lcv += np.dot(dx.T, dx.conj())
                        nlocal += 1
                log.debug('Process {} owns {} fasus.'.format(self.rank, nlocal))
                if self.comm is None:
                    cv = lcv
                else:
                    self.comm.Barrier()
                    #cv = self.comm.allreduce(lcv)
                    cv = np.zeros((n3, n3))
                    self.comm.Allreduce(lcv, cv)

                cv = cv / self.nframes
                if self.rank == 0:
                    log.info("Global CM calculated")
        else:
            # Covariance matrix supplied. This requires that the corresponding
            # target structure is given as well.
            if target is None:
                raise ValueError('A defined covariance matrix requires'
                                 + ' a defined target.')
            else:
                self.avg = target
                cv = covar

        if self.rank == 0:
            log.info('Pcz: diagonalizing covariance matrix')
        time_diag_cov_0 = time()
        w, v = eigh(cv)

        if fastmethod:
            vv = np.zeros(nsamples)
            z = np.dot(tmptrj.T,v)
            for i in range(nsamples):
                vv[i] = np.sqrt((z[:,i]*z[:,i]).sum())
                z[:,i] = z[:,i]/vv[i]

            w2 = np.sqrt(abs(w/nsamples))*vv
            w = w2[w2.argsort()]
            v = z[:,w2.argsort()]

        cs = np.cumsum(w[::-1])
        self.totvar = cs[-1]
        tval = cs[-1] * self.quality / 100
        i = 0
        while cs[i] < tval:
            i += 1

        i += 1
        self.nvecs = i
        # override this with req_evecs, if given:
        if req_evecs is not None:
            if req_evecs > len(w):
                if self.rank == 0:
                    log.error('Pcz: you asked for {0} eigenvectors but there'
                              + ' are only {1} available.'.format(req_evecs, 
                                                                  len(w)))
            else:
                self.nvecs = req_evecs
                i = req_evecs

        self.evals = w[-1:-(i + 1):-1]
        self.evecs = v[:, -1:-(i + 1):-1].T
        time_diag_cov_1 = time()
        if self.rank == 0:
            log.info( 'Pcz: Time for diagonalizing covariance matrix: '
                     + '{0:.2f} s\n'.format(time_diag_cov_1 - time_diag_cov_0))

        time_proj_calc_0 = time()

        plist = []
        n3 = 3 * self.natoms
        for f in self.cofasu.fasulist:
            if f.owner  == self.rank:
                dx = (f.x - self.avg).reshape((-1, n3))
                plist.append(np.dot(dx, self.evecs.T).T)
            
        if len(plist) == 0:
            lproj = np.zeros((0, 0))
        else:
            lproj = np.hstack(plist)
        if self.comm is not None:
            gproj = self.comm.allgather(lproj)
            self.projs = np.hstack([p for p in gproj if p.size > 0])
        else:
            self.projs = lproj

        time_proj_calc_1 = time()
        if self.rank == 0:
            log.info('Pcz: Time for calculating projections: '
                     + '{0:.2f} s'.format(time_proj_calc_1 - time_proj_calc_0))

    def numframes(self):
        """
        Return the numnber of frames in the trajectory.

        Returns:
            nframes (int): number of frames in the trajwectory
        """
        return self.nframes

    def _avg(self):
        """
        Return the average structure contained in the pcz file
        as an (natoms,3) numpy array.

        >>> topfile = "../../../../test/2ozq.pdb"
        >>> trjfile = "../../../../test/2ozq.dcd"
        >>> from MDPlus.core import Fasu, Cofasu
        >>> f = Fasu(topfile, trjfile, selection='name CA')
        >>> c = Cofasu(f)
        >>> p = Pcz(c)
        >>> print(np.allclose(p._avg()[0], 
        ...       np.array([ 31.323149, 61.575380, 40.136298]), 
        ...       atol=0.001, rtol=0.001))
        True

        """
        return self.avg

    def _eval(self, ival):
        """
        Returns an eigenvalue from the file.

        Examnple:

        >>> topfile = "../../../../test/2ozq.pdb"
        >>> trjfile = "../../../../test/2ozq.dcd"
        >>> from MDPlus.core import Fasu, Cofasu
        >>> f = Fasu(topfile, trjfile, selection='name CA')
        >>> c = Cofasu(f)
        >>> p = Pcz(c)
        >>> print(np.allclose(p._eval(4), 
        ...       np.array([2.6183940]), rtol=0.001, atol=0.001))
        True

        """
        if ival >= self.nvecs:
            print 'Error - only ', self.nvecs, ' eigenvectors present'
            return 0.0
        else:
            return self.evals[ival]

    def _evals(self):
        """
        Returns an array of all eigenvalues in the file.

        Example:

        >>> topfile = "../../../../test/2ozq.pdb"
        >>> trjfile = "../../../../test/2ozq.dcd"
        >>> from MDPlus.core import Fasu, Cofasu
        >>> f = Fasu(topfile, trjfile, selection='name CA')
        >>> c = Cofasu(f)
        >>> p = Pcz(c)
        >>> print(np.allclose(p._evals()[4], 
        ...       np.array([2.6183940]), rtol=0.001, atol=0.001))
        True

        """
        return self.evals

    def _evec(self, ivec):
        """
        Returns a chosen eigenvector from the file in the
        form of a (3*natoms) numpy array.

        Example:

        >>> topfile = "../../../../test/2ozq.pdb"
        >>> trjfile = "../../../../test/2ozq.dcd"
        >>> from MDPlus.core import Fasu, Cofasu
        >>> f = Fasu(topfile, trjfile, selection='name CA')
        >>> c = Cofasu(f)
        >>> p = Pcz(c)
        >>> print(np.allclose(abs(p._evec(1)[12]), 
        ...       np.array([0.00865751377]), rtol=0.001, atol=0.001))
        True

        """
        if ivec >= self.nvecs:
            print 'Error - only ', self.nvecs, 'eigenvectors present'
            return None
        else:
            return self.evecs[ivec, :]

    def _evecs(self):
        """
        Returns all eigenvectors in the file in the form of a
        (Mnvecs,3*natoms) numpy array.

        Example:

        >>> topfile = "../../../../test/2ozq.pdb"
        >>> trjfile = "../../../../test/2ozq.dcd"
        >>> from MDPlus.core import Fasu, Cofasu
        >>> f = Fasu(topfile, trjfile, selection='name CA')
        >>> c = Cofasu(f)
        >>> p = Pcz(c)
        >>> e = p._evecs()
        >>> print(e.shape)
        (18, 471)

        >>> element = abs(e[1,12])
        >>> print(np.allclose(element, 
        ...       np.array([0.0086575138]), rtol=0.001, atol=0.001))
        True

        """
        return self.evecs

    def _proj(self, iproj):
        """
        Returns an array of the projections along a given eigenvector. There
        will be one value per snapshot.

        Example:
        >>> topfile = "../../../../test/2ozq.pdb"
        >>> trjfile = "../../../../test/2ozq.dcd"
        >>> from MDPlus.core import Fasu, Cofasu
        >>> f = Fasu(topfile, trjfile, selection='name CA')
        >>> c = Cofasu(f)
        >>> p = Pcz(c)
        >>> prj = abs(p._proj(3))
        >>> print(np.allclose(prj[21], 0.3312888, rtol=0.001, atol=0.001))
        True

        """
        if iproj >= self.nvecs:
            print 'Error - only ', self.nvecs, 'eigenvectors present'
            return None
        else:
            return self.projs[iproj, :]

    def scores(self, framenumber):
        """
        Return the scores (projections) corresponding to a chosen snapshot.

        Args:
            framenumber (int): index of trajectory frame

        Returns:
            scores ([nvecs] numpy array): Scores for each eigenvector.

        Example:

        >>> topfile = "../../../../test/2ozq.pdb"
        >>> trjfile = "../../../../test/2ozq.dcd"
        >>> from MDPlus.core import Fasu, Cofasu
        >>> f = Fasu(topfile, trjfile, selection='name CA')
        >>> c = Cofasu(f)
        >>> p = Pcz(c)
        >>> s = abs(p.scores(12))
        >>> print(np.allclose(s[3], 0.5800652, rtol=0.001, atol=0.001))
        True

        """
        return self.projs.T[framenumber]

    def coords(self, framenumber):
        """
        Returns the coordinates of the selected frame. Synonym for frame method.
        """
        return self.frame(framenumber)

    def frame(self,framenumber):
        """
        Method to return the coordinates of the given frame.
        
        Args:
            framenumber (int): index of selected frame

        Retuns:
            crds ([natom, 3] numpy array): coordinates


        Example:

        >>> topfile = "../../../../test/2ozq.pdb"
        >>> trjfile = "../../../../test/2ozq.dcd"
        >>> from MDPlus.core import Fasu, Cofasu
        >>> f = Fasu(topfile, trjfile, selection='name CA')
        >>> c = Cofasu(f)
        >>> c.align(procrustes=True)
        >>> p = Pcz(c, quality=95)
        >>> ref = c[5]
        >>> x = p.frame(5)
        >>> print( (abs(x - ref)).mean() < 0.19)
        True

        """
        if(framenumber >= self.nframes):
            return None
        else:
            scores = self.scores(framenumber)
            return self.unmap(scores)


    def closest(self, scores):
        """
        Returns the index of the frame with scores closest to the target values.

        Args:
            scores (numpy array): target scores. If the scores vector has less
                than nvec elements, the least significant are assumed to be zero.

        Returns:
            indx (int): The index of the snapshot whose scores are closest to
                the input set.
        """
        ns = len(scores)
        temp = self.projs

        best = 0
        err = ((temp[0:ns, 0] - scores) * (temp[0:ns, 0] - scores)).sum()
        for frame in range(self.nframes):
            newerr = ((temp[0:ns, frame] - scores) 
                      * (temp[0:ns, frame] - scores)).sum()
            if newerr < err:
                err = newerr
                best = frame
        return best

    def unmap(self,scores):
        """
        Return the coordinates corresponding to a given set of scores. 

        Args:
            scores (numpy array): a list of scores. If scores has less than
                nvec elements, the least significant are assumed to be zero.


        Returns:
            crds ([natom, 3] numpy array): coordinates.

        Example:

        >>> topfile = "../../../../test/2ozq.pdb"
        >>> trjfile = "../../../../test/2ozq.dcd"
        >>> from MDPlus.core import Fasu, Cofasu
        >>> f = Fasu(topfile, trjfile, selection='name CA')
        >>> c = Cofasu(f)
        >>> p = Pcz(c)
        >>> a = p._avg()
        >>> a2 = p.unmap(np.zeros(p.nvecs))
        >>> print((abs(a - a2)).mean() < 0.001)
        True

        """
        x = self._avg()
        for i in range(self.nvecs):
            x = x + (self._evec(i)*scores[i]).reshape((self.natoms,3))
        return x

    def map(self,crds):
        """
        Method to map an arbitrary coordinate set onto the PC model. 
        
        The coordinate set should be a (natom,3) array-like object that matches
        (for size) what's in the pczfile. An array of scores will be 
        returned, one value for each eignevector in the pcz file.

        Args:
            crds ([natom, 3] numpy array): coordinates.

        Returns:
            scores ([nvecs] numpy array): list of scores.

        Example:

        >>> topfile = "../../../../test/2ozq.pdb"
        >>> trjfile = "../../../../test/2ozq.dcd"
        >>> from MDPlus.core import Fasu, Cofasu
        >>> f = Fasu(topfile, trjfile, selection='name CA')
        >>> c = Cofasu(f)
        >>> p = Pcz(c)
        >>> m = p.scores(10)
        >>> crds = c[10]
        >>> print(np.allclose(abs(p.map(crds)),abs(m), rtol=0.001, atol=0.001))
        True

        """
        c = fastfitting.fitted(crds, self.avg)
        c = c - self.avg
        prj = np.zeros(self.nvecs)
        for i in range(self.nvecs):
             prj[i]=(np.dot(c.flatten(),self._evec(i)))
        return prj
  

    def write(self, filename,  version='PCZ6', title='Created by pcz.write()'):
        """
        Write out the PCZ file.

        Args:
            filename (str): Name of .pcz file.
            version (str): Pcz version (format) - can be 'PCZ4', 'PCZ6', or
                'PCZ7'
            title (str): Title for .pcz file.

        """

        self.version = version # Pcz file version (format)
        if self.rank != 0:
            return
        if self.version == 'PCZ7' and not h5py_available:
            log.info('WARNING: The PCZ6 format will be used because '
                     + 'the h5py module required for PCZ7 does not seem'
                     + ' to be installed.')
            self.version = 'PCZ6'

        if self.version == 'UNKN':
            if h5py_available:
                self.version = 'PCZ7'
            else:
                self.version = 'PCZ6'

        if not self.version in ['PCZ4', 'PCZ6', 'PCZ7']:
            raise TypeError('Only PCZ4/6/7 formats supported')

        log.info("Using "+self.version+" format")

        if self.version == 'PCZ4' or self.version == 'PCZ6':
            f = open(filename, 'wb')
            f.write(struct.pack('4s80s3if', self.version, title, self.natoms, 
                    self.nframes, self.nvecs, self.totvar))
            f.write(struct.pack('4i', 0, 0, 0, 0))
            for v in self._avg().flatten():
                f.write(struct.pack('f', v))
            for i in range(self.nvecs):
                for v in self._evec(i):
                    f.write(struct.pack('f', v))
                f.write(struct.pack('f', self._eval(i)))

                projection = self._proj(i)

                if self.version == 'PCZ4':
                    for v in projection:
                        f.write(struct.pack('f', v))
                elif self.version == 'PCZ6':
                    pinc = (projection.max() - projection.min()) / 65534
                    p0 = (projection.max() + projection.min()) / 2
                    f.write(struct.pack('2f', p0, pinc))
                    for v in projection:
                        f.write(struct.pack('h', np.int16((v - p0) / pinc)))

                else:
                    print 'Error - only PCZ4 and PCZ6 formats supported'

            f.close()
            return
        elif self.version == 'PCZ7':
            if not h5py_available:
                print ('Error: the h5py module is required for PCZ7 format '
                      + 'but does not seem to be installed.')
                sys.exit(0)
            f = h5py.File(filename, "w")
            # Write evecs and evalues
            f.create_dataset("evec_dataset", (self.nvecs, (3 * self.natoms)), 
                             dtype='f', data=self._evecs())
            f.create_dataset("eval_dataset", (self.nvecs,), 
                             dtype='f', data=self._evals())
            # Write reference coordinates
            f.create_dataset("ref_coord_dataset", (len(self._avg().flatten()),),
                             dtype='f', data=np.array(self._avg().flatten()))
            # Write properties
            f.attrs['version'] = self.version
            f.attrs['title'] = title
            f.attrs['natoms'] = self.natoms
            f.attrs['nframes'] = self.nframes
            f.attrs['nvecs'] = self.nvecs
            f.attrs['quality'] = self.totvar

            # Loop on every ts
            proj_dataset = f.create_dataset("proj_dataset", (self.nframes,
            self.nvecs), dtype='int16')
            p0_dataset = f.create_dataset("p0_dataset", (self.nframes,), 
                                          dtype='f')
            pinc_dataset = f.create_dataset("pinc_dataset", (self.nframes,), 
                                            dtype='f')

            for ts_index in xrange(self.nframes):
                projection_values = self.scores(ts_index)

                pinc = (projection_values.max() 
                        - projection_values.min()) / 65534
                if pinc == 0:
                    pinc == numpy.nextafter(0, 1)
                p0 = (projection_values.min() + projection_values.max()) / 2
                p0_dataset[ts_index] = p0
                pinc_dataset[ts_index] = pinc
                projection_values = projection_values - p0
                proj_dataset[ts_index] = (projection_values 
                                          / pinc).astype(np.int16)


        else:
            raise TypeError('Only PCZ4/6/7 formats supported')

class Pczfile:
    """
    Initialises a new pcz object with the data from the given file.

    Args:
        filename (str): Name of the .pcz format file to be loaded.

    Attributes:
        natoms (int): Number of atoms
        nframes (int): number of frames
        nvecs (int): number of eigenvectors
        totvar (float): total variance in original data
        quality (float): percentage of total variance captured
        evals ([nvecs] numpy array): eigenvalues (largest first)
        evecs ([nvecs, 3*natoms] numpy array): eigenvectors (order as evals)
        projs ([nframes, nvecs] numpy array): projection data
        avg ([natoms, 3] numpy array): average structure

    """
    def __init__(self, filename, preload=True):
        self.filename = filename
        preload = True # enforce preloading
        self.preloaded = preload
        try:
            self.filehandle = open(self.filename, 'rb')
        except IOError as e:
            print "Problems while tried to open a pcz-format file."
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
            return
        self.data = self.filehandle.read(100)
        if self.data[0:4] != 'PCZ4' and self.data[0:4] != 'PCZ6':
                if not h5py_available:
                    print "Error: unrecognised pcz file format"
                    sys.exit(0)
                try:
                    self.filehandle = h5py.File(self.filename, "r")
                    self.data = 'PCZ7'
                except IOError:
                    print 'Error: unrecognised pcz file format'
                    self.filehandle.close()
                    return

        if self.data[0:4] == 'PCZ4' or self.data[0:4] == 'PCZ6':
            self.keydata = struct.unpack('4s80s3if', self.data)
            self.version = self.keydata[0]
            self.title = self.keydata[1]
            self.natoms = self.keydata[2]
            self.nframes = self.keydata[3]
            self.nvecs = self.keydata[4]
            self.totvar = self.keydata[5]

            self.data = self.filehandle.read(16)
            self.keydata = struct.unpack('4i', self.data)
            self.extra = self.keydata[3]

            if self.extra == 0:
                self.headerblocksize = 116
            else:
                self.headerblocksize = 116 + 16 * self.natoms

            self.avgblocksize = 3 * self.natoms * 4
            if self.version == 'PCZ4':
                self.evblocksize = 3 * self.natoms * 4 + 4 + self.nframes * 4
            else:
                self.evblocksize = 3 * self.natoms * 4 + 4 + 8 + self.nframes * 2

            if preload:
                self.preloaded = False
                self.avg = self._avg()
                self.evals = self._evals()
                self.quality = 100.0 * (self.evals.sum() / self.totvar)
                self.evecs = self._evecs()
                self.projs = np.zeros((self.nvecs, self.nframes))
                for i in range(self.nvecs):
                    self.projs[i, :] = self._proj(i)
                self.preloaded = True

        elif self.data[0:4] == 'PCZ7':
            self.version = self.filehandle.attrs['version']
            self.title = self.filehandle.attrs['title']
            self.natoms = self.filehandle.attrs['natoms']
            self.nframes = self.filehandle.attrs['nframes']
            self.numframes = self.nframes
            self.n_evecs = self.filehandle.attrs['nvecs']
            self.nvecs = self.filehandle.attrs['nvecs']
            self.totvar = self.filehandle.attrs['quality']
            self.evecs = np.array(self.filehandle['evec_dataset'])
            self.evals = np.array(self.filehandle['eval_dataset'])
            self.avg = np.array(self.filehandle['ref_coord_dataset'])
            self.avg = self.avg.reshape((-1,3))
            self.quality = 100.0 * (self.evals.sum()/self.totvar)

            self.preloaded = preload
            if preload:
                self._projs = np.array(self.filehandle['proj_dataset'])
                self._p0 = np.array(self.filehandle['p0_dataset'])
                self._pinc = np.array(self.filehandle['pinc_dataset'])

                self.projs = self.projs * self._pinc + self._p0
        else:
            print 'Error: unrecognised pcz file format'
            return

    def _avg(self):
        """
        Returns the average structure contained in the pcz file
        as an (natoms,3) numpy array.
        """
        if self.preloaded:
            return self.avg
        elif self.version == 'PCZ7':
            return self.avg
        else:
            self.filehandle.seek(self.headerblocksize)
            self.data = self.filehandle.read(self.avgblocksize)
            return np.array(struct.unpack(str(self.natoms * 3) + 'f',
                                          self.data)).reshape((self.natoms, 3))

    def _eval(self, ival):
        """
        Returns an eigenvalue from the file.
        """
        if ival >= self.nvecs:
            print 'Error - only ', self.nvecs, ' eigenvectors present'
            return 0.0
        else:
            if self.preloaded:
                return self.evals[ival]
            elif self.version == 'PCZ7':
                return self.evals[ival]
            else:
                self.filehandle.seek(self.headerblocksize + self.avgblocksize +
                                     ival * self.evblocksize + self.avgblocksize)
                return struct.unpack('f', self.filehandle.read(4))[0]

    def _evals(self):
        """
        Returns an array of all eigenvalues in the file.
        """
        if self.preloaded:
            return self.evals
        else:
            evs = np.zeros(self.nvecs)
            for i in range(self.nvecs):
                evs[i] = self._eval(i)
            return evs

    def _evec(self, ivec):
        """
        Returns a chosen eigenvector from the file in the
        form of a (3*natoms) numpy array.
        """
        if ivec >= self.nvecs:
            print 'Error - only ', self.nvecs, 'eigenvectors present'
            return None
        else:
            if self.preloaded:
                return self.evecs[ivec, :]
            elif self.version == 'PCZ7':
                return self.evecs[ivec, :]
            else:
                self.filehandle.seek(self.headerblocksize + self.avgblocksize +
                                     ivec * self.evblocksize)
                return np.array(struct.unpack(str(3 * self.natoms) + 'f',
                                              self.filehandle.read(self.avgblocksize)))

    def _evecs(self):
        """
        Returns all eigenvectors in the file in the form of a
        (nvecs,3*natoms) numpy array.
        """
        if self.preloaded:
            return self.evecs
        else:
            evs = np.zeros((self.nvecs, self.natoms * 3))
            for i in range(self.nvecs):
                evs[i, :] = self._evec(i)
            return evs

    def _proj(self, iproj):
        """
        Returns an array of the projections along a given eigenvector. There
        will be one value per snapshot.
        """
        if iproj >= self.nvecs:
            print 'Error - only ', self.nvecs, 'eigenvectors present'
            return None
        if self.preloaded:
            return self.projs[iproj, :]

        if self.version == 'PCZ7':
            proj_list = []
            for frame_index in xrange(self.nframes):
                p0 = np.array(self.filehandle['p0_dataset'][frame_index])
                pinc = np.array(self.filehandle['pinc_dataset'][frame_index])
                i = np.array(self.filehandle['proj_dataset'][frame_index][iproj])
                proj_list.append(p0 + pinc * i)
            return np.array(proj_list)

        self.filehandle.seek(self.headerblocksize + self.avgblocksize +
                             iproj * self.evblocksize + self.avgblocksize + 4)

        if self.version == 'PCZ4':
            return np.array(struct.unpack(str(self.nframes) + 'f',
                                          self.filehandle.read(4 * self.nframes)))
        ip = list(0 for i in range(self.nframes))
        p0, pinc = struct.unpack('2f', self.filehandle.read(8))
        self.filehandle.seek(self.headerblocksize + self.avgblocksize +
                             iproj * self.evblocksize + self.avgblocksize + 12)
        ip = struct.unpack(str(self.nframes) + 'h',
                           self.filehandle.read(self.nframes * 2))
        return np.array(list(p0 + pinc * i for i in ip))

    def scores(self, framenumber):
        """
        Returns the scores (projections) corresponding to a chosen snapshot.

        Args:
            framenumber (int): index of selected frame

        Returns:
            scores ([nvecs] numpy array): list of scores
        """
        if framenumber >= self.nframes:
            return None
        elif self.version == 'PCZ7':
            p0 = np.array(self.filehandle['p0_dataset'][framenumber])
            pinc = np.array(self.filehandle['pinc_dataset'][framenumber])
            projs_comp = np.array(self.filehandle['proj_dataset'][framenumber])
            projs = [p0 + pinc * i for i in projs_comp]
            return np.array(projs)
        else:
            x = np.zeros(self.nvecs)
            for i in range(self.nvecs):
                x[i] = self._proj(i)[framenumber]
            return x

    def frame(self, framenumber):
        """
        Return the coordinates of the given frame.

        Args:
            framenumber (int): index of selected frame

        Returns:
            crds ([natoms, 3] numpy array): coordinates.
        """
        if (framenumber >= self.nframes):
            return None
        else:
            scores = self.scores(framenumber)
            return self.unmap(scores)

    def unmap(self, scores):
        """
        Return the coordinates corresponding to a given set of scores.

        Args:
            scores (numpy array): list of scores. If fewer than nvecs
                elements, the least significant are assumed to be zero.

        Returns:
            crds ([natoms, 3] numpy array): coordinates.
        """
        if self.version == 'PCZ7':
            projs = np.array(scores).T
            crds = np.array(self.avg + np.dot(projs, self.evecs))
            return crds.reshape(self.natoms, 3)
        else:
            x = self._avg()
            for i in range(len(scores)):
                x = x + (self._evec(i) * scores[i]).reshape((self.natoms, 3))
            return x

    def closest(self, scores):
        """
        Return the index of the frame with scores closest to the target values.

        Args:
            scores (numpy array): list of scores. If fewer than nvecs
                elements, the least significant are assumed to be zero.

        Returns:
            indx (int): index of the frame with the most similar scores.
        """
        ns = len(scores)
        if self.preloaded:
            temp = self._projs
        else:
            temp = np.zeros((self.nvecs, self.nframes))
            for vec in range(self.nvecs):
                temp[vec, :] = self._proj(vec)

        best = 0
        err = ((temp[0:ns, 0] - scores) * (temp[0:ns, 0] - scores)).sum()
        for frame in range(self.nframes):
            newerr = ((temp[0:ns, frame] - scores) * (temp[0:ns, frame] - scores)).sum()
            if newerr < err:
                err = newerr
                best = frame
        return best

    def map(self, crds):
        """
        Map an arbitrary coordinate set onto the PC model. 

        Args:
            crds ([natoms, 3] numpy array): coordinates

        Returns:
            scores ([nvecs] numpy array): scores vector
        """
        crdset = np.array(crds)
        if np.shape(crdset) == (self.natoms, 3):
            avg = np.reshape(self._avg(), (self.natoms, 3))
            c = fastfitting.fitted(crdset, avg) - avg
            prj = np.zeros(self.nvecs)
            for i in range(self.nvecs):
                prj[i] = (np.dot(c.flatten(), self._evec(i)))
            return prj
        else:
            raise ValueError('coordinate array size does not match pcz data.')

if __name__ == "__main__":
    import doctest
    doctest.testmod()
