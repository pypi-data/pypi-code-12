import functools
import zipfile
import sqlite3
import contextlib

import pandas as pd

import wrenlab.ncbi.gene
import wrenlab.util

from wrenlab.data.drugbank import DrugBank

def AILUN(platform_id):
    url = "ftp://phoenix.omrf.hsc.net.ou.edu/AILUN.db"
    path = str(wrenlab.util.download(url))
    with contextlib.closing(sqlite3.connect(path)) as db:
        c = db.cursor()
        c.execute("SELECT probe_id, gene_id FROM probe_gene WHERE platform_id=?", 
                (platform_id,))
        return dict(c)

def connectivity_map_design():
    url = "https://www.broadinstitute.org/cmap/cmap_instances_02.xls"
    path = str(wrenlab.util.download(url))
    D = pd.read_excel(path)\
            .loc[:,["instance_id","batch_id","cmap_name",
                "concentration (M)", "duration (h)", "cell2", "vehicle"]]
    D.columns = ["SampleID", "BatchID", "Drug", "Concentration", 
            "Duration", "CellType", "Vehicle"]
    D = D.set_index(["SampleID"])
    D = D.ix[[isinstance(ix, int) for ix in D.index],:]
    D.index = D.index.astype(int)
    for c in D.columns:
        if c not in ("Concentration", "Duration"):
            D[c] = D[c].astype("category")
    return D

@functools.lru_cache()
def connectivity_map():
    # the data values are ranks 1 ... N
    # with rank 1 being highest treatment / control ratio and rank N being lowest
    url = "ftp://ftp.broad.mit.edu/pub/cmap/rankMatrix.txt.zip"
    path = str(wrenlab.util.download(url))
    with zipfile.ZipFile(path) as zf:
        with zf.open("rankMatrix.txt", "r") as h:
            X = pd.read_csv(h, sep="\t")\
                    .set_index(["probe_id"])\
                    .iloc[:,:-1]
            X.columns = list(map(int, X.columns))
            probe_gene = {k:v for k,v in AILUN(570).items() if k in X.index}
            X = X.loc[list(probe_gene.keys()),:]
            rows = []
            for gene_id, df in X.groupby(probe_gene):
                v = df.mean()
                v.name = gene_id
                rows.append(v)
            Xc = pd.concat(rows, axis=1)
            D = connectivity_map_design()
            D, Xc = D.align(Xc, axis=0, join="inner")
            Xc = Xc.T
            Xc.index.name = "Entrez Gene ID"
            Xc.columns.name = "SampleID"
            Xc = Xc.apply(lambda x: wrenlab.util.ranks(-x))
            #return D, Xc
            Xc = Xc.groupby(D["Drug"].astype(str), axis=1)\
                    .mean()\
                    .apply(lambda x: wrenlab.util.ranks(-x))
            return Xc

if __name__ == "__main__":
    """
    X = connectivity_map()
    mu = X.mean().sort_index(ascending=False)
    print(mu.describe())
    print(mu.head().index)
    print(mu.tail().index)
    #print(X.head().T.head().T)
    """

    #print(AILUN(570))

    #D = connectivity_map_design()
    #print(D.tail())

    #pprint.pprint(db._items)
