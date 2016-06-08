# source
# http://nbviewer.ipython.org/github/tritemio/notebooks/blob/master/Mixture_Model_Fitting.ipynb
from easydev import DevTools
devtools = DevTools()
from scipy.optimize import minimize, show_options
import numpy as np
import pylab
from easydev import AttrDict, do_profile
import scipy.stats
from . import criteria
import numpy as np

half_log_two_pi = 0.5*np.log(2*np.pi)

class Model(object):
    def __init__(self):
        pass
    def log_density(self, data):
        raise NotImplementedError
    def estimate(self, data, weights):
        raise NotImplementedError
    def generate(self):
        raise NotImplementedError
    def pdf(self):
        raise NotImplementedError
    def __repr__(self):
        raise NotImplementedError


class GaussianModel(Model):
    def __init__(self, mu=1, sigma=1):
        super(GaussianModel, self).__init__()
        self.mu = mu
        self.sigma = sigma
    def log_density(self, data):
        # log of gaussian distribution
        res = -(data-self.mu)**2 / (2 * self.sigma**2)
        res += - np.log(self.sigma)  - half_log_two_pi
        return res
    def estimate(self, data, weights=None):
        assert(len(data.shape) == 1), "Expect 1D data!"
        # d L/ dmu ==0 and dL/dsigma==0
        if weights:
            wsum = np.sum(weights)
            self.mu = np.sum(weights * data) / wsum
            self.sigma = np.sqrt(np.sum(weights * (data - self.mu) ** 2) / wsum)
        else:
            self.mu = np.sum(data)
            self.sigma = np.sqrt(np.sum( (data - self.mu) ** 2) )
    def generate(self, N):
        return np.array([scipy.stats.norm.rvs(self.mu, self.sigma) for this in range(N)])
    def pdf(self,data):
        pass


class PoissonModel(Model):
    def __init__(self, lmbda=10):
        super(PoissonModel, self).__init__()
        self.lmbda = lmbda
    def log_density(self, data):
        # log of gaussian distribution
        return - self.lmbda + data * np.log(self.lmbda)
    def estimate(self, data, weights=None):
        assert(len(data.shape) == 1), "Expect 1D data!"
        # d L/ dmu ==0 and dL/dsigma==0
        if weights:
            wsum = np.sum(weights)
            self.lmbda = np.sum(weights * data) / wsum
        else:
            self.lmbda = np.sum(data)
    def generate(self, N):
        return np.array([scipy.stats.poisson.rvs(self.lmbda) for this in range(N)])
    def __repr__(self):
        return "Poisson[lmbda={lmbda:.4g}]".format(lmbda=self.lmbda)


class MixtureModel(object):
    def __init__(self, mixture=[0.5,0.5], N=1000):
        self.N = N
        self.data = []
        self.mixture = mixture
        self.Ns = [int(x*N) for x in mixture]
        if sum(self.Ns) != N:
            print('Warning: rounding mixture ratio. total N will be %s' %
                    sum(self.Ns))
        self.type = "continuous"

    def generate(self):
        raise NotImplementedError

    def plot(self, bins=30, normed=True):
        self.hist(bins=bins, normed=normed)

    def hist(self, bins=30, normed=True):
        pylab.hist(self.data, bins=bins, normed=normed)


