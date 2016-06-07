from collections import namedtuple
import os.path
import urllib.request
import shelve

import yaml
import pandas as pd
import numpy as np

from wrenlab.util.remote_table import remote_table
from wrenlab.util import memoize, download, KVStore

def gene_taxon():
    if not KVStore.exists("gene_taxon"):
        LOG.debug("Initializing KVStore for gene_taxon ...")
        tbl = remote_table("NCBI.gene.info")
        store = KVStore("gene_taxon", writeback=True)
        for taxon_id, gene_id in tbl.index.values:
            store[int(gene_id)] = int(taxon_id)
        store.sync()
        store.close()
    return KVStore("gene_taxon")

@memoize
def info(taxon_id):
    assert isinstance(taxon_id, int)
    genes = remote_table("NCBI.gene.info")
    return genes.loc[taxon_id,:]

@memoize
def _synonyms():
    tbl = remote_table("NCBI.gene.synonym")
    o = []
    for (taxon_id, gene_id, synonyms, designations) in tbl.to_records(index=False):
        text = "|".join([field for field in [synonyms, designations] if
            (field is not None) and (field == field)])
        for synonym in text.split("|"):
            synonym = synonym.strip()
            if synonym:
                o.append((taxon_id, gene_id, synonym))
    o = pd.DataFrame.from_records(o, columns=["Taxon ID", "Gene ID", "Synonym"])
    return o.drop_duplicates()

@memoize
def synonyms(taxon_id):
    tbl = _synonyms()
    return tbl.ix[tbl["Taxon ID"] == taxon_id,:].drop("Taxon ID", axis=1)

@memoize
def accession(taxon_id):
    assert isinstance(taxon_id, int)
    return remote_table("NCBI.gene.accession")\
            .loc[taxon_id,:]\
            .dropna(how="all")

@memoize
def ensembl(taxon_id):
    assert isinstance(taxon_id, int)
    o = remote_table("NCBI.gene.ensembl")
    return o.ix[o["Taxon ID"] == taxon_id,:]\
            .drop("Taxon ID", axis=1)

Gene = namedtuple("Gene", "id,symbol,name,chromosome")

def by_id(gene_id):
    m = gene_taxon()
    taxon_id = m[gene_id]
    df = info(taxon_id)
    symbol = df.loc[gene_id, "Symbol"]
    name = df.loc[gene_id, "Name"]
    chromosome = df.loc[gene_id, "Chromosome"]
    return Gene(gene_id, symbol, name, chromosome)
