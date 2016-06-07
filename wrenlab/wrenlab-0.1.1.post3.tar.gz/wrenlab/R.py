"""
Python interface to R functions.
"""

import collections
from contextlib import redirect_stdout, redirect_stderr
import os
import warnings

import pandas as pd
import numpy as np
import scipy.stats

from rpy2.robjects import r, pandas2ri
from rpy2.robjects.packages import importr

from wrenlab.util import LOG

pandas2ri.activate()

r["Sys.setenv"](R_SHARE_DIR="/usr/share/R")

def dict_to_list(d):
    ks, vs = map(list, zip(*d.items()))
    o = r["as.list"](vs)
    o.names = ks
    return o

def vsn(X):
    """
    Variance-stabilizing normalization.

    Arguments
    ---------
    X : :class:`pandas.DataFrame`
        An expression matrix, with probes as rows and samples as columns.
    """
    LOG.info("Calling R VSN function on matrix of shape: {}".format(X.shape))
    pkg = importr("vsn")
    Xm = np.array(X)
    with open(os.devnull, "w") as h:
        with redirect_stdout(h):
            o = np.array(r["as.matrix"](pkg.vsn2(Xm)))
    o = pd.DataFrame(o, index=X.index, columns=X.columns)
    o.index.name = X.index.name
    o.columns.name = X.columns.name
    return o

def impute_qPCR(X, design, controls=None, max_iterations=100):
    if controls is None:
        controls = list(X.index[~X.isnull().any(axis=1)])

    pkg = importr("wrenlab")
    c = r["unlist"](controls)
    with open(os.devnull, "w") as h:
        with redirect_stdout(h):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                o = pkg.impute_qPCR(X, design, c, max_iterations=max_iterations)
    o = pandas2ri.ri2py(o)
    return pd.DataFrame(o, index=X.index, columns=X.columns)

def wilcoxGST(index, statistics, alternative="mixed", type="auto"):
    assert alternative in ("mixed", "either", "up", "down")
    assert type in ("t", "f", "auto")
    # unused: ranks_only (default T), nsim
    pkg = importr("limma")
    return float(pkg.geneSetTest(index, statistics, alternative=alternative, type=type, ranks_only=True)[0])

def fit_rocke_durbin(X, theta=0.05):
    pkg = importr("GESTr")
    Xm = np.array(X)
    with open(os.devnull, "w") as h:
        with redirect_stdout(h):
            o = pkg.fitRockeDurbin(Xm, theta=theta)
    return dict(zip(o.names, [x[0] for x in o]))

def mi(X):
    """
    Multiple imputation using the "mi" package.

    Arguments
    ---------
    X : :class:`pandas.DataFrame`
        A matrix with variables as rows and samples as columns.
    """
    X = X.dropna(thresh=10)
    pkg = importr("mi")
    X_r = pkg.missing_data_frame(X.T)
    X_r = pkg.change(X_r, y=r["as.character"](["X{}".format(i) for i in X.index]), 
            what="family", to="gaussian")
    imputations = pkg.mi(X_r, **{"n.iter":30, "n.chains":4, "max.minutes": 20})
    r.show(imputations)

def compose(*fns):
    def fn(x):
        for fn in reversed(fns):
            x = r[fn](x)
        return x
    return fn

def rstrip_digit(x):
    for i in reversed(range(len(x))):
        if not x[i].isdigit():
            return x[:(i+1)]
    return ""

def fix_index(index):
    o = []
    for ix in index:
        if ix == "(Intercept)":
            o.append("Intercept")
            continue
        else:
            ixs = []
            for six in ix.split(":"):
                base = rstrip_digit(six)
                if len(base) < len(six):
                    digit = six[len(base):]
                    six = "{}[{}]".format(base, digit)
                ixs.append(six)
            o.append(":".join(ixs))
    return o

class LMERModel(object):
    def __init__(self, fit):
        self._fit = fit

    @property
    def fixed_effects(self):
        o = pandas2ri.ri2py(compose("as.data.frame", "coef", "summary")(self._fit))
        o.index = fix_index(o.index)
        o.columns = ["coef", "SE", "t"]
        o["p"] = 2 * (1 - scipy.stats.norm.cdf(o["t"].abs()))
        return o

    @property
    def random_effects(self):
        print(r["summary"](self._fit))
        re = r["ranef"](self._fit)
        o = collections.OrderedDict()
        for key, df in zip(re.names, re):
            o[key] = pandas2ri.ri2py(df)
            o[key].columns = fix_index(o[key].columns)
        return o

def lmer(formula, y, design):
    assert y.shape[0] == design.shape[0]
    assert "y" not in design.columns

    formula_r = r["as.formula"]("y ~ {}".format(formula))
    D = design.copy()
    D["y"] = y

    pkg = importr("lme4")
    fit = pkg.lmer(formula_r, D)
    return LMERModel(fit)

class StanModel(object):
    def __init__(self, path):
        pkg = importr("rstan")
        self._model = pkg.stan_model(path)

    def fit(self, data, iter=1000, chains=4):
        pkg = importr("rstan")
        data = dict_to_list(data)
        fit = self._model
        fit = pkg.sampling(self._model, data=data, iter=iter, chains=chains)
        return StanFit(fit)

    def save(self, path):
        pass

    @staticmethod
    def load(path):
        pass

class StanFit(object):
    def __init__(self, fit):
        self._fit = fit

    def serve(self, host="127.0.0.1", port=8080, launch_browser=False):
        pkg = importr("shinystan")
        pkg.launch_shinystan(object=self._fit, 
                port=port, 
                **{"launch.browser": launch_browser})

def stan(model_path, data, iter=1000, chains=4):
    pkg = importr("rstan")
    data = dict_to_list(data)
    #handle = r["file"](model_path)
    fit = pkg.stan(file=model_path, data=data, iter=iter, chains=chains)
    return StanFit(fit)