class GaussianMixtureModel(MixtureModel):
    """Creates a mix of Gaussian distribution

    .. plot::
        :width: 80%
        :include-source:

        from biokit.stats.mixture import GaussianMixture
        gmm = GaussianMixtureModel()
        gmm.hist(60)
        X = linsapce(-6,6,100)
        plot(X, gmm.pdf(X, [-2,1,0.3,2,1,0.7]), lw=3, color='k')

    """
    def __init__(self, mu=[-2,2], sigma=[1,1], mixture=[0.3,0.7], N=10000):
        """.. rubric:: constructor

        :param list mu: list of mean for each model
        :param list sigma: list of standard deviation for each model
        :param list mixture: list of amplitude for each model

        """
        super(GaussianMixtureModel, self).__init__(mixture, N)
        assert len(mu) == len(sigma)
        assert len(mu) == len(mixture)
        self.mu = mu
        self.sigma = sigma
        self.k = len(self.mu)
        self.model = scipy.stats.poisson
        self.name = "gaussian"

    def generate(self):
        self.data = []
        for m, s, n in zip(self.mu, self.sigma, self.Ns):
            data = GaussianModel(m, s).generate(n)
            self.data.extend(data)
        self.data = np.array(self.data)
        return self.data

    def pdf(self, x, params, normalise=True):
        """Expected parameters are

        params is a list of gaussian distribution ordered as mu, sigma, pi,
        mu2, sigma2, pi2, ...

        """
        assert divmod(len(params), 3)[1] == 0
        k = len(params) / 3
        pis = np.array(params[2::3])

        if any(np.array(pis)<0):
            return 0
        if normalise is True:
            pis /= pis.sum()
        # !!! sum pi must equal 1 otherwise may diverge badly
        data = 0
        for i in range(0, int(k)):
            mu, sigma, pi_ = params[i*3: (i+1)*3]
            pi_ = pis[i]
            if sigma != 0:
                data += pi_ * pylab.normpdf(x, mu, sigma)
        return data


class PoissonMixtureModel(MixtureModel):
    """

        pmm = PoissonMixtureModel([5,20], [0.4,0.6], N=10000)
        hist(pmm.generate(), range(40), normed=True)
        plot([x+0.5 for x in range(40)], gmm.pdf(range(40), [5,0.4,20,0.6]), lw=4, color='k')

    """

    def __init__(self, lmbda=[5,20], mixture=[0.4,0.6], N=10000):
        super(PoissonMixtureModel, self).__init__(mixture, N)
        assert len(lmbda) == len(mixture)
        self.lmbda = lmbda
        self.model = scipy.stats.poisson.pmf
        self.name = "poisson"

    def generate(self):
        self.data = []
        for m, n in zip(self.lmbda, self.Ns):
            data = PoissonModel(m).generate(n)
            self.data.extend(data)
        self.data = np.array(self.data)
        return self.data

    def pdf(self, x, params, normalise=True):
        assert divmod(len(params), 2)[1] == 0
        k = len(params) / 2

        pis = np.array(params[1::2])

        if any(np.array(pis)<0):
            return 0
        if normalise is True:
            pis /= pis.sum()
        # !!! sum pi must equal 1 otherwise may diverge badly
        data = 0
        for i in range(0, int(k)):
            mu, pi_ = params[i*2: (i+1)*2]
            pi_ = pis[i]
            mu = int(mu)
            data += pi_ * scipy.stats.poisson.pmf(x, mu)
        return data

    def log_likelihood(self, params, sample):
        data = self.pdf(sample, params)
        data = [x if x!=0 else 1e-16 for x in sample]
        res =  -1 * pylab.log(data).sum()
        return res


