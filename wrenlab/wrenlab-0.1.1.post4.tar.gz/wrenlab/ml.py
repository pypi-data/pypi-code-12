"""
Machine learning utilities.
"""

import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats
import sklearn.cross_validation
import sklearn.metrics
import pandas as pd

from wrenlab.util import align_series

class Problem(object):
    def __init__(self, y, X, type=None):
        assert isinstance(self.y, pd.Series)

        self.y = y
        self.X = X
        assert y.shape[0] == X.shape[0]
        if len(set(y)) == 2:
            self.type = "binary"
            self.predict_fn = lambda model, X: model.predict_log_proba(X)
        else:
            self.type = "continuous"
            self.predict_fn = lambda model, X: model.predict(X)

    def cross_validate(self, model, k=10):
        X = np.array(self.X)
        y = np.array(self.y)
        kf = sklearn.cross_validation.KFold(y.shape[0], k)
        y_hat = np.empty(y.shape)
        for tr_ix, te_ix in kf:
            X_tr, y_tr = X[tr_ix,:], y[tr_ix]
            model.fit(X_tr, y_tr)
            y_hat[te_ix] = self.predict_fn(model, X[te_ix,:])
        y_hat = pd.Series(y_hat, index=self.y.index)
        return Result(self.y, y_hat)

class Result(object):
    def __init__(self, y, y_hat):
        assert isinstance(y, pd.Series)
        assert isinstance(y_hat, pd.Series)
        # NOTE: y and y_hat are not assumed to be aligned, because
        #   a missing/NA value in y_hat means "no prediction"
        self.y = y.dropna()
        self.y_hat = y_hat.loc[self.y.index]

    @property
    def accuracy(self):
        return (self.y == self.y_hat).mean()

    @property
    def summary(self):
        return pd.Series([getattr(self, p) for p in self.PROPERTIES], 
                index=self.PROPERTIES)

class BinaryResult(Result):
    PROPERTIES = ["TP", "FP", "FN", "precision", "recall"]

    def __init__(self, y, y_hat):
        assert y.dtype.name == "bool"
        if y_hat.dtype.name == "float":
            raise NotImplementedError("Scores/probabilities not supported yet")
        assert y_hat.dtype.name == "bool"
        super(BinaryResult, self).__init__(y, y_hat)

    @property
    def TP(self):
        return (self.y & self.y_hat).sum()

    @property
    def FP(self):
        return ((~self.y) & self.y_hat).sum()

    @property
    def FN(self):
        return ((self.y) & (~self.y_hat)).sum()

    @property
    def precision(self):
        return self.TP / (self.TP + self.FP)

    @property
    def recall(self):
        return self.TP / (self.TP + self.FN)

    """
    @property
    def AUC(self):
        try:
            return sklearn.metrics.roc_auc_score(self.y, self.y_hat)
        except:
            return np.nan
    """

class CategoricalResult(Result):
    def __init__(self, y, y_hat):
        assert y.dtype.name == "category"
        assert y_hat.dtype.name == "category"

        y = y.cat.remove_unused_categories()
        super(CategoricalResult, self).__init__(y, y_hat)

        categories = self.y.cat.categories
        self.y = self.y.cat.set_categories(categories, ordered=True)

        disjoint = len(set(self.y_hat.cat.categories) - set(categories)) > 0
        if disjoint:
            categories = ["OTHER"] + list(sorted(categories))
            self.y = self.y.cat.set_categories(categories)

            self.y_hat = pd.Series(list(self.y_hat), index=self.y_hat.index)
            self.y_hat.ix[~self.y_hat.isin(self.y.cat.categories)] = "OTHER"
            self.y_hat = self.y_hat.astype("category")
        self.y_hat = self.y_hat.cat.set_categories(categories)

        self._results = {}
        for c in categories:
            self._results[c] = BinaryResult(self.y == c, self.y_hat == c)

    @property
    def categories(self):
        return list(self.y.cat.categories)

    def confusion_matrix(self, normalize=False):
        o = pd.DataFrame(index=self.categories, columns=self.categories).fillna(0)
        o.index.name = "y"
        o.columns.name = "y_hat"
        for c_y in self.categories:
            for c_y_hat in self.categories:
                o.loc[c_y,c_y_hat] = ((self.y == c_y) & (self.y_hat == c_y_hat)).sum()
        if "OTHER" in self.categories:
            o = o.drop("OTHER")
        if normalize:
            o = o.divide(1 + o.sum(axis=0), axis=1)
        return o

    @property
    def summary(self):
        ix = list(self._results.keys())
        o = pd.concat([self._results[c].summary for c in ix], axis=1).T
        o.index = ix
        return o.rename_axis("Category")

class ContinuousResult(Result):
    PROPERTIES = ["accuracy", "r2", "MAD", "MSE"]

    def __init__(self, y, y_hat, tolerance=0.1):
        """
        Arguments
        ---------

        tolerance : float
            y and y_hat values less than this distance away are considered to be
            the same for classification-based metrics.
        """
        super(ContinuousResult, self).__init__(y, y_hat)
        self.tolerance = tolerance

    @property
    def micro_precision(self):
        raise NotImplementedError

    @property
    def micro_recall(self):
        raise NotImplementedError

    @property
    def macro_precision(self):
        y, y_hat = align_series(self.y, self.y_hat, dropna=True)
        return np.isclose(y, y_hat, atol=self.tolerance).mean()

    @property
    def macro_recall(self):
        y_hat = self.y_hat.loc[self.y.index]
        return np.isclose(self.y, y_hat, atol=self.tolerance).mean()

    @property
    def r2(self):
        y, y_hat = align_series(self.y, self.y_hat, dropna=True)
        return scipy.stats.pearsonr(y, y_hat)[0] ** 2

    @property
    def MAD(self):
        return np.abs(self.y - self.y_hat).mean()

    @property
    def MSE(self):
        return ((self.y - self.y_hat) ** 2).mean()

    def plot(self, path=None):
        plt.clf()
        y, y_hat = align_series(self.y, self.y_hat, dropna=True)
        data = pd.DataFrame.from_dict({"y":y, "y_hat":y_hat})
        sns.regplot(x="y", y="y_hat", data=data, fit_reg=False)
        plt.xlim([0, y.max() * 1.1])
        plt.ylim([0, y_hat.max() * 1.1])
        plt.ylabel("$\hat{y}$")
        plt.xlabel("y")
        if path is not None:
            plt.savefig(path)
