import collections
import os.path

import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.api as sm
import patsy
import pandas as pd
import numpy as np
from scipy import stats

import wrenlab.data.signature
import wrenlab.plot
import wrenlab.normalize
import wrenlab.ontology
import wrenlab.GO
from wrenlab.util import memoize, download, remote_table

@memoize
def _gene_ontology(taxon_id):
    o = wrenlab.ontology.fetch("GO")
    X = remote_table("NCBI.gene.gene_go")
    ix = (X["Taxon ID"] == taxon_id) & (X["Evidence"] != "IEA")
    mapping = X.ix[ix,["Gene ID", "Term ID"]]
    return AnnotationSet(mapping, metadata=o.terms.drop("Namespace", axis=1))

def _gene_ontology_concepts(taxon_id):
    A = _gene_ontology(taxon_id)
    J = A.mapping.drop(["Score"], axis=1)\
            .merge(wrenlab.GO.concepts())\
            .drop(["Term ID"], axis=1)\
            .loc[:,["Element ID", "Concept", "Direction"]]
    return AnnotationSet(J)

def _NoaLTP(taxon_id):
    assert taxon_id == 10090
    return wrenlab.data.signature.NoaLTP()

_AVAILABLE = {
    "GO": _gene_ontology,
    "gene_ontology": _gene_ontology,
    "gene_ontology_concepts": _gene_ontology_concepts,
    "NoaLTP": _NoaLTP
}

class SignatureAnalysis(object):
    def __init__(self, data):
        self._data = data

    @property
    def data(self):
        return self._data.copy()

    def plot(self, term, path, center=False):
        data = self._data.loc[term,:]
        xs = data["coef"]
        error = next(iter(data["stderr"]))
        if center:
            xs -= xs.iloc[0]
        wrenlab.plot.bar(xs, 
                error=error, 
                y_label="\n".join([term, r"(log$_2$ expression, relative LM coefficient)"]))
        plt.savefig(path)

    def plot_all(self, dir, center=False):
        assert os.path.isdir(dir)
        for term in self._data.index.levels[0]:
            path = os.path.join(dir, "{}.png".format(term.replace(" ", "_")))
            self.plot(term, path, center=center)

