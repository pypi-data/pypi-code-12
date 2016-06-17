from .cubical_complex import *
from .simplicial_complex import *
from .prod_simplicial_complex import *
from .generalized_complex import *
from collections import deque
import ast

def read_dat(filename):
    facets = deque()
    with open(filename, 'r') as input:
        for line in input:
            simplex = map(int, line.split())
            facets.append(simplex)

    complex = SimplicialComplex(list(facets))
    return complex

def read_pcub(filename):
    cubes = deque()
    with open(filename, 'r') as input:
        for line in input:
            cube = ast.literal_eval(line)
            cubes.append(cube)

    complex = CubicalComplex(cubes=list(cubes))
    return complex

def read_cub(filename):
    cubes = deque()
    with open(filename, 'r') as input:
        for line in input:
            cube = None
            try:
                cube = map(int, line.split())
            except ValueError:
                cube = ast.literal_eval(line)
            assert cube is not None
            if len(cube) > 0:
                cubes.append(cube)

    complex = CubicalComplex(full_cubes=list(cubes))
    return complex

def read_dat_hdf5(filename):
    import h5py as h
    f=h.File(filename, "r")
    dset = next(f[x] for x in f)
    arr = dset[()]
    complex = SimplicialComplex.from_numpy_array(arr)
    del arr
    return complex

def read_fcub_hdf5(filename):
    import h5py as h
    f=h.File(filename, "r")
    dset = next(f[x] for x in f)
    arr = dset[()]
    complex = CubicalComplex.from_full_cube_numpy_array(arr)
    del arr
    return complex

def read_cmem_hdf5(filename):
    import h5py as h
    f=h.File(filename, "r")
    dset = next(f[x] for x in f)
    arr = dset[()]
    complex = CubicalComplex.from_numpy_array(arr)
    del arr
    return complex

def read_gen_hdf5(filename):
    import h5py as h
    f=h.File(filename, "r")
    kappa_map = f['/kappa_map'][()]
    dims = f['/dims'][()]
    complex = GeneralizedComplex.from_numpy_kappa_map(kappa_map, dims)
    del kappa_map
    del dims
    return complex

def read_prod_simplicial(filename):
    facets = deque()
    with open(filename, 'r') as input:
        for line in input:
            coords =  map(int, line.split())
            prod_simplex = [(coords[i], coords[i+1]) for i in xrange(0, len(coords), 2)]
            facets.append(prod_simplex)

    complex = ProdSimplicialComplex(list(facets))
    return complex

def read(filename):
    if filename.endswith('.dat'):
        return read_dat(filename)
    elif filename.endswith('.pcub_py'):
        return read_pcub(filename)
    elif filename.endswith('.cub'):
        return read_cub(filename)
    elif filename.endswith('.dat.hdf5'):
        return read_dat_hdf5(filename)
    elif filename.endswith('.fcub.hdf5'):
        return read_fcub_hdf5(filename)
    elif filename.endswith('.cmem.hdf5'):
        return read_cmem_hdf5(filename)
    elif filename.endswith('.gen.hdf5'):
        return read_gen_hdf5(filename)
    elif filename.endswith('.pdat'):
        return read_prod_simplicial(filename)
    else:
        raise RuntimeError("Supported file types: {}".format(['.dat', '.pcub_py', '.cub', '.dat.hdf5', '.gen.hdf5', '.fcub.hdf5', '.cmem.hdf5']))
