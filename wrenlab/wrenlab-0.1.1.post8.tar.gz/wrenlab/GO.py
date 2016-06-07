import pandas as pd

from wrenlab.util import memoize
import wrenlab.ontology

@memoize
def concepts():
    o = wrenlab.ontology.fetch("GO")
    ts = o.terms
    ix = ts["Name"].str.match("^(?:positive|negative) regulation of",
            as_indexer=True)
    coef = pd.Series(0, index=ts.index)
    coef[ts["Name"].str.match("^positive regulation of")] = 1
    coef[ts["Name"].str.match("^negative regulation of")] = -1
    ts["Concept"] = ts["Name"].str.replace(\
        "^(?:(?:positive|negative) )?regulation of ", "")
    ts["Directionality"] = coef
    o = []
    for concept, df in ts.groupby("Concept"):
        try:
            pos = df.ix[df["Directionality"] == 1,:].index[0]
            neg = df.ix[df["Directionality"] == -1,:].index[0]
        except IndexError:
            continue
        o.append((concept, pos, 1))
        o.append((concept, neg, -1))
    return pd.DataFrame.from_records(o, columns=["Concept", "Term ID", "Direction"])