class Fitting(object):
    """Base class for :class:`EM` and :class:`GaussianMixtureFitting`"""
    def __init__(self, data, k=2, method='Nelder-Mead', distribution="gaussian"):
        """.. rubric:: constructor

        :param list data:
        :param int k: number of GMM to use
        :param str method: minimization method to be used (one of scipy optimise module)

        """
        self.data = np.array(data)
        self.size = float(len(self.data))
        self._k = k
        self._model = None
        self._method = method
        # initialise the model
        self.distribution = distribution
        self.k = k
        self.verbose = True

    def _get_method(self):
        return self._method
    def _set_method(self, method):
        devtools.check_param_in_list(method, ['Nelder-Mead',
            'Powell', 'CG', 'BFGS', 'Newton-CG', 'Anneal', 'L-BFGS-B', "SLSQP"])
        self._method = method
    method = property(_get_method, _set_method)

    def _get_k(self):
        return self._k
    def _set_k(self, k):
        assert k > 0
        self._k = k
        if self.distribution == "gaussian":
            self._model = GaussianMixtureModel()
        elif self.distribution == "poisson":
            self._model = PoissonMixtureModel()
        
    k = property(_get_k, _set_k)

    def _get_model(self):
        return self._model
    model = property(_get_model)

    def get_guess(self):
        """Random guess to initialise optimisation"""
        params = {}
        m = self.data.min()
        M = self.data.max()
        range_ = M - m

        mus = [m + range_ / (self.k+1.) * i for i in range(1, self.k+1)]
        params['mus'] = mus

        sigma = range_ / float(self.k+1) / 2.
        params['sigmas'] = [sigma] * self.k

        params['pis'] = [1./self.k] * self.k

        params = [ [mu,sigma,pi]  for mu,sigma,pi in
                    zip(params['mus'], params['sigmas'], params['pis'])]
        params = list(pylab.flatten(params))
        return params

    def plot(self, normed=True, N=1000, Xmin=None, Xmax=None, bins=50, color='red', lw=2,
            hist_kw={'color':'#5F9EA0'}, ax=None):

        if ax:
            ax.hist(self.data, normed=normed, bins=bins, **hist_kw)
        else:
            pylab.hist(self.data, normed=normed, bins=bins, **hist_kw)
        if Xmin is None:
            Xmin = self.data.min()
        if Xmax is None:
            Xmax = self.data.max()
        X = pylab.linspace(Xmin, Xmax, N)

        if self.distribution == "poisson":
            X = pylab.linspace(Xmin-30, Xmax+30, Xmax-Xmin+1)
            X= [int(this) for this in X]

        if ax:
            ax.plot(X, [self.model.pdf(x, self.results.x) for x in X],
                    color=color, lw=lw)
        else:
            pylab.plot(X, [self.model.pdf(x, self.results.x) for x in X],
                    color=color, lw=lw)

        if self.distribution == "gaussian":
            K = len(self.results.x)
            # The PIs must be normalised
            for i in range(0, int(K/3)):
                mu, sigma, pi_ = self.results.mus[i], self.results.sigmas[i], self.results.pis[i]
                if ax:
                    ax.plot(X, [pi_ * pylab.normpdf(x, mu, sigma) for x in X],
                            'g--', alpha=0.5)
                else:
                    pylab.plot(X, [pi_ * pylab.normpdf(x, mu, sigma) for x in X],
                        'g--', alpha=0.5)


class PoissonMixtureFitting(Fitting):
    def __init__(self, data, k=2, method='Nelder-Mead'):
        super(PoissonMixtureFitting, self).__init__(data, k=k, method=method,
            distribution="poisson")

    def estimate(self, guess=None, k=None, maxfev=2e4, maxiter=1e3,
            bounds=None, constraints=(), display=False):
        if k is not None:
            self.k = k

        if guess is None:
            guess = self.get_guess()

        res = minimize(self.model.log_likelihood, x0=guess, args=(self.data,),
                    method=self.method,
                    options=dict(maxiter=maxiter, maxfev=maxfev, disp=display),
                    bounds=bounds, constraints=constraints)

        self.results = res
        pis = np.array(self.results.x[2::3])
        #pis /= pis.sum()
        self.results.pis_raw = pis.copy()
        unstable = False
        k = len(self.results.x)/3
        params = []
        for i in range(0, int(k)):
            # In poisson, k and loc must be integer hence the cast in the next 2
            # lines
            params.append(int(self.results.x[i*3]))
            params.append(int(self.results.x[(i*3+1)]))
            params.append(pis[i])
        self.results.x = params

        # FIXME shall we multiply by -1 ??
        self.results.log_likelihood = self.model.log_likelihood(params, self.data)
        if self.results.log_likelihood and unstable is False:
            self.results.AIC = criteria.AIC(self.results.log_likelihood, self.k, logL=True)
            self.results.AICc = criteria.AICc(self.results.log_likelihood, self.k,
                                        self.data.size, logL=True)
        else:
            self.results.AIC = 1000
            self.results.AICc = 1000
            self.results.BIC = 1000

        pis = np.array(self.results.x[2::3])

        self.results.pis = list(pis / pis.sum())
        self.results.sigmas = self.results.x[1::3]
        self.results.mus = self.results.x[0::3]

        return res


