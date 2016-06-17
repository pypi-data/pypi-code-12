class BettiNumbersOverZ(object):

    def __init__(self, complex):
        self._complex = complex

    def __call__(self):
        from .impl import capd_impl
        complex_impl = self._complex.capd
        betti = capd_impl.BettiNumbersOverZ(complex_impl)()
        return dict(enumerate(betti))

def ComputeBettiNumbers(complex, modulo=0):
        from .impl import capd_impl
        betti = capd_impl.ComputeBettiNumbers(complex.capd, modulo)
        return dict(enumerate(betti))


class FundamentalGroup(object):

    def __init__(self, complex, method):
        self._complex = complex
        self._method = method

    def __call__(self):
        from .impl import capd_impl
        complex_impl = self._complex.capd
        relators = capd_impl.FundamentalGroup(complex_impl, self._method)()
        return relators


class CountCriticalCells(object):

    def __init__(self, complex, method):
        self._complex = complex
        self._method = method

    def __call__(self):
        from .impl import capd_impl
        complex_impl = self._complex.capd
        cc = capd_impl.CountCriticalCells(complex_impl, self._method)()
        return cc

class GenerateKappaMap(object):
    def __init__(self, complex):
        self._complex = complex

    def __call__(self):
        from .impl import capd_impl
        from .impl import has_numpy_helpers
        if not has_numpy_helpers:
            raise RuntimeError('Please recompile with numpy installed')
        from .impl import numpy_helpers
        import numpy as np

        complex_impl = self._complex.capd
        kappaGen = capd_impl.GenerateKappaMap(complex_impl)
        kappaMap = np.zeros((kappaGen.kappaSize(), 3), dtype=np.int_);
        dims = np.zeros((kappaGen.dimsSize()), dtype=np.uint8);

        numpy_helpers.Complex_store_in_numpy_arrays(kappaGen, kappaMap, dims)

        return dims, kappaMap

class BuildMultivectorDynamicsOnGrid(object):

    @classmethod
    def Enabled(cls):
        from .impl import capd_impl
        return capd_impl.BuildMultivectorDynamicsOnGrid.Enabled()


    def __init__(self, coordinates, mapping, radius, epsilon):
        from .impl import capd_impl
        self._impl = capd_impl.BuildMultivectorDynamicsOnGrid(coordinates, mapping, radius, epsilon)

    def __call__(self):
        return self._impl()


class BuildMultivectorDynamicsOnCellCodeMap(object):

    @classmethod
    def Enabled(cls):
        from .impl import capd_impl
        return capd_impl.BuildMultivectorDynamicsOnCellCodeMap.Enabled()

    def __init__(self, complex, map):
        from .impl import capd_impl
        self._impl = capd_impl.BuildMultivectorDynamicsOnCellCodeMap(complex.capd, map)

    def __call__(self):
        return self._impl()
