from poap.controller import SerialController, ThreadController, BasicWorkerThread, SimTeamController
from sot_sync_strategies import *
from sot_async_strategies import *
from rbf_interpolant import *
from sampling_methods import *
from rbf_surfaces import *
from rs_capped import *
from numpy.matlib import repmat
from ensemble_surrogate import *
from poly_regression import *
from utils import *

class Ackley:
    def __init__(self, dim=10):
        self.xlow = -15 * np.ones(dim)
        self.xup = 20 * np.ones(dim)
        self.dim = dim
        self.info = str(dim)+"-dimensional Ackley function \n" +\
                             "Global optimum: f(0,0,...,0) = 0"
        self.min = 0
        self.integer = []
        self.continuous = np.arange(0, dim)

    def objfunction(self, x):
        if len(x) != self.dim:
            raise ValueError('Dimension mismatch')
        n = float(len(x))
        return -20.0 * np.exp(-0.2*np.sqrt(sum(x**2)/n)) - \
            np.exp(sum(np.cos(2.0*np.pi*x))/n)


class Rastrigin:
    def __init__(self, dim=10):
        self.xlow = -4 * np.ones(dim)
        self.xup = 5 * np.ones(dim)
        self.dim = dim
        self.info = str(dim)+"-dimensional Rastrigin function \n" +\
                             "Global optimum: f(0,0,...,0) = 0"
        self.min = 0
        self.integer = []
        self.continuous = np.arange(0, dim)

    def objfunction(self, x):
        if len(x) != self.dim:
            raise ValueError('Dimension mismatch')
        return np.sum(x**2 - np.cos(2 * np.pi * x))


class Griewank:
    def __init__(self, dim=10):
        self.xlow = -500 * np.ones(dim)
        self.xup = 700 * np.ones(dim)
        self.dim = dim
        self.info = str(dim)+"-dimensional Griewank function \n" +\
                             "Global optimum: f(0,0,...,0) = 0"
        self.min = 0
        self.integer = []
        self.continuous = np.arange(0, dim)

    def objfunction(self, x):
        if len(x) != self.dim:
            raise ValueError('Dimension mismatch')
        total = 1
        for i, y in enumerate(x):
            total *= np.cos(y / np.sqrt(i+1))
        return 1.0 / 4000.0 * sum([y**2 for y in x]) - total + 1


class Michalewicz:
    def __init__(self, dim=10):
        self.xlow = np.zeros(dim)
        self.xup = np.pi * np.ones(dim)
        self.dim = dim
        self.info = str(dim)+"-dimensional Michalewicz function \n" +\
                             "Global optimum: ??"
        self.min = np.NaN
        self.integer = []
        self.continuous = np.arange(0, dim)

    def objfunction(self, x):
        if len(x) != self.dim:
            raise ValueError('Dimension mismatch')
        return -np.sum(np.sin(x) * (np.sin(((1 + np.arange(self.dim)) * x ** 2)/np.pi)) ** 20)


class Keane:
    def __init__(self, dim=30):
        self.xlow = 1.0 * np.ones(dim)
        self.xup = 10.0 * np.ones(dim)
        self.dim = dim
        self.min = -0.835
        self.integer = []
        self.continuous = np.arange(0, dim)
        self.info = str(dim)+"-dimensional Keane bump function \n" +\
                             "Global optimum: -0.835 for large n"

    def objfunction(self, x):
        d = len(x)
        y1 = 0.0
        y2 = 1.0
        y3 = 0.0

        for i in range(d):
            y1 += (np.cos(x[i]) ** 4)

        for i in range(d):
            y2 *= (np.cos(x[i]) ** 2)

        for i in range(d):
            y3 += (i+1) * (x[i] ** 2)

        y = (y1 - 2.0 * y2) / np.sqrt(y3)

        return - np.abs(y)


class Rosenbrock:
    def __init__(self, dim=10):
        self.xlow = -2.048 * np.ones(dim)
        self.xup = 2.048 * np.ones(dim)
        self.dim = dim
        self.info = str(dim)+"-dimensional Rosenbrock function \n" +\
                             "Global optimum: f(1,1,...,1) = 0"
        self.min = 0
        self.integer = []
        self.continuous = np.arange(0, dim)

    def objfunction(self, x):
        if len(x) != self.dim:
            raise ValueError('Dimension mismatch')
        total = 0
        for i in range(len(x) - 1):
            total += 100 * (x[i]**2 - x[i+1])**2 + (x[i] - 1)**2
        return total


class Schwefel:
    def __init__(self, dim=10):
        self.xlow = -512 * np.ones(dim)
        self.xup = 512 * np.ones(dim)
        self.dim = dim
        self.info = str(dim)+"-dimensional Schwefel function \n" +\
                             "Global optimum: f(420.968746,...,420.968746) = 0"
        self.min = 0
        self.integer = []
        self.continuous = np.arange(0, dim)

    def objfunction(self, x):
        if len(x) != self.dim:
            raise ValueError('Dimension mismatch')
        return 418.9829 * self.dim - \
            sum([y * np.sin(np.sqrt(abs(y))) for y in x])


class Sphere:
    def __init__(self, dim=10):
        self.xlow = -15 * np.ones(dim)
        self.xup = 20 * np.ones(dim)
        self.dim = dim
        self.info = str(dim)+"-dimensional Sphere function \n" +\
                             "Global optimum: f(0,0,...,0) = 0"
        self.min = 0
        self.integer = []
        self.continuous = np.arange(0, dim)

    def objfunction(self, x):
        """Evaluate the Sphere function  at x

        :param x: Data point
        :return: Value at x
        """
        if len(x) != self.dim:
            raise ValueError('Dimension mismatch')
        return sum(x**2)