class GaussianMixtureFitting(Fitting):
    """GaussianMixtureFitting using scipy minization

    .. plot::
        :width: 80%
        :include-source:

        from biokit.stats.mixture import GaussianMixture, GaussianMixtureFitting
        m = GaussianMixture(mu=[-1,1], sigma=[0.5,0.5], mixture=[0.2,0.8])
        mf = GaussianMixtureFitting(m.data)
        mf.estimate(k=2)
        mf.plot()

    """
    def __init__(self, data, k=2, method='Nelder-Mead'):
        """

        Here we use the function minimize() from scipy.optimization.
        The list of (currently) available minimization methods is 'Nelder-Mead' (simplex),
        'Powell', 'CG', 'BFGS', 'Newton-CG',> 'Anneal', 'L-BFGS-B' (like BFGS but bounded),
        'TNC', 'COBYLA', 'SLSQPG'.

        """
        super(GaussianMixtureFitting, self).__init__(data, k=k, method=method)

    def estimate(self, guess=None, k=None, maxfev=2e4, maxiter=1e3,
            bounds=None):
        """guess is a list of parameters as expected by the model

        guess = {'mus':[1,2], 'sigmas': [0.5, 0.5], 'pis': [0.3, 0.7]  }

        """
        if k is not None:
            self.k = k

        if guess is None:
            # estimate the mu/sigma/pis from the data
            guess = self.get_guess()

        res = minimize(self.model.log_likelihood, x0=guess, args=(self.data,),
            method=self.method, options=dict(maxiter=maxiter, maxfev=maxfev),
            bounds=bounds)

        self.results = res
        pis = np.array(self.results.x[2::3])
        self.results.pis_raw = pis.copy()
        # The ratio may be negative, in which case we need to normalise.
        # An example would be to have -0.35, -0.15, which normalise would five 0.7, 0.3 as expected.
        """if sum(pis<0) > 0:
            unstable = True
            pis /= pis.sum()
            if self.verbose:
                print("Unstable... found negative pis (k=%s)" % self.k)
        else:
            unstable = False
            pis /= pis.sum()
        """
        unstable = False
        k = len(self.results.x)/3
        params = []
        for i in range(0, int(k)):
            params.append(self.results.x[i*3])
            params.append(self.results.x[(i*3+1)])
            params.append(pis[i])
        self.results.x = params

        # FIXME shall we multiply by -1 ??
        self.results.log_likelihood = self.model.log_likelihood(params, self.data)
        if self.results.log_likelihood and unstable is False:
            self.results.AIC = criteria.AIC(self.results.log_likelihood, self.k, logL=True)
            self.results.AICc = criteria.AICc(self.results.log_likelihood, self.k,
                                        self.data.size, logL=True)
            self.results.BIC = criteria.BIC(self.results.log_likelihood, self.k,
                                        self.data.size, logL=True)
        else:
            self.results.AIC = 1000
            self.results.AICc = 1000
            self.results.BIC = 1000

        pis = np.array(self.results.x[2::3])

        self.results.pis = list(pis / pis.sum())
        self.results.sigmas = self.results.x[1::3]
        self.results.mus = self.results.x[0::3]

        return res

