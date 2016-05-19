#!/usr/bin/env python
'''
The pcz class.
'''
import numpy as np
import dask.array as da
from scipy.linalg import *
import struct
import logging as log
import sys
from time import time
import warnings
from MDPlus.core import fastfitting

CHUNKS=1000

try:
    import h5py
    h5py_available = True
except ImportError:
    h5py_available = False

class Pcz:
    def __init__(self, cofasu, version='PCZ6',target=None, covar=None, quality=90.0,
                 req_evecs=None,  fastmethod=False, comm=None):
        '''
        Initialises a new pcz object with the data from the given
        cofasu object:
        >>> topfile = "../../../../test/2ozq.pdb"
        >>> trjfile = "../../../../test/2ozq.dcd"
        >>> from MDPlus.core import cofasu
        >>> c = cofasu.Cofasu(cofasu.Fasu(topfile, trjfile, 
        ...    selection='name CA and resid 1 to 10'))
        >>> p = Pcz(c)

        
        target can be a precalculated global average
        structure:

        >>> target = c[:].mean(axis=0)-10.0
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

        >>> f = cofasu.Fasu(topfile, trjfile, selection='resid 1 to 30')
        >>> c = cofasu.Cofasu(f)
        >>> p1 = Pcz(c)
        >>> ev1 = p1.evals()
        >>> p2 = Pcz(c, fastmethod=True)
        >>> ev2 = p2.evals()
        >>> print(np.allclose(ev1, ev2))
        True

        '''

        self.version = version
        self.cofasu = cofasu
        self.comm = comm
        self.quality = quality
        self.natoms = self.cofasu.shape[1]
        self.nframes = self.cofasu.shape[0]
        
        if comm is not None:
            self.rank = comm.Get_rank()
            self.size = comm.Get_size()
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
                self._avg = self.cofasu.x.mean(axis=0)
                tmptrj = self.cofasu.x[::stepsize]
                tmptrj = tmptrj - self._avg
                tmptrj = tmptrj.reshape((-1, 3 * self.natoms))

                cv = da.dot(tmptrj.conj(), tmptrj.T).compute()/nsamples
            else:
                if comm is None:
                    cv = da.cov(self.cofasu.x.reshape((-1, self.natoms*3)), 
                                rowvar=0, bias=1).compute()
                    self._avg = self.cofasu.x.mean(axis=0)
                else:
                    blocksize = len(cofasu) / self.size
                    if blocksize * self.size < len(cofasu):
                        blocksize += 1
                    start = self.rank * blocksize
                    end = min(start + blocksize, len(cofasu))
                    trj = cofasu.x[start:end]
                    wt = float(len(trj))/self.nframes
                    assert wt > 0.0
                    l_avg = trj.mean(axis=0).compute()
                    l_avg = l_avg * wt
                    avg = comm.allreduce(l_avg)
                    self._avg = da.from_array(avg, chunks=CHUNKS)
                    trj = trj.reshape((-1, self.natoms * 3))
                    trj = trj - self._avg.flatten()
                    cov = da.dot(trj.T, trj.conj()).compute()
                    cv = comm.allreduce(cov)
                    cv = cv / self.nframes
        else:
            # Covariance matrix supplied. This requires that the corresponding
            # target structure is given as well.
            if target is None:
                raise ValueError('A defined covariance matrix requires'
                                 + ' a defined target.')
            else:
                self._avg = da.from_array(target, chunks=CHUNKS)
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

        self._evals = w[-1:-(i + 1):-1]
        self._evecs = v[:, -1:-(i + 1):-1].T
        time_diag_cov_1 = time()
        if self.rank == 0:
            log.info( 'Pcz: Time for diagonalizing covariance matrix: '
                     + '{0:.2f} s\n'.format(time_diag_cov_1 - time_diag_cov_0))

        time_proj_calc_0 = time()
        avg = self._avg

        if comm is not None:
            blocksize = len(cofasu) / self.size
            if blocksize * self.size < len(cofasu):
                blocksize += 1
            if self.rank == 0:
                log.info('Pcz: Calculating projections with '
                         + 'blocksize {}'.format(blocksize))
            start = self.rank * blocksize
            end = min(start + blocksize, len(cofasu))
            trj = cofasu.x[start:end].reshape((-1, self.natoms * 3))
            trj = trj - self._avg.flatten()
            evecs = da.from_array(self._evecs, chunks=CHUNKS)
            projs = da.dot(trj, evecs.T).T.compute()
            self._projs = np.hstack(comm.allgather(projs))
        else:
            trj = (cofasu.x - avg).reshape((-1, self.natoms*3))
            evecs = da.from_array(self._evecs, chunks=CHUNKS)
            self._projs = da.dot(trj, evecs.T).T.compute()

        time_proj_calc_1 = time()
        if self.rank == 0:
            log.info('Pcz: Time for calculating projections: '
                     + '{0:.2f} s'.format(time_proj_calc_1 - time_proj_calc_0))

    def avg(self):
        """
        Returns the average structure contained in the pcz file
        as an (natoms,3) numpy array.
        >>> topfile = "../../../../test/2ozq.pdb"
        >>> trjfile = "../../../../test/2ozq.dcd"
        >>> from MDPlus.core import cofasu
        >>> f = cofasu.Fasu(topfile, trjfile, selection='name CA')
        >>> c = cofasu.Cofasu(f)
        >>> p = Pcz(c)
        >>> print(np.allclose(p.avg()[0], 
        ...       np.array([ 31.323149, 61.575380, 40.136298]), 
        ...       atol=0.001, rtol=0.001))
        True

        """
        return self._avg.compute()

    def eval(self, ival):
        """
        Returns an eigenvalue from the file.
        >>> topfile = "../../../../test/2ozq.pdb"
        >>> trjfile = "../../../../test/2ozq.dcd"
        >>> from MDPlus.core import cofasu
        >>> f = cofasu.Fasu(topfile, trjfile, selection='name CA')
        >>> c = cofasu.Cofasu(f)
        >>> p = Pcz(c)
        >>> print(np.allclose(p.eval(4), 
        ...       np.array([2.6183940]), rtol=0.001, atol=0.001))
        True

        """
        if ival >= self.nvecs:
            print 'Error - only ', self.nvecs, ' eigenvectors present'
            return 0.0
        else:
            return self._evals[ival]

    def evals(self):
        """
        Returns an array of all eigenvalues in the file.
        >>> topfile = "../../../../test/2ozq.pdb"
        >>> trjfile = "../../../../test/2ozq.dcd"
        >>> from MDPlus.core import cofasu
        >>> f = cofasu.Fasu(topfile, trjfile, selection='name CA')
        >>> c = cofasu.Cofasu(f)
        >>> p = Pcz(c)
        >>> print(np.allclose(p.evals()[4], 
        ...       np.array([2.6183940]), rtol=0.001, atol=0.001))
        True

        """
        return self._evals

    def evec(self, ivec):
        """
        Returns a chosen eigenvector from the file in the
        form of a (3*natoms) numpy array.
        >>> topfile = "../../../../test/2ozq.pdb"
        >>> trjfile = "../../../../test/2ozq.dcd"
        >>> from MDPlus.core import cofasu
        >>> f = cofasu.Fasu(topfile, trjfile, selection='name CA')
        >>> c = cofasu.Cofasu(f)
        >>> p = Pcz(c)
        >>> print(np.allclose(abs(p.evec(1)[12]), 
        ...       np.array([0.00865751377]), rtol=0.001, atol=0.001))
        True

        """
        if ivec >= self.nvecs:
            print 'Error - only ', self.nvecs, 'eigenvectors present'
            return None
        else:
            return self._evecs[ivec, :]

    def evecs(self):
        """
        Returns all eigenvectors in the file in the form of a
        (nvecs,3*natoms) numpy array.
        >>> topfile = "../../../../test/2ozq.pdb"
        >>> trjfile = "../../../../test/2ozq.dcd"
        >>> from MDPlus.core import cofasu
        >>> f = cofasu.Fasu(topfile, trjfile, selection='name CA')
        >>> c = cofasu.Cofasu(f)
        >>> p = Pcz(c)
        >>> e = p.evecs()
        >>> print(e.shape)
        (18, 471)

        >>> element = abs(e[1,12])
        >>> print(np.allclose(element, 
        ...       np.array([0.0086575138]), rtol=0.001, atol=0.001))
        True

        """
        return self._evecs

    def proj(self, iproj):
        """
        Returns an array of the projections along a given eigenvector. There
        will be one value per snapshot.
        >>> topfile = "../../../../test/2ozq.pdb"
        >>> trjfile = "../../../../test/2ozq.dcd"
        >>> from MDPlus.core import cofasu
        >>> f = cofasu.Fasu(topfile, trjfile, selection='name CA')
        >>> c = cofasu.Cofasu(f)
        >>> p = Pcz(c)
        >>> prj = abs(p.proj(3))
        >>> print(np.allclose(prj[21], 0.3312888, rtol=0.001, atol=0.001))
        True

        """
        if iproj >= self.nvecs:
            print 'Error - only ', self.nvecs, 'eigenvectors present'
            return None
        else:
            return self._projs[iproj, :]

    def scores(self, framenumber):
        """
        Method that returns the scores (projections) corresponding to
        a chosen snapshot (zero-based).
        >>> topfile = "../../../../test/2ozq.pdb"
        >>> trjfile = "../../../../test/2ozq.dcd"
        >>> from MDPlus.core import cofasu
        >>> f = cofasu.Fasu(topfile, trjfile, selection='name CA')
        >>> c = cofasu.Cofasu(f)
        >>> p = Pcz(c)
        >>> s = abs(p.scores(12))
        >>> print(np.allclose(s[3], 0.5800652, rtol=0.001, atol=0.001))
        True

        """
        if( framenumber >= self.nframes):
             return None
        else:
             x = np.zeros(self.nvecs)
             for i in range(self.nvecs):
                 x[i] = self.proj(i)[framenumber]
             return x

    def coords(self, framenumber):
        """
        Synonym for frame() method, to match cofasu.
        """
        return self.frame(framenumber)

    def frame(self,framenumber):
        """
        Method to return the coordinates of the given frame - i.e.
        to decompress a snapshot. The data is returned as a (natoms,3) 
        numpy array.
        >>> topfile = "../../../../test/2ozq.pdb"
        >>> trjfile = "../../../../test/2ozq.dcd"
        >>> from MDPlus.core import cofasu
        >>> f = cofasu.Fasu(topfile, trjfile, selection='name CA')
        >>> c = cofasu.Cofasu(f)
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
        Method to find the index of the frame with scores closest to the
        target values.
        """
        ns = len(scores)
        temp = self._projs

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
        Method to return the coordinates corresponding to a given
        set of scores. If the scores vector has less than nvec elements,
        Pczfile.expand is called to fill in the missing values.
        >>> topfile = "../../../../test/2ozq.pdb"
        >>> trjfile = "../../../../test/2ozq.dcd"
        >>> from MDPlus.core import cofasu
        >>> f = cofasu.Fasu(topfile, trjfile, selection='name CA')
        >>> c = cofasu.Cofasu(f)
        >>> p = Pcz(c)
        >>> a = p.avg()
        >>> a2 = p.unmap(np.zeros(p.nvecs))
        >>> print((abs(a - a2)).mean() < 0.001)
        True

        """
        x = self.avg()
        if len(scores) < self.nvecs:
            scores = self.expand(scores)
        for i in range(self.nvecs):
            x = x + (self.evec(i)*scores[i]).reshape((self.natoms,3))
        return x

    def expand(self, scores):
        """
        Method to complete a truncated list of scores with values for
        missing eigenvectors. Basically the pcz file is scanned to
        find the frame with the best match to the scores given, the
        missing values are then copied directly from this frame.
        >>> topfile = "../../../../test/2ozq.pdb"
        >>> trjfile = "../../../../test/2ozq.dcd"
        >>> from MDPlus.core import cofasu
        >>> f = cofasu.Fasu(topfile, trjfile, selection='name CA')
        >>> c = cofasu.Cofasu(f)
        >>> p = Pcz(c)
        >>> e = abs(p.expand([1.0, 2.0, 3.0]))
        >>> print(np.allclose(e[3:6], 
        ...       [2.5556779, 0.9558872, 2.2131005], rtol=0.001, atol=0.001))
        True

        """
        nvecs = self.nvecs
        ns = len(scores)
        if ns >= nvecs:
            return scores
        else:
            newscores = np.zeros(nvecs)
            newscores[0:ns] = scores
            temp = self._projs
            best = 0
            err = ((temp[0:ns,0]-scores)*(temp[0:ns,0]-scores)).sum()
            newscores[ns:nvecs] = temp[ns:nvecs,0]
            for frame in range(self.nframes):
                newerr = ((temp[0:ns,frame]-scores) 
                          * (temp[0:ns,frame]-scores)).sum()
                if newerr < err:
                    err = newerr
                    newscores[ns:nvecs] = temp[ns:nvecs,frame]
            return newscores

    def map(self,crds):
        """
        Method to map an arbitrary coordinate set onto the PC model. The
        coordinate set should be a (natom,3) array-like object that matches
        (for size) what's in the pczfile. An array of projections will be 
        returned, one value for each eignevector in the pcz file.
        >>> topfile = "../../../../test/2ozq.pdb"
        >>> trjfile = "../../../../test/2ozq.dcd"
        >>> from MDPlus.core import cofasu
        >>> f = cofasu.Fasu(topfile, trjfile, selection='name CA')
        >>> c = cofasu.Cofasu(f)
        >>> p = Pcz(c)
        >>> m = p.scores(10)
        >>> crds = c[10]
        >>> print(np.allclose(abs(p.map(crds)),abs(m), rtol=0.001, atol=0.001))
        True

        """
        c = fastfitting.fitted(crds, self._avg)
        c = c - self._avg
        prj = np.zeros(self.nvecs)
        for i in range(self.nvecs):
             prj[i]=(np.dot(c.flatten(),self.evec(i)))
        return prj
  

    def write(self, filename,  title='Created by pcz.write()'):
        """
        Write out the PCZ file. At the moment only the PCZ4 and PCZ6 formats
        are  implemented.
        """

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
            for v in self.avg().flatten():
                f.write(struct.pack('f', v))
            for i in range(self.nvecs):
                for v in self.evec(i):
                    f.write(struct.pack('f', v))
                f.write(struct.pack('f', self.eval(i)))

                projection = self.proj(i)

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
                             dtype='f', data=self.evecs())
            f.create_dataset("eval_dataset", (self.nvecs,), 
                             dtype='f', data=self.evals())
            # Write reference coordinates
            f.create_dataset("ref_coord_dataset", (len(self.avg().flatten()),),
                             dtype='f', data=np.array(self.avg().flatten()))
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

if __name__ == "__main__":
    import doctest
    doctest.testmod()