class Himmelblau:
    def __init__(self, dim=30):
        self.xlow = -100 * np.ones(dim)
        self.xup = 100 * np.ones(dim)
        self.dim = dim
        self.min = -78.3323
        self.integer = []
        self.continuous = np.arange(0, dim)

    def objfunction(self, x):
        if len(x) != self.dim:
            raise ValueError('Dimension mismatch')
        return (1.0/self.dim) * np.sum(x**4 - 16*(x**2) + 5*x)


class Schwefel2_26:
    def __init__(self, dim=30):
        self.xlow = -500 * np.ones(dim)
        self.xup = 500 * np.ones(dim)
        self.dim = dim
        self.min = -12569.48
        self.integer = []
        self.continuous = np.arange(0, dim)

    def objfunction(self, x):
        if len(x) != self.dim:
            raise ValueError('Dimension mismatch')
        return - np.dot(x, np.sin(np.sqrt(np.abs(x))))


class Exponential:
    def __init__(self, dim=10):
        self.xlow = np.zeros(dim)
        self.xup = 5 * np.ones(dim)
        self.dim = dim
        self.integer = []
        self.continuous = np.arange(0, dim)

    def objfunction(self, x):
        if len(x) != self.dim:
            raise ValueError('Dimension mismatch')
        return np.exp(np.sum(x))


class RotatedSphere:
    def __init__(self, dim=30):
        self.xlow = -100 * np.ones(dim)
        self.xup = 100 * np.ones(dim)
        self.dim = dim
        self.integer = []
        self.continuous = np.arange(0, dim)
        mat = np.random.randn(dim, dim)
        Q, R = np.linalg.qr(mat)
        self.rotation = Q
        self.optimum = np.zeros(dim)

    def objfunction(self, xx):
        if len(xx) != self.dim:
            raise ValueError('Dimension mismatch')
        x = self.optimum + np.dot(self.rotation, (xx - self.optimum))
        return sum(x ** 2)


class Schoen:
    def __init__(self, dim=30, k=None, fi=None, z=None):
        self.xlow = np.zeros(dim)
        self.xup = np.ones(dim)
        self.dim = dim
        self.integer = []
        self.continuous = np.arange(0, dim)
        self.k = k
        if self.k is None:
            self.k = 50
        self.fi = fi
        if self.fi is None:
            self.fi = -np.abs(np.random.randn(self.k, 1).ravel())
        self.z = z
        if self.z is None:
            self.z = np.random.rand(self.k, self.dim)

        self.min = np.amin(self.fi)
        self.optimum = self.z[np.argmin(self.fi), :]

    def objfunction(self, xx):
        if len(xx) != self.dim:
            raise ValueError('Dimension mismatch')
        x = np.atleast_2d(xx)
        prodmat = repmat(np.sum((self.z - x) ** 2, 1), self.k, 1).T
        np.fill_diagonal(prodmat, 1)
        prodvec = np.prod(prodmat, axis=0)
        return np.dot(prodvec, self.fi) / np.sum(prodvec)


def test_ensamble():
    dim = 10
    maxeval = 500
    data = Ackley(dim=dim)

    bounds = np.vstack((data.xlow.T, data.xup.T)).T
    basisp = basis_TD(dim, 2)
    surf = PolyRegression(bounds, basisp)

    models = [
        RBFInterpolant(surftype=CubicRBFSurface, maxp=maxeval),
        surf
    ]
    exp_design = LatinHypercube(dim=data.dim, npts=50)
    X = from_unit_box(exp_design.generate_points(), data)
    response_surface = EnsembleSurrogate(models, maxeval)
    for i in range(exp_design.npts):
        response_surface.add_point(X[i, :], data.objfunction(X[i, :]))

    for i in range(500):
        if response_surface.nump == 50:
            print response_surface.nump
            temp = response_surface.eval(np.zeros(dim,))
        if response_surface.nump == 100:
            print response_surface.nump
            temp = response_surface.eval(np.zeros(dim,))
        if response_surface.nump == 200:
            print response_surface.nump
            temp = response_surface.eval(np.zeros(dim,))
        if response_surface.nump == 300:
            print response_surface.nump
            temp = response_surface.eval(np.zeros(dim,))
        if response_surface.nump == 400:
            print response_surface.nump
            temp = response_surface.eval(np.zeros(dim,))
        if response_surface.nump == 500:
            print response_surface.nump
            temp = response_surface.eval(np.zeros(dim,))
            die
        randpt = from_unit_box(np.random.rand(dim,), data)
        response_surface.add_point(randpt, data.objfunction(randpt))

if __name__ == "__main__":
    nruns = 5
    dim = 30
    maxeval = 500
    nthreads = 1

    datavec = [Ackley(dim=dim), Rastrigin(dim=dim), Griewank(dim=dim), Keane(dim=dim), Michalewicz(dim=dim)]
    for data in datavec:
        print "\n" + data.__class__.__name__

        vals = np.zeros(nruns,)
        for ii in range(nruns):
            controller = SerialController(data.objfunction)

            nsamples = nthreads

            controller.strategy = \
                SyncStrategyNoConstraints(
                    worker_id=0, data=data,
                    maxeval=maxeval, nsamples=nsamples,
                    exp_design=SymmetricLatinHypercube(dim=data.dim, npts=2*(data.dim+1)),
                    response_surface=RBFInterpolant(surftype=CubicRBFSurface, maxp=maxeval),
                    sampling_method=CandidateDYCORS(data=data, numcand=100*data.dim))

            # Run the optimization strategy
            result = controller.run()

            print(result.value)
            vals[ii] = result.value
        print np.min(vals), np.max(vals), np.median(vals), np.mean(vals), np.std(vals)/np.sqrt(nruns)


