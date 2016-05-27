import numpy as np
import scipy.stats as st
import warnings
#idea taken from http://stackoverflow.com/questions/21623717/fit-data-to-all-possible-distributions-and-return-the-best-fit


def findBestDistribution(data, disttype='continuous'):
    '''
    find best statistical distribution,see:
    http://docs.scipy.org/doc/scipy-0.14.0/reference/stats.html

    currently only continuous distributions embedded

    returns scipy.stats[DIST], fitparams
    '''

    if disttype != 'continuous':
        raise NotImplemented()

    distributions = [st.alpha, st.anglit, st.arcsine,
                     st.beta, st.betaprime, st.bradford,
                     st.burr, st.cauchy,st.chi,
                     st.chi2, st.cosine, st.dgamma,
                     st.dweibull, st.erlang, st.expon,
                     st.exponweib,st.exponpow, st.f,
                     st.fatiguelife, 
                    st.fisk, st.foldcauchy , st.foldnorm ,
                    st.frechet_r  ,st.frechet_l, st.genlogistic, st.genpareto,
                    st.genexpon, st.genextreme, st.gausshyper,
                    st.gamma,st.gengamma, st.genhalflogistic,
                    st.gilbrat,st.gompertz, st.gumbel_r,
                    st.gumbel_l ,st.halfcauchy ,st.halflogistic,
                    st.halfnorm , st.hypsecant, st.invgamma,
                    st.invgauss,   st.invweibull,  st.johnsonsb,
                    st.johnsonsu  ,  st.ksone,   st.kstwobign,
                    st.laplace,   st.logistic,    st.loggamma,
                    st.loglaplace  , st.lognorm , st.lomax,
                    st.maxwell, st.mielke, st.nakagami,
                    st.ncx2, st.ncf, st.nct,
                    st.norm, st.pareto, st.pearson3,
                    st.powerlaw , st.powerlognorm, 
                    st.powernorm, st.rdist, st.reciprocal, 
                    st.rayleigh,st.rice , st.recipinvgauss, 
                    st.semicircular, st.t, st.triang,
                    st.truncexpon, st.truncnorm, st.tukeylambda,
                    st.uniform, st.vonmises,  st.wald,
                    st.weibull_min, st.weibull_max, st.wrapcauchy]

    mles = []
    pars_l = []
    valid_dist = []

    with warnings.catch_warnings():
        warnings.filterwarnings('ignore')

        for distribution in distributions:
            pars = distribution.fit(data)
            #maximum-likelihood estimation:
            mle = distribution.nnlf(pars, data)
            if np.isfinite(mle):
                valid_dist.append(distribution)
                mles.append(abs(mle))
                pars_l.append(pars)

    best_fit = sorted(zip(valid_dist, mles, pars_l), key=lambda d: d[1])[0]
    print 'Best fit reached using {}, MLE value: {}'.format(best_fit[0].name, best_fit[1])
    print pars_l
    return best_fit[0], best_fit[2]



if __name__ == '__main__':
    import sys
    import pylab as plt
    # generate a random sample using a given distribution:
    n = 1000
    nn = 100
    # choose a distribution:
    data = st.norm.rvs(size=n)
    # find best dist:
    dist, param = findBestDistribution(data)

    if 'no_window' not in sys.argv:
        plt.hist(data, normed=True, histtype='stepfilled', alpha=0.2)
        x = np.linspace(data.min(), data.max(), nn)
        plt.plot(x, dist.pdf(x, *param))
        plt.show()
