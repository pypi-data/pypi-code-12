from .complex import *

class ProdSimplicialComplex(Complex):

    def __init__(self, simplices, impl=None):
        super(ProdSimplicialComplex, self).__init__(ProdSimplicialComplex._create(simplices) if impl is None else impl)

    @classmethod
    def _create(cls, simplices):
        from .impl import capd_impl
        impl = capd_impl.ProdSimplicialComplex([sorted(s) for s in simplices])

        return impl
