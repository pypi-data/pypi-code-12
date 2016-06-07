__all__ = ["Experiment"]

import os
import os.path
import collections
import multiprocessing as mp

import sklearn.decomposition
import numpy as np
import scipy.stats
import patsy
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
from joblib import Parallel, delayed

import wrenlab.impute
import wrenlab.correlation
import wrenlab.normalize
from wrenlab.util import LOG

Model = collections.namedtuple("Model", "params,metadata")

"""
class Model(collections.OrderedDict):
    ""
    Represents a (per-gene) collection of OLS models performed 
    on the same dataset and formula.
    ""
    def __init__(self, formula=None):
        self.formula = formula
        super(Model, self).__init__()

    def __repr__(self):
        return "<Model with {} elements>".format(len(self))

    @property
    def params(self):
        return pd.DataFrame([v.params for v in self.values()], index=self.keys())

    @property
    def p(self):
        return pd.DataFrame([v.pvalues for v in self.values()], index=self.keys())

    @property
    def t(self):
        return pd.DataFrame([v.tvalues for v in self.values()], index=self.keys())
"""

OLS = collections.namedtuple("OLS", "params,tvalues,pvalues")

def _fit(y, design, groups=None, regularize=False, method="statsmodels", formula=None):
    design, y = design.dropna().align(y.dropna(), axis=0, join="inner")

    if method == "statsmodels":
        if groups is not None:
            m = sm.MixedLM(y, design, groups=groups)
            if regularize:
                return m.fit_regularized()
            else:
                return m.fit()
        else:
            X = np.array(design)
            parameters = design.columns
            beta, _, rank, sv = np.linalg.lstsq(X, y)
            residual = y  - np.dot(X, beta)
            #r2 = (1 - residual) / ((y - y.var())
            t = pd.Series(beta / X.std(axis=0), index=parameters)
            p = scipy.stats.t.cdf(t, df=t.shape[0] - 1)
            p = pd.Series(np.minimum(p, 1-p) * 2, index=parameters)
            coef = pd.Series(beta, index=parameters)
            return OLS(coef, t, p)
    elif method == "lmer":
        import wrenlab.R
        assert formula is not None
        fit = wrenlab.R.lmer(formula, y, design)
        df = fit.fixed_effects
        return OLS(df["coef"], df["t"], df["p"])
    else:
        raise ValueError

def _fit_multiple(Y, design):
    LOG.info("Fitting linear models: {} samples x {} transcripts".format(*Y.T.shape))
    X = np.array(design)
    parameters = design.columns
    beta, _, rank, sv = np.linalg.lstsq(X, Y.T)
    for j in range(beta.shape[1]):
        beta_j = beta[:,j]
        t = pd.Series(beta_j / X.std(axis=0), index=parameters)
        p = scipy.stats.t.cdf(t, df=t.shape[0] - 1)
        p = pd.Series(np.minimum(p, 1-p) * 2, index=parameters)
        coef = pd.Series(beta_j, index=parameters)
        yield OLS(coef, t, p)


