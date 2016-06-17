from .complex import *

class GeneralizedComplex(Complex):

    def __init__(self, impl=None):
        super(GeneralizedComplex, self).__init__(impl)

    @classmethod
    def from_numpy_kappa_map(cls, kappa_map, dims):
        from .impl import has_numpy_helpers
        if not has_numpy_helpers:
            raise RuntimeError('Please recompile with numpy installed')
        from .impl import numpy_helpers, capd_impl

        return GeneralizedComplex(numpy_helpers.GeneralizedComplex_from_numpy_kappa_map(kappa_map, dims))
