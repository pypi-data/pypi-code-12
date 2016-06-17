from .complex import *
import itertools as it

class CubicalComplex(Complex):
    pass

    def __init__(self, size=None, **kwargs):
        from .impl import capd_impl

        if 'impl' in kwargs:
            super(CubicalComplex, self).__init__(kwargs['impl'])
            return

        _cubes = kwargs.get('cubes', [])
        _full_cubes = kwargs.get('full_cubes', [])

        if not size:
            cubes = map(self._convert_cube, _cubes)
            full_cubes = map(self._convert_full_cube, _full_cubes)
            dim = 0
            try:
                dim = len(next(it.chain(cubes, full_cubes)))
            except StopIteration:
                pass

            size = [0]*dim

            for cube in it.chain(cubes, full_cubes):
                for d in xrange(dim):
                    if size[d] < cube[d][0]:
                        size[d] = cube[d][0]
            size = map(lambda x: x + 1, size)
        else:
            dim = len(size)
            cubes = (self._convert_cube(c) for c in _cubes)
            full_cubes = (self._convert_full_cube(c) for c in _full_cubes)

        super(CubicalComplex, self).__init__(capd_impl.CubicalComplex(list(size)))

        for cube in it.chain(cubes, full_cubes):
            assert len(cube) == dim
            assert all(0 <= cube[d][0] < size[d] for d in xrange(dim)), (cube, size)
            self.capd.insert(cube)

        numpy_full_cubes = kwargs.get('numpy_full_cubes', None)
        if numpy_full_cubes is not None:
            from .impl import has_numpy_helpers
            if not has_numpy_helpers:
                raise RuntimeError('Please recompile with numpy installed')
            from .impl import numpy_helpers
            numpy_helpers.CubicalComplex_insert_full_cubes_numpy_array(self.capd, numpy_full_cubes)

        self.fillWithBoundaries()

    def _convert_cube(self, cube):
        return [(b, (e - b > 0)) for b, e in cube]

    def _convert_full_cube(self, cube):
        return [(coor, True) for coor in cube]

    def insertFullCube(self, cube):
        self.capd.insertFullCube(cube)

    def fillWithBoundaries(self):
        self.capd.fillWithBoundaries()

    @classmethod
    def from_full_cube_numpy_array(cls, cubes):
        from .impl import has_numpy_helpers
        if not has_numpy_helpers:
            raise RuntimeError('Please recompile with numpy installed')
        from .impl import numpy_helpers, capd_impl
        import numpy as np

        cubes = np.ascontiguousarray(cubes, dtype=np.uint64)
        return CubicalComplex(impl=numpy_helpers.CubicalComplex_create_from_full_cube_numpy_array(cubes))

    @classmethod
    def from_numpy_array(cls, data):
        from .impl import has_numpy_helpers
        if not has_numpy_helpers:
            raise RuntimeError('Please recompile with numpy installed')
        from .impl import numpy_helpers, capd_impl
        import numpy as np

        shape = data.shape
        data = np.ascontiguousarray(data, dtype=np.uint64).reshape(-1)

        assert all(x%2 == 1 for x in shape)


        shape = map(lambda x: x/2, shape)
        shape = np.ascontiguousarray(shape, dtype=np.uint64)

        complex = CubicalComplex(impl=numpy_helpers.CubicalComplex_create_from_numpy_array(data, shape))
        complex._numpy_data = data
        return complex
