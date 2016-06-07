import os.path
import sqlite3
import warnings

import numpy as np
import pandas as pd

import acfsa
import wrenlab.ontology
import wrenlab.ncbi.geo.metadb

from wrenlab.util import *

EXCLUDE_TISSUES = [ "ear", "hip", "sputum", "pith", "neck", "tail", "stem",
        "wing", "stoma", "serum", "node", "fin", "finger", "primary cell",
        "root", "adult", "arm", "blast cell", "primary cell" ] 

INCLUDED_TISSUES = [89, 149, 763, 142, 759, 269, 784, 141, 1253, 1101, 930,
        876, 232, 1487, 772, 452, 290, 414, 991, 887, 801, 1629, 123, 671, 2807, 1158, 562]

def excluded_tissues():
    BTO = wrenlab.ontology.fetch("BTO")
    return [int(x[4:]) for x in BTO.terms.index[BTO.terms.Name.isin(EXCLUDE_TISSUES)]]

@memoize
def disease_state():
    """
    """
    # FIXME: use concat title + ch instead of just ch
    PATTERNS = {
            "Cancer": "(cancer|carcinoma|neoplas|leukemia)"
    }
    mdb = wrenlab.ncbi.geo.metadb.connect()
    df = mdb.samples
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ix = df.Characteristics.dropna().str.contains(PATTERNS["Cancer"]).astype(float)
    o = pd.DataFrame.from_dict({"Cancer": ix})
    return o.dropna()

@memoize
def tissue():
    """
    """
    mdb = wrenlab.ncbi.geo.metadb.connect()
        
    BTO = wrenlab.ontology.fetch("BTO")
    ix = BTO.synonyms["Term ID"]\
            .isin(["BTO:{:07d}".format(ix) for ix in INCLUDED_TISSUES])
    synonyms = BTO.synonyms.ix[ix,:]

    trie = acfsa.Trie(
            case_sensitive=False, 
            allow_overlaps=False, 
            boundary_characters=" \n.:?")
    for term_id, s in synonyms.to_records(index=False):
        trie.add(s, key=int(term_id[4:]))
    trie.build()

    records = mdb.samples.loc[:,["Title", "Characteristics"]].to_records()

    o = []
    for sample_id, channel, title, ch in records:
        text = "\n".join(filter(None, [title,ch])).strip()
        if len(text) == 0:
            continue
        ms = trie.search(text)
        if len(ms) != 1:
            continue
        o.append((sample_id, channel, ms[0].key))
    o = pd.DataFrame.from_records(o, 
            columns=["SampleID", "Channel", "TissueID"])\
                    .set_index(["SampleID", "Channel"])
    o.TissueID = o.TissueID.astype("category")
    return o

@memoize
def map_experiments_to_samples(method="largest", min_size=10):
    assert method in ("largest", "smallest")
    assert isinstance(min_size, int)

    mdb = wrenlab.ncbi.geo.metadb.connect()
    j = mdb.experiment_sample
    counts = j.ExperimentID.value_counts()
    counts = counts.ix[counts >= min_size]
    counts = dict(zip(counts.index, counts))
    j["Count"] = [counts.get(ix) for ix in j.ExperimentID]
    def fn(df):
        return df.sort_values("Count", ascending=(method=="smallest")).ExperimentID.iloc[0]
    return j.dropna().groupby("SampleID").apply(fn)

def get_labels_new():
    E = map_experiments_to_samples()
    E = dict(zip(E.index, E))

    T = tissue()
    D = disease_state()
    columns = ["PlatformID", "ExperimentID", "TaxonID", "TissueID"] + list(D.columns)

    mdb = wrenlab.ncbi.geo.metadb.connect()
    o = pd.concat([mdb.samples, T, D], axis=1)
    o["ExperimentID"] = [E.get(id) for id in o.index.get_level_values(0)]
    o = o.loc[:,columns]
    o = o\
            .dropna(how="any", subset=o.columns[:4])\
            .dropna(how="all", subset=o.columns[4:])
    for c in ["ExperimentID", "TissueID"]:
        o[c] = [int(x) if not np.isnan(x) else None for x in o[c]]
        o[c] = o[c].astype("category")
    return o

@memoize
def get_labels():
    BTO = wrenlab.ontology.fetch("BTO")

    path = os.path.join(os.path.dirname(__file__), "labels.tsv")
    A = pd.read_csv(path, sep="\t")\
            .query("channel == 1")\
            .set_index(["sample_id"])
    A = A.query("channel == 1").copy()
    A.index = ["GSM{}".format(id) for id in A.index]
    A.index.name = "SampleID"
    A["TissueID"] = [int(x[4:]) if isinstance(x, str) else None for x in A["tissue_id"]]

    PBMC = ["peripheral blood mononuclear cell", "peripheral blood"]
    for ix in BTO.terms.index[BTO.terms["Name"].isin(PBMC)]:
        ix = int(ix[4:])
        A.ix[A["TissueID"] == ix, "TissueID"] = 89
    tissue_name_id = {name:int(id[4:]) for id,name in zip(BTO.terms.index, BTO.terms["Name"])}
    for tissue_name in EXCLUDE_TISSUES:
        tissue_id = tissue_name_id[tissue_name]
        A.ix[A["TissueID"] == tissue_id, "TissueID"] = None

    A = A.loc[:,["age","gender","TissueID"]]
    A.columns = ["Age", "Gender", "TissueID"]

    gconv = {"F":0.0,"M":1.0}
    A["Gender"] = [gconv.get(g, np.nan) for g in A["Gender"]]
    A["Gender"] = A["Gender"].astype(float)

    A["Age"] /= 12

    db = sqlite3.connect("/data/ncbi/geo/GEOmetadb.sqlite")
    # FIXME: order by biggest experiments
    gsm_gse = {k:int(v[3:]) for k,v in \
            pd.read_sql("select gsm,gse from gse_gsm;", db).to_records(index=False)}
    gsm_gpl = {k:int(v[3:]) for k,v in \
            pd.read_sql("select gsm,gpl from gsm;", db).to_records(index=False)}
    A["TaxonID"] = 9606 # FIXME
    A["ExperimentID"] = [gsm_gse.get(ix) for ix in A.index]
    A["PlatformID"] = [gsm_gpl.get(ix) for ix in A.index]
    A["Age"] = A["Age"].astype(float)

    A = A.dropna(subset=["TissueID", "ExperimentID", "PlatformID"])
    for k in ["TissueID", "ExperimentID", "PlatformID"]:
        A[k] = A[k].astype(int).astype("category")

    A.index = [int(x[3:]) for x in A.index]
    A.index.name = "SampleID"
    return A