class AnnotationSet(object):
    """
    A bidirectional map of Entrez Gene IDs to Term IDs, with an additional
    "background" attribute listing all "elements" (usually genes)
    annotated by any term in the set.
    """

    def __init__(self, mapping, metadata=None):
        """
        Arguments
        ---------
        mapping: a :class:`pandas.DataFrame` with 2 or 3 columns: 
            Element IDs, Term IDs, and (optional) a score associated with the relationship
        metadata: :class:`pandas.DataFrame`, optional
            Term IDs are row indices, columns contain metadata about each term (e.g., names)
        """

        assert isinstance(mapping, pd.DataFrame)
        assert(mapping.shape[1] in (2,3))
        if mapping.shape[1] == 2:
            mapping["Score"] = 1
        mapping.columns = ["Element ID", "Term ID", "Score"]
        self.mapping = mapping.drop_duplicates(subset=["Element ID", "Term ID"]) 
        self.metadata = metadata

    def __repr__(self):
        return "<AnnotationSet with {} terms and {} elements>".format(len(self.terms),
                len(self.elements))

    @property
    def elements(self):
        return list(sorted(set(self.mapping["Element ID"])))

    @property
    def terms(self):
        return list(sorted(set(self.mapping["Term ID"])))

    def enrichment(self, scores, min_count=3):
        """
        Perform enrichment analysis for the association of a scored set of genes 
        with terms using Fisher's Exact test.

        Arguments
        ---------
        scores: a :class:`pandas.Series` with Entrez Gene IDs as indices and
            numeric or boolean values  
        min_count: int
            The minimum number of selected genes which must be annotated with the 
            term in order to consider the term for enrichment.

        Returns
        -------
        A :class:`pandas.DataFrame` with statistics showing enrichment values 
        for each term.
        """
        return self._enrichment_binary(scores, min_count)

    def _enrichment_permutation(self, scores):
        raise NotImplementedError

    def _enrichment_binary(self, scores, min_count):
        background = list(set(self.elements) & set(scores.index))
        scores = scores.loc[background]

        if (scores.dtype == np.bool):
            s = scores
        else:
            s = scores > scores.quantile(0.95)
        s = s.astype(int)
        s.name = "Score2"
        m = self.mapping.ix[self.mapping["Element ID"].isin(background),:].copy()
        m["Score"] = 1
        j = m.merge(s.to_frame(), how="inner", left_on="Element ID", right_index=True)\
                .dropna(subset=["Term ID"])
        counts = j.groupby(["Score2", "Term ID"])["Score"].count()

        # as a s
        ct = pd.concat([
                counts.loc[1],
                s.sum() - counts.loc[1],
                counts.loc[0]], axis=1)
        ct.columns = ["AS", "S", "A"]
        ct = ct.fillna(0)
        ct["O"] = len(s) - ct.sum(axis=1)
        ct = ct.ix[ct["AS"] >= min_count,:]
        assert ((ct["AS"] + ct["S"]) == s.sum()).all()
        assert ((ct["A"] + ct["O"]) == (len(s) - s.sum())).all()

        o = []
        for term_id in ct.index:
            cts = ct.loc[term_id,:]
            cts = np.array(cts).reshape((2,2))
            OR, p = stats.fisher_exact(cts)
            slpv = -1 * np.sign(np.log(OR)) * np.log10(p)
            o.append((term_id, OR, slpv))
        o = pd.DataFrame(o, columns=["Term ID", "Odds Ratio", "SLPV"])\
                .set_index(["Term ID"])
        o = ct.join(o, how="inner")
        if self.metadata is not None:
            o = self.metadata.join(o, how="right")
        return o.sort_values("SLPV", ascending=False)

    def signature(self, X, D, groups, subset=None):
        assert groups.shape[0] == 2 ** groups.shape[1]
        groups = groups.sort_values(by=list(groups.columns))
        n_coef = groups.shape[0]

        X = X.loc[list(set(X.index) & set(self.mapping["Element ID"])),:]
        Am = self.mapping.ix[self.mapping["Element ID"].isin(X.index),:]
        Xn = wrenlab.normalize.quantile(X)

        dvars = ":".join("C({})".format(c) for c in D.columns)
        formula = "Expression ~ C(Gene) + {} + Signature:{}".format(dvars, dvars)
        n_coef = groups.shape[0]

        o, ix = [], []

        for dcat, df in Am.groupby("Term ID"):
            s = np.array(df["Score"])
            if len(set(s)) < 2:
                continue
            n = df.shape[0]
            design = pd.concat([D]*n)
            design["Signature"] = np.tile(s, (D.shape[0],1)).T.flatten()
            design["Signature"] -= design["Signature"].mean()
            design["Gene"] = np.tile(df["Element ID"], (D.shape[0],1)).T.flatten()
            design["Expression"] = np.array(Xn.loc[df["Element ID"],:]).flatten()
            
            y, x = patsy.dmatrices(formula, design)
            model = sm.OLS(y, x)
            fit = model.fit()
            coef = fit.params
            stderr = fit.bse

            for g, coef, stderr in zip(groups.index, coef[-n_coef:], stderr[-n_coef:]):
                ix.append((dcat, g))
                o.append((n, coef, stderr))
        ix = pd.MultiIndex.from_tuples(ix, names=["Term ID", "Group"])
        o = pd.DataFrame.from_records(o, index=ix, columns=["N", "coef", "stderr"])
        return SignatureAnalysis(o)

    @staticmethod
    def get(key, taxon_id):
        return annotation(key, taxon_id)

def annotation(key, taxon_id):
    fn = _AVAILABLE[key]
    return fn(taxon_id)
