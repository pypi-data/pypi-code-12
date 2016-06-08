import numpy as np
import scipy.stats

from mixem.distribution.distribution import Distribution


class PoissonDistribution(Distribution):
    """Univariate normal distribution with parameters (mu, sigma)."""

    def __init__(self, lmbda, loc):
        self.lmbda = lmbda
        self.loc = 0

    def log_density(self, data):
        assert(len(data.shape) == 1), "Expect 1D data!"

        return - self.lmbda  + data * np.log(self.lmbda)  

        #res = scipy.stats.poisson.pmf(data, self.lmbda, loc=self.sigma)

    def estimate_parameters(self, data, weights):
        assert(len(data.shape) == 1), "Expect 1D data!"

        wsum = np.sum(weights)

        # derivative over lambda of -lambda + x log(lamnda) 
        self.lmbda = np.sum(weights * data) / wsum #- self.loc / self.lmbda


    def __repr__(self):
        return "Poisson[lmbda={lmbda:.4g}, loc={loc:.4g}]".format(lmbda=self.lmbda, loc=self.loc)


