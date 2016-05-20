import numpy as np
import mdtraj as mdt
import tempfile
import os
import logging as log
from MDPlus.core import fastfitting
import warnings

def pib(coords, box):
    '''
    Pack coordinates into periodic box
    '''

    assert len(coords.shape) == 2
    assert coords.shape[1] == 3
    assert box.shape == (3, 3)

    boxinv = np.zeros((3))
    boxinv[0] = 1.0 / box[0,0]
    boxinv[1] = 1.0 / box[1,1]
    boxinv[2] = 1.0 / box[2,2]

    for xyz in coords:
        s = np.floor(xyz[2] * boxinv[2])
        xyz[2] -= s * box[2,2]
        xyz[1] -= s * box[2,1]
        xyz[0] -= s * box[2,0]

        s = np.floor(xyz[1] * boxinv[1])
        xyz[1] -= s * box[1,1]
        xyz[0] -= s * box[1,0]

        s = np.floor(xyz[0] * boxinv[0])
        xyz[0] -= s * box[0,0]

    return coords

class Fasu:
    def __init__(self, topology, trajectory, frames=None, selection='all', 
    centre=None, pack_into_box=False):
        '''
        A Fasu defines the required data to be extracted from one or more
        trajectory files.

        Arguments are:
        topology:   
            name of a topology file compliant with the trajectory files(s).
        trajectory: 
            list of one or more trajectory files.
        frames:     
            selection of trajectory frames to include. Can be a slice object, 
            or a numpy array.
        selection:  
            MDTraj-compliant atom selection string.
        centre:     
            If not None, an MDTraj-compliant atom selection string that defines
            atoms whose geometric centre will be moved to the centre of the 
            periodic box (if there is one), or to the origin (if there isn't).
        pack_into_box: 
            if True, all coordinates will be imaged into the primary unit cell,
            after any centering has been done.

        '''
        test = open(topology, 'r')
        test.close()

        self.topology = topology
        self.trajectory = trajectory
        if not isinstance(trajectory, list):
            self.trajectory = [trajectory,]

        for t in self.trajectory:
            test = open(t, 'r')
            test.close()

        if frames is not None:
            if not (isinstance(frames, slice) or 
                    isinstance(frames, np.ndarray)):
                raise TypeError('frames must be a slice object or numpy array')
        if frames is None:
            frames = slice(0, None, 1)

        self.frames = frames
        self.selection = selection
        self.centre = centre
        self.pack_into_box = pack_into_box

    def _process(self):
        '''
        Private function that processes the Fasu definition

        '''

        u = mdt.load(self.topology)
        self.sel = u.top.select(self.selection)
        ext = os.path.splitext(self.trajectory[0])[1].lower()
        if not ext in ['gro', 'pdb']:
            u = mdt.load(self.trajectory, top=self.topology, 
                         atom_indices=self.sel)
        else:
            u = mdt.load(self.trajectory, atom_indices=self.sel)

        masses = [atom.element.mass for atom in u.top.atoms]
        masses = np.array(masses, dtype='float32')
        names = [u.top.atom(i).name for i in range(u.n_atoms)]

        if self.frames is not None:
            x = np.array(u.xyz[self.frames], dtype='float32')
        else:
            x = np.array(u.xyz, dtype='float32')

        if self.centre is not None:
            c = u.top.select(self.centre)
            if len(c) == 0:
                raise ValueError('Atom selection for centering matches no atoms.')
            for i in range(len(x)):
                try:
                    cx = x[i][c].mean(axis=0)
                except IndexError:
                    print c
                    raise
                if u.unitcell_vectors is None:
                    shift = -cx
                else:
                    shift = u.unitcell_vectors[i].diagonal()/2 - cx
                x[i] = x[i] + shift

        if self.pack_into_box:
            for i in range(len(x)):
                x[i] = pib(x[i], u.unitcell_vectors[i])

        self.x = x * 10.0
        self.masses = masses
        self.names = names
        self.u = u
        self.shape = x.shape

    def _reload(self):
        '''
        reload the coordinates from the trajectory file
        '''
        if self.frames is not None:
            x = np.array(self.u.xyz[self.frames], dtype='float32')
        else:
            x = np.array(self.u.xyz, dtype='float32')

        if self.centre is not None:
            c = self.u.top.select(self.centre)
            if len(c) == 0:
                raise ValueError('Atom selection for centreing matches no atoms.')
            for i in range(len(x)):
                try:
                    cx = x[i][c].mean(axis=0)
                except IndexError:
                    print c
                    raise
                if self.u.unitcell_vectors is None:
                    shift = -cx
                else:
                    shift = self.u.unitcell_vectors[i].diagonal()/2 - cx
                x[i] = x[i] + shift

        if self.pack_into_box:
            for i in range(len(x)):
                x[i] = pib(x[i], self.u.unitcell_vectors[i])

        self.x = x * 10.0