class Experiment(object):
    def __init__(self, design, data, metadata=None):
        assert isinstance(data, pd.DataFrame)
        assert isinstance(design, pd.DataFrame)
        assert design.shape[0] == data.shape[1]
        assert (design.index == data.columns).all()
        self._design = design
        self._data = data
        self.metadata = metadata or {}

    @property
    def design(self):
        return self._design.copy()

    @property
    def data(self):
        return self._data.copy()

    @property
    def shape(self):
        return self._data.shape

    def complete(self):
        return not self._data.isnull().any().any()

    def impute(self, method="linear_model"):
        fn = getattr(wrenlab.impute, method)
        data = fn(self.data).dropna()
        return Experiment(self.design, data, 
                metadata={k:v for k,v in self.metadata.items()})

    def normalize(self, method="quantile"):
        """
        Normalize the data in this Experiment with the given method, 
        returning a new Experiment object.
        """
        assert method in ("vsn", "quantile")
        data = self._data.dropna(thresh=int(0.2 * self._data.shape[0]), axis=1)
        if data.shape[1] == 0:
            raise Exception("No samples remaining after dropping those with >80% missing values.")
        design = self.design.loc[data.columns,:]
        if method == "quantile":
            data = data.dropna(thresh=int(0.5 * self._data.shape[1]))
            if data.shape[0] == 0:
                raise Exception("No probes remaining after dropping those with >50% missing values.")
            data = wrenlab.normalize.quantile(data)
        elif method == "vsn":
            data = wrenlab.normalize.vsn(data.dropna(how="any"))
        else:
            raise ValueError("Invalid normalization method: '{}'".format(method))
        return Experiment(design, data, metadata={k:v for k,v in self.metadata.items()})

    def pca(self, n_components=10, subset=None):
        data = self.data.dropna()
        if subset is not None:
            ix = list(set(subset) & set(data.index))
            data = data.loc[ix,:]
        model = sklearn.decomposition.PCA(n_components=n_components)
        components = pd.DataFrame(model.fit_transform(data.T).T,
                columns=data.columns,
                index=["C{}".format(i) for i in range(1, n_components+1)])

        metadata = {k:v for k,v in self.metadata.items()}
        metadata["Original Dimensions"] = data.shape[1]
        return Experiment(self.design, components, metadata=metadata)

    def fit(self, formula, groups=None, regularize=False, method="statsmodels"):
        """
        Fit OLS models for each gene/probe to the given formula.

        Arguments
        ---------
        formula : str
            The statistical formula to fit.
        groups : str
            If this is supplied, fit a mixed-effects model using
            the provided categorical variable as the groups.
        regularize : bool
            Whether to regularize, which penalizes fixed-effects terms. 
            Applies only to mixed-effects models.
        method : ("statsmodels", "lmer")
            The fitting software to use.
        """
        assert method in ("statsmodels", "lmer")

        design = self.design.dropna()
        design, data = design.T.align(self._data, join="inner", axis=1)
        design = design.T
        data = data.dropna(thresh=max(3, int(0.1 * data.shape[1])))

        design["Age"] = design["Age"].astype(float)
        for c in ["TissueID", "PlatformID", "ExperimentID"]:
            if c in design.columns:
                design[c] = design[c].astype("category")

        if method == "statsmodels":
            design = patsy.dmatrix(formula, design, return_type="dataframe")
            if groups is not None:
                groups = design[groups]

        """
        print(design["Age"].min(), design["Age"].max())
        print(data.min().min(), data.max().max())
        print(data.isnull().sum().sum())
        print(data.head().T.head().T)
        print(design.head())
        """

        index = data.index
        LOG.info("Fitting linear model ...")
        LOG.info("Design shape: {}".format(design.shape))
        LOG.info("Data shape: {}".format(data.shape))

        #NJOBS = 1
        NJOBS = mp.cpu_count() - 8

        if (groups is None) and (data.isnull().sum().sum() == 0):
            rs = _fit_multiple(data, design)
        else:
            rs = Parallel(n_jobs=NJOBS)(delayed(_fit)
                    (data.loc[probe_id,:], design, groups, regularize, method, formula)
                        for probe_id in index)
        o = []
        for model in rs:
            df = pd.concat([model.params, model.tvalues, model.pvalues], 
                    keys=["coef", "t", "p"],
                    axis=1)
            v = pd.Series(df.values.ravel("C"),
                    index=pd.MultiIndex.from_product([df.index, df.columns],
                        names=["Variable", "Statistic"]))
            o.append(v)
        params = pd.concat(o, keys=self._data.index, axis=1).T
        params.index.name = self._data.index.name
        for axis in (0,1):
            params.sort_index(axis=axis, inplace=True)
        metadata = {k:v for k,v in self.metadata.items()}
        return Model(params=params, metadata=metadata)
 
        """
        print("job's done")
        for probe_id, fit in zip(index, rs):
            model[probe_id] = fit
        #for probe_id in self._data.index:
        #    y = self._data.loc[probe_id,:]

        return model
        """

    @property
    def report(self):
        mu = self._data.mean(axis=1).dropna()
        std = self._data.std(axis=1).dropna()
        ix = list(set(mu.index) & set(std.index))
        r = scipy.stats.pearsonr(mu.loc[ix], std.loc[ix])[0]

        data = np.array(self._data).flat
        data = data[~np.isnan(data)]
        return pd.Series((r, data.min(), data.max(), scipy.stats.skew(data)),
                index=[
                    "Mean-SD correlation",
                    "min",
                    "max",
                    "skewness",
        ])

        """
        os.makedirs(outdir, exist_ok=True)

        # Mean-SD plot
        mu = self._data.mean(axis=1)
        std = self._data.std(axis=1)
        sns.regplot(mu, std)
        plt.xlabel("Mean")
        plt.ylabel("Standard Deviation")
        plt.savefig(os.path.join(outdir, "mean_stdev.png"))

        # Distribution
        plt.clf()
        xs = np.array(self._data).flat
        sns.distplot(xs[~np.isnan(xs)])
        plt.xlabel("Intensity")
        plt.ylabel("Frequency")
        plt.savefig(os.path.join(outdir, "intensity_histogram.png"))
        """

    def correlate(self, covariate, method="pearson"):
        if method == "pearson":
            return wrenlab.correlation.pearson(self.data, self.design[covariate]).dropna()
        elif method == "spearman":
            return wrenlab.correlation.spearman(self.data, self.design[covariate]).dropna()
        else:
            raise ValueError("Method must be one of: {}".format(("pearson", "spearman")))

class ExperimentSet(list):
    def __init__(self, items, metadata=None):
        super(ExperimentSet, self).__init__(items)
        self.metadata = metadata or {}

    def plot_covariate_distribution(self, covariate):
        """
        Make a multi-boxplot of the distribution of values for a
        given covariate.
        """
        data = pd.DataFrame.from_records([(E.metadata["ExperimentID"], y) 
            for E in self for y in E.design[covariate].dropna()],
            columns=["ExperimentID", covariate])
        return sns.boxplot(y="ExperimentID", x=covariate, data=data, orient="h")

    def combine(self):
        """
        Combine the experiments within this ExperimentSet into a single Experiment
        with an additional ExperimentID categorical variable added to the design 
        matrix.
        """
        data = pd.concat([E.data for E in self], axis=1)
        design = pd.concat([E.design for E in self])
        parameters = set([k for E in self for k in E.metadata.keys()])
        for p in parameters:
            design[p] = 0
            for E in self:
                design.loc[E.design.index, p] = int(E.metadata[p])
            design[p] = design[p].astype("category")
            if len(set(design[p])) == 1:
                del design[p]
        return Experiment(design, data, metadata={k:v for k,v in self.metadata.items()})

    def filter(self, fn):
        """
        Filter experiments using a function.

        Arguments
        ---------
        fn : A function of signature f(Experiment) -> bool, where the result
            specifies whether to keep a given experiment.

        Returns
        -------
        A new :class:`ExperimentSet` with the selected experiments retained.
        """
        return ExperimentSet(list(filter(fn, self)),
                metadata={k:v for k,v in self.metadata.items()})
