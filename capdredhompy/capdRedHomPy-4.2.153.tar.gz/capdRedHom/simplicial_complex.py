from .complex import *

class SimplicialComplex(Complex):

    def __init__(self, simplices, impl=None, **kwargs):
        super(SimplicialComplex, self).__init__(SimplicialComplex._create(simplices, **kwargs) if impl is None else impl)

    @classmethod
    def _create(cls, simplices, **kwargs):
        from .impl import capd_impl
        if 'type' in kwargs:
            impl = capd_impl.SimplicialComplex([sorted(s) for s in simplices], int(kwargs['type']))
        else:
            impl = capd_impl.SimplicialComplex([sorted(s) for s in simplices])

        return impl

    @classmethod
    def from_numpy_array(cls, simplices):
        from .impl import has_numpy_helpers
        if not has_numpy_helpers:
            raise RuntimeError('Please recompile with numpy installed')
        from .impl import numpy_helpers, capd_impl

        import numpy as np
        simplices = np.ascontiguousarray(simplices, dtype=np.int)
        return SimplicialComplex(None, numpy_helpers.SimplicialComplex_create_from_numpy_array(simplices))