class Cofasu:
    '''
    A collection of Fasus.
    '''

    def __init__(self, fasulist, check=None, comm=None):
        '''
        A Cofasu is created from a list of one or more Fasus:
            c = Cofasu(fasulist)

        Arguments are:
        fasulist: list.
            list of fasus 

        check: None or string.
            if check is None, fasus are considered legitimate if they match in
            their second dimension (i.e., number of atoms)

            If check is 'names', fasus must also match atom names.

            If check is 'masses', fasus must match for atom masses, but not
            neccessarily names.

        comm: None or MPI communicator.
            if not none, MPI is used where possible.
        '''

        if comm is not None:
            rank = comm.Get_rank()
            size = comm.Get_size()
        else:
            rank = 0
            size = 1

        if not isinstance(fasulist, list):
            fasulist = [fasulist,]

        nfasus = len(fasulist)
        for ifas in range(nfasus):
            fasulist[ifas].owner = size * ifas / nfasus

        for f in fasulist:
            if f.owner == rank:
                f._process()
            else:
                f.names = None
                f.masses = None
                f.shape = None
                f.x = None

        for f in fasulist:
            if comm is not None:
                f.masses = comm.bcast(f.masses, root=f.owner)
                f.names = comm.bcast(f.names, root=f.owner)
                f.shape = comm.bcast(f.shape, root=f.owner)
                if f.x is None:
                    f.x = np.array((1, f.shape[1], f.shape[2]), dtype='float32')
        
        nats = fasulist[0].shape[1]
        for i in range(1, len(fasulist)):
            if not fasulist[i].shape[1] == nats:
                raise ValueError('Fasus have mismatched number of atoms')

        if check is "names":
            nref = fasulist[0].names
            for i in range(1, len(fasulist)):
                if not (nref[:] == fasulist[i].names[:]).all:
                    raise ValueError('Fasus have mismatched atom names')

        elif check is "masses":
            mref = self.fasulist[0].masses
            for i in range(1, len(self.fasulist)):
                if not (mref[:] == fasulist[i].masses[:]).all:
                    raise ValueError('Fasus have mismatched atom masses')

        # Update fasu.frames slice definitions now file sizes are known:
        for i in range(len(fasulist)):
            if isinstance(fasulist[i].frames, slice):
                frames = fasulist[i].frames
                if frames.stop == None:
                    l = fasulist[i].shape[0]
                    start = frames.start
                    step = frames.step
                    stop = l + 1
                    if step is not None:
                        stop = stop * step
                    if start is not None:
                        stop += start
                    fasulist[i].frames = slice(start, stop, step) 

        self.masses = fasulist[0].masses
        totframes = 0
        for f in fasulist:
            totframes += f.shape[0]
        self.shape = (totframes, fasulist[0].shape[1], fasulist[0].shape[2])
        self.fasulist = fasulist
        self.comm = comm
        self.avg = self.average()

    def x(self, key):

        if type(key) is tuple:
            _key1 = key[0]
            if type(_key1) is int:
                _key1 = slice(_key1, _key1+1)
            _key2 = key[1]
            if len(key) == 3:
                _key3 = key[2]
            else:
                _key3 = None

        elif type(key) is int:
            _key1 = slice(key, key+1)
            _key2 = None
            _key3 = None

        elif type(key) is slice:
            _key1 = key
            _key2 = None
            _key3 = None

        totsize = self.shape[0]
        indx = range(totsize)[_key1]
        newsize = len(indx)

        reverse = False
        if indx[-1] < indx[0]:
            reverse = True
            indx = indx[::-1]
        maxval = 0
        j = 0
        x = []
        y = []
        sizes = [f.shape[0] for f in self.fasulist]
        for size in sizes:
            ix = []
            iy = []
            minval = maxval
            maxval += size
            while j < len(indx) and indx[j] < maxval:
                ix.append(j)
                iy.append(indx[j] - minval)
                j += 1
            x.append(ix)
            y.append(iy)
        if reverse:
            for ix in x:
                for v in ix:
                    v = len(indx) - v
            for iy in y:
                 iy = iy.reverse()

        _x = np.zeros((newsize, self.shape[1], self.shape[2]), dtype='float32')
        for i in range(len(self.fasulist)):
            f = self.fasulist[i]
            if self.comm is not None:
                _x[x[i]] = self.comm.bcast(f.x[y[i]], root=f.owner)
            else:
                _x[x[i]] = f.x[y[i]]
        if _key2 is not None:
            if _key3 is not None:
                _x = _x[(slice(0,len(_x)), _key2, _key3)]
            else:
                _x = _x[(slice(0,len(_x)), _key2)]
        if len(_x) == 1:
            _x = _x[0]
        return _x

    def __len__(self):
        return self.shape[0]

    def __getitem__(self, key):
        return self.x(key)

    def shape(self):
        return self.shape

    def reset(self):
        '''
        Removes any alignment from the trajectories
        '''
        if self.comm is None:
            rank = 0
        else:
            rank = self.comm.Get_rank()
        for f in self.fasulist:
            if f.owner == rank:
                f._reload()

        self.avg = self.average()

    def average(self):
        '''
        The mean structure, without any extra fitting process
        '''
        if self.comm is None:
            rank = 0
        else:
            rank = self.comm.Get_rank()

        sum = np.zeros((self.shape[1], self.shape[2]), dtype='float32')
        for f in self.fasulist:
            if f.owner == rank:
                sum += f.x.sum(axis=0)
        if self.comm is not None:
            tsum = self.comm.allreduce(sum)
        else:
            tsum = sum

        return  tsum/len(self)

    def align(self, target=None, weighted=False, procrustes=False,
    error=0.0001, maxcyc=10):
        '''
        Aligns the frames in a trajectory to some reference structure, with
        optional mass-weighting.

        Arguments:
            target:
            If given, a reference structure to fir to, as a [N,3] numpy array.

            weighted:
            If specified, mass-weighted fitting is done.

            procrustes:
            If specified , procrustes iterative fitting is done to convergence.

            error:
            Defines the target error for the procrustes fit.

            maxcyc:
            Defines the maximum number of iterations for the procrustes method.
        '''

        self.reset()
        if target is None:
            targ = self[0]
        else:
            targ = target

        if weighted:
            weights = self.masses
        else:
            weights = np.ones_like(self.masses)
        weights = np.array([weights,] * 3).T

        if self.comm is None:
            rank = 0
        else:
            rank = self.comm.Get_rank()
        for f in self.fasulist:
            if f.owner ==  rank:
                f.x = fastfitting.fitted_traj(f.x, targ, weights)

        self.avg = self.average()
            
        if not procrustes:
            return

        err = self.avg - targ
        err = (err*err).mean()
        cycle = 1
        while err > error and cycle < maxcyc:
            target = self.avg
            oldavg = self.avg
            self.reset()
            for f in self.fasulist:
                if f.owner ==  rank:
                    f.x = fastfitting.fitted_traj(f.x, target, weights)

            self.avg = self.average()
            
            err = self.avg - oldavg
            err = (err*err).mean()
            cycle += 1
        if self.comm is None or rank == 0:
            log.debug('Procrustes converged in {} cycles'.format(cycle)
                      + ' with error {}'.format(err))

    def write(self, filename, coordinates=None):
        '''
        Writes selected data to an output file, of format specified by the
        given filename's extension.

        Arguments:
            filename:
            Name of the file to be written. All MDTraj-supported formats are
            available.

            coordinates:
            An [nframes, natoms, 3] numpy array defining what will be written,
            else all frames in the Cofasu will be output.
        '''

        # Note: currently ignores box data.
        ext = os.path.splitext(filename)[1].lower()
        needs_topology = ext in ['.gro', '.pdb']

        if self.comm is not None:
            rank = self.comm.Get_rank()
        else:
            rank = 0

        if needs_topology:
            if rank == 0:
                u = mdt.load(self.fasulist[0].topology)
                sel = u.top.select(self.fasulist[0].selection)
                u = mdt.load(self.fasulist[0].topology, atom_indices=sel)
                top = u.top

        if coordinates is None:
            coordinates = self[:]

        if ext in ['.xtc', '.trr']:
            coordinates = coordinates * 0.1
        if ext in '.gro' and coordinates.ndim == 2:
            coordinates = np.array([coordinates,])
        if rank == 0:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                with mdt.open(filename, 'w') as f:
                    if needs_topology:
                        f.write(coordinates, top)
                    else:
                        f.write(coordinates)
