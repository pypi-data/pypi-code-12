import numpy as np
import mdtraj as mdt
import tempfile
import os
import h5py
import logging as log
import dask.bag as db
import dask.array as da
from MDPlus.core import fastfitting
import warnings

# This is the chunks size for dask:
CHUNKS = 10000

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

    def _process(self, hdfdir=None):
        '''
        Private function that processes the Fasu definition, returning 
        the name of an HDF5-format file that contains the required data.

        Arguments:
            hdfdir: 
            The name of the directory in which the HDF5 format file
            will be created. If not given, the OS-defined temporary directory
            is used.
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

        h5filename = tempfile.NamedTemporaryFile(dir=hdfdir).name

        if self.frames is not None:
            x = np.array(u.xyz[self.frames], dtype='float32')
        else:
            x = np.array(u.xyz, dtype='float32')

        if self.centre is not None:
            c = u.top.select(self.centre)
            for i in range(len(x)):
                cx = x[i][c].mean(axis=0)
                if u.unitcell_vectors is None:
                    shift = -cx
                else:
                    shift = u.unitcell_vectors[i].diagonal()/2 - cx
                x[i] = x[i] + shift

        if self.pack_into_box:
            for i in range(len(x)):
                x[i] = pib(x[i], u.unitcell_vectors[i])

        hf = h5py.File(h5filename, 'w')
        hx = hf.create_dataset('x', data=x*10.0)
        hm = hf.create_dataset('m', data=masses)
        if u.unitcell_vectors is not None:
            hb = hf.create_dataset('b', data=u.unitcell_vectors)
        dt = h5py.special_dtype(vlen=unicode)
        hn = hf.create_dataset('n', data=names, dtype=dt)

        hf.close()
        return h5filename

class Cofasu:
    '''
    A collection of Fasus.
    '''

    def __init__(self, fasulist, check=None, hdfdir=None):
        '''
        A Cofasu is created from a list of one or more Fasus:
            c = Cofasu(fasulist)
        or alternatively from a list of already-created HDF5-format files:
            c = Cofasu(hdf5filelist)

        Arguments are:
        fasulist: list.
            list of fasus or pre-processed hdf5-format files

        check: None or string.
            if check is None, fasus are considered legitimate if they match in
            their second dimension (i.e., number of atoms)

            If check is 'names', fasus must also match atom names.

            If check is 'masses', fasus must match for atom masses, but not
            neccessarily names.

        hdfdir: None or string.
            If not None, the name of the temporary directory where the hdf5
            files will be made. 
        '''

        if not isinstance(fasulist, list):
            fasulist = [fasulist,]

        if isinstance(fasulist[0], str):
            self.hflist = fasulist
        else:
            b = db.from_sequence([f._process(hdfdir=hdfdir) 
                                 for f in fasulist])
            self.hflist = b.compute()

        self.hlist = [h5py.File(h, 'r+') for h in self.hflist]
        
        if check is "names":
            nref = self.hlist[0]['n']
            for i in range(1, len(self.hlist)):
                if not (nref[:] == self.hlist[i]['n'][:]).all:
                    raise ValueError('Fasus have mismatched atom names')

        elif check is "masses":
            mref = self.hlist[0]['m']
            for i in range(1, len(self.hlist)):
                if not (mref[:] == self.hlist[i]['m'][:]).all:
                    raise ValueError('Fasus have mismatched atom masses')

        # Update fasu.frames slice definitions now file sizes are known:
        for i in range(len(fasulist)):
            if (isinstance(fasulist[i], Fasu) and 
                    isinstance(fasulist[i].frames, slice)):
                frames = fasulist[i].frames
                if frames.stop == None:
                    l = len(self.hlist[i]['x'])
                    start = frames.start
                    step = frames.step
                    stop = l + 1
                    if step is not None:
                        stop = stop * step
                    if start is not None:
                        stop += start
                    fasulist[i].frames = slice(start, stop, step) 

        xs = [da.from_array(h['x'], chunks=CHUNKS) for h in self.hlist]
        self.x = da.concatenate(xs)
        if all(['b' in h for h in self.hlist]):
            xb = [da.from_array(h['b'], chunks=CHUNKS) for h in self.hlist]
            self.box = da.concatenate(xb)
        else:
            self.box = None
        self.masses = self.hlist[0]['m']
        self.shape = self.shape()
        self.fasulist = fasulist

    def __len__(self):
        return len(self.x)

    def __getitem__(self, key):
        return self.x[key].compute()

    def shape(self):
        return self.x.shape

    def reset(self):
        '''
        Removes any alignment from the trajectories
        '''
        xs = [da.from_array(h['x'], chunks=CHUNKS) for h in self.hlist]
        self.x = da.concatenate(xs)

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
            targ = self.x[0]
            target = targ.compute()
        else:
            targ = da.from_array(target, chunks = CHUNKS)

        if weighted:
            weights = self.masses
        else:
            weights = np.ones_like(self.masses)
        weights = da.from_array(np.stack([weights,] * 3).T, chunks=CHUNKS)

        self.x = da.map_blocks(fastfitting.fitted_traj, self.x, targ, weights)
        if not procrustes:
            return

        avg = self.x.mean(axis=0).compute()
        err = avg - target
        err = (err*err).mean()
        cycle = 1
        self.reset()
        while err > error and cycle < maxcyc:
            target = da.from_array(avg, chunks=CHUNKS)
            oldavg = avg
            x = da.map_blocks(fastfitting.fitted_traj, self.x, 
                                target, weights)
            avg = x.mean(axis=0).compute()
            err = avg - oldavg
            err = (err*err).mean()
            cycle += 1
        log.debug('Procrustes converged in {} cycles'.format(cycle)
                  + ' with error {}'.format(err))
        target = da.from_array(avg, chunks=CHUNKS)
        self.reset()
        self.x = da.map_blocks(fastfitting.fitted_traj, self.x, 
                               target, weights)

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

        if needs_topology:
            u = mdt.load(self.fasulist[0].topology)
            sel = u.top.select(self.fasulist[0].selection)
            u = mdt.load(self.fasulist[0].topology, atom_indices=sel)
            top = u.top

        if coordinates is None:
            coordinates = self.x.compute()

        if ext in ['.xtc', '.trr']:
            coordinates = coordinates * 0.1

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            with mdt.open(filename, 'w') as f:
                if needs_topology:
                    f.write(coordinates, top)
                else:
                    f.write(coordinates)
