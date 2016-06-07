import functools
import os.path

import numpy as np
import pandas as pd

import mmat

from wrenlab.util import memoize
from wrenlab.experiment import Experiment, ExperimentSet

@functools.lru_cache()
@memoize
def array_describe(path):
    # FIXME: Find a way to regenerate if mtime changes
    X = mmat.MMAT(path)
    return X.describe()

class GEO(object):
    def __init__(self, matrix_dir, labels):
        self._matrix_dir = matrix_dir
        self._labels = labels

    def __getitem__(self, taxon_id):
        return GEOTaxon(taxon_id, self._matrix_dir, self._labels)

class GEOTaxon(object):
    def __init__(self, taxon_id, matrix_dir, labels):
        self.taxon_id = int(taxon_id)
        self._path = os.path.join(matrix_dir, "{}.mmat".format(taxon_id))
        self._X = mmat.MMAT(self._path)
        self._path_t = os.path.join(matrix_dir, "{}.t.mmat".format(taxon_id))
        self._XT = mmat.MMAT(self._path_t)

        self._A = labels.copy()
        # FIXME: Drop Channel index, if it exists - assumes Channel is always 1 for now
        if isinstance(self._A.index, pd.MultiIndex):
            assert (self._A.index.names == ["SampleID", "Channel"]).all()
            self._A.index = self._A.index.droplevel(1)
        if self._A.index.dtype == object:
            assert self._A.index[0].startswith("GSM")
            self._A.index = [int(x[3:]) for x in self._A.index]
        assert self._A.index.dtype == np.int64

        self._A = self._A.ix[self._A["TaxonID"] == taxon_id,:] # necessary?
        X_ix = [int(x[3:]) for x in self._X.index]
        self._A = self._A.loc[list(set(self._A.index) & set(X_ix)),:]

    def describe(self, axis=1):
        if axis == 1:
            return array_describe(self._path)
        elif axis == 0:
            return array_describe(self._path_t)
        else:
            raise ValueError

    def gene(self, gene_id, standardize=False):
        if standardize is True:
            design = self.gene(gene_id, standardize=False)
            y = design["Expression"]
            summary = self.describe().dropna()
            summary.index = [int(x[3:]) for x in summary.index]
            ix = list(set(y.index) & set(summary.index))
            y,summary = y.loc[ix],summary.loc[ix,:]
            design = design.loc[ix,:]
            y = pd.Series([(yy - mu) / sd for yy,mu,sd in 
                zip(y,summary["mean"].astype(float),summary["std"].astype(float))],
                index=ix)
            design["Expression"] = y
            return design
        else:
            ix = ["GSM{}".format(ix) for ix in self._A.index]
            x = self._XT.loc[gene_id, ix].dropna()
            x.index = [int(x[3:]) for x in x.index]
            o, x = self._A.copy().align(x, join="inner", axis=0)
            o["Expression"] = x
            return o

    def experiment(self, experiment_id):
        # FIXME: assumes A index is str
        raise NotImplementedError

        A = self._A.ix[self._A["ExperimentID"] == experiment_id,:]
        X = self._X.loc[list(set(A.index)),:].to_frame().T
        design = A.loc[X.columns,["TissueID", "Age", "Gender"]]
        metadata = {
            "ExperimentID": int(experiment_id),
            "TaxonID": self.taxon_id
        }
        return Experiment(design, X, metadata=metadata)

    def experiments(self, tissue_id, min_samples=10, min_transcripts=500):
        # FIXME: assumes A index is str
        raise NotImplementedError

        A = self._A.ix[self._A["TissueID"] == tissue_id,:]
        for (experiment_id, platform_id), df in A.groupby(["ExperimentID", "PlatformID"]):
            N = df.shape[0]
            if N < min_samples:
                continue
            X = self._X.loc[df.index,:].to_frame().T
            X.index.name = "Entrez Gene ID"
            if X.dropna(how="any").shape[0] < min_transcripts:
                continue
            design = df.loc[:,["Age", "Gender"]]
            E = Experiment(design, X, metadata={
                "ExperimentID": int(experiment_id),
                "TaxonID": self.taxon_id,
                "PlatformID": int(platform_id),
                "TissueID": tissue_id})
            yield E