class EM2(object):
    def __init__(self, data):
        self.data = data

    def estimate(self, models=None, pis=None, max_iter=100, 
        tol=1e-15, tol_iters=10):

        if models is None and pis is None:
            raise ValueError("must provide a list of models")
        elif models is not None and pis is None:
            self.k = len(models)
            pis = np.array([1./self.k] * self.k)
            m = min(self.data)
            M = max(self.data)
            mus = pylab.linspace(m, M, self.k)
            sigmas = (M-m)/self.k
            models = [GaussianModel() for this in range(self.k)]
        elif models is not None and pis is not None:
            self.k = len(models)
            assert len(models) == len(pis)

        N = len(self.data)
        resp = np.empty((N, self.k))
        log_density = np.empty((N, self.k))

        iteration = 0
        while True:

            # The E-Step computing the log likelihood with respect to the
            # conditional distributions
            for k in range(self.k):
                log_density[:,k] = models[k].log_density(self.data)

            # normalsie and compute overall log likelihood
            resp = pis[np.newaxis, :] * np.exp(log_density)
            resp /= np.sum(resp, axis=1)[:, np.newaxis]

            log_likelihood = np.sum(resp * log_density)
            iteration += 1

            # The M-step that requires the log distribution + estimation
            # parameters to be available in the distribution class

            for k in range(self.k):
                models[k].estimate(self.data, None) #resp[:,k])
            pis = np.mean(resp, axis=0)
            print("it=%s pis=%s L=%s" % (iteration, pis, log_likelihood))

            iteration += 1
            if iteration > max_iter:
                break


class EM(Fitting):
    """Expectation minimization class to estimate parameters of GMM

    .. plot::
        :width: 50%
        :include-source:

        from biokit.stats.mixture import Mixture, EM
        m = Mixture(mu=[-1,1], sigma=[0.5,0.5], mixture=[0.2,0.8])
        em = EM(m.data)
        em.estimate(k=2)
        em.plot()

    """
    def __init__(self, data, distribution="gaussian", max_iter=100):
        """.. rubric:: constructor

        :param data:
        :param model: not used. Model is the :class:`GaussianMixtureModel` but
            could be other model.
        :param int max_iter: max iteration for the minization

        """
        super(EM, self).__init__(data, k=2, distribution=distribution) # default is k=2
        self.max_iter = max_iter

    @do_profile()
    def estimate(self, guess=None, k=2):
        """

        :param list guess: a list to provide the initial guess. Order is mu1, sigma1,
            pi1, mu2, ...
        :param int k: number of models to be used.
        """
        #print("EM estimation")
        self.k = k
        # Initial guess of parameters and initializations
        if guess is None:
            # estimate the mu/sigma/pis from the data
            guess = self.get_guess()

        mu = np.array(guess[0::3])
        sig = np.array(guess[1::3])
        pi_ = np.array(guess[2::3])
        N_ = len(pi_)

        gamma = np.zeros((N_, self.size))
        N_ = np.zeros(N_)
        p_new = guess

        # EM loop
        counter = 0
        converged = False

        self.mus = []
        while not converged:
        # Compute the responsibility func. and new parameters
            for k in range(0, self.k):
                # unstable if eslf.model.pdf is made of zeros
                #if self.model.pdf(self.data, p_new,normalise=False).sum()!=0:
                #    gamma[k, :] = pi_[k]*pylab.normpdf(self.data, mu[k],
                #        sig[k])/(self.model.pdf(self.data, p_new, normalise=False))
                #else:
                gamma[k, :] = pi_[k]*pylab.normpdf(self.data, mu[k], sig[k])/  \
                        (self.model.pdf(self.data, p_new, normalise=False)+1e-10)
                N_[k] = 1.*gamma[k].sum()
                mu[k] = sum(gamma[k]*self.data)/N_[k]
                sig[k] = pylab.sqrt( sum(gamma[k]*(self.data - mu[k])**2)/N_[k] )
                #N_[k] += 1
                pi_[k] = N_[k] /  self.size

            self.results = {'x': p_new, 'nfev':counter, 'success': converged}

            p_new = [(mu[x], sig[x], pi_[x]) for x in range(0, self.k)]
            p_new = list(pylab.flatten(p_new))

            self.status = True
            try:
                assert abs(N_.sum() - self.size)/self.size < 1e-6
                assert abs(pi_.sum() - 1) < 1e-6
            except:
                print("issue arised at iteration %s" % counter)
                self.debug = {'N':N_, 'pis':pi_}
                self.status = False
                break

            self.mus.append(mu)

            # Convergence check
            counter += 1
            converged = counter >= self.max_iter

        self.gamma = gamma

        if self.status is True:
            self.results = {'x': p_new, 'nfev':counter, 'success': converged}


        self.results = AttrDict(**self.results)
        self.results.mus = self.results.x[0::3]
        self.results.sigmas = self.results.x[1::3]
        self.results.pis = self.results.x[2::3]

        log_likelihood = self.model.log_likelihood(self.results.x, self.data)
        self.results.AIC = criteria.AIC(log_likelihood, k, logL=True)

        self.results.log_likelihood = log_likelihood
        self.results.AIC = criteria.AIC(log_likelihood, self.k, logL=True)
        self.results.AICc = criteria.AICc(log_likelihood, self.k, self.data.size, logL=True)
        self.results.BIC = criteria.BIC(log_likelihood, self.k, self.data.size, logL=True)



class AdaptativeMixtureFitting(object):
    """Automatic Adaptative Mixture Fitting

    .. plot::
        :width: 80%
        :include-source:

        from biokit.stats.mixture import AdaptativeMixtureFitting, Mixture
        m = Mixture(mu=[-1,1], sigma=[0.5,0.5], mixture=[0.2,0.8])
        amf = AdaptativeMixtureFitting(m.data)
        amf.run(kmin=1, kmax=6)
        amf.diagnostic(k=amf.best_k)


    """
    # TODO: propose to use EM or Minimization.
    def __init__(self, data, method='Nelder-Mead'):
        self.fitting = GaussianMixtureFitting(data, method=method)
        self.verbose = True

    def run(self, kmin=1, kmax=6, criteria='AICc'):
        self.all_results = {}
        self.x = []

        for k in range(kmin, kmax+1):
            self.fitting.estimate(k=k)

            # here ritteria does not matter. if one fails, all fail
            if self.fitting.results['AIC'] != 1000:
                self.x.append(k)
                self.all_results[k] = self.fitting.results.copy()

        m = np.array([self.all_results[x][criteria] for x in self.x]).min()
        index = np.array([self.all_results[x][criteria] for x in self.x]).argmin()
        if self.verbose:
            print('Found min ', m, 'for k  ', self.x[index])
        self.best_k = self.x[index]
        self.min_value = m


    def plot(self, criteria='AICc'):

        pylab.plot(self.x, [self.all_results[x]['BIC'] for x in self.x], 'o-', label='BIC')
        pylab.plot(self.x, [self.all_results[x]['AIC'] for x in self.x], 'o-',  label='AIC')
        pylab.plot(self.x, [self.all_results[x]['AICc'] for x in self.x], 'o-', label='AICc')

        m = np.array([self.all_results[x][criteria] for x in self.x]).min()
        # [exp((m-this[criteria])/2) for this in amf.all_results]

        pylab.axhline(m - pylab.log(0.9)*2, color='k', label='90% equi-probability', alpha=0.9)
        pylab.axhline(m - pylab.log(0.5)*2, color='k', label='50% equi-probability', alpha=0.5)
        pylab.axhline(m - pylab.log(0.3)*2, color='k', label='30% equi-probability', alpha=0.3)

        pylab.legend()


    def diagnostic(self, kmin=1, kmax=8, k=None, ymax=None):
        self.run(kmin=kmin, kmax=kmax);
        pylab.clf()
        pylab.subplot(3,1,2);
        self.plot()
        mf = GaussianMixtureFitting(self.fitting.data)
        if k is None:
            mf.estimate(k=self.best_k)
        else:
            mf.estimate(k=k)
        pylab.subplot(3,1,1)
        mf.plot()
        if ymax is not None:
            pylab.ylim([0, ymax])

        pylab.subplot(3,1,3)
        min_value = np.array([self.all_results[x]['AICc'] for x in self.x]).min()
        pylab.plot(self.x, [pylab.exp((min_value-self.all_results[k]['AICc'])/2)
            for k in  self.x], 'o-', label='AICc')
        min_value = np.array([self.all_results[x]['AIC'] for x in self.x]).min()
        pylab.plot(self.x, [pylab.exp((min_value-self.all_results[k]['AIC'])/2)
            for k in  self.x], 'o-', label='AIC')

        pylab.xlabel('probability of information loss (based on AICc')
        pylab.legend()





